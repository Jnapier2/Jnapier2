#!/usr/bin/env python3
"""Read-only portfolio and GitHub metadata audit.

The audit validates the recruiter-facing profile, the declared public repository
set, repository metadata and required files, canonical links, live-site
reachability, and manual UI controls such as pinned repository order.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / ".github" / "portfolio-manifest.json"
PROFILE_README_PATH = ROOT / "README.md"
OUTPUT_DIR = ROOT / "audit-output"
HTTP_TIMEOUT_SECONDS = 15
HTTP_ATTEMPTS = 3
MAX_TEXT_BYTES = 2_000_000
USER_AGENT = "Gateway-Portfolio-Audit/1.0"


@dataclass
class Finding:
    severity: str
    area: str
    message: str


@dataclass
class RepoAuditResult:
    name: str
    findings: list[Finding] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class Audit:
    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.repository_rows: list[dict[str, str]] = []

    def add(self, severity: str, area: str, message: str) -> None:
        self.findings.append(Finding(severity, area, message))

    @property
    def errors(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "error"]

    @property
    def warnings(self) -> list[Finding]:
        return [item for item in self.findings if item.severity == "warning"]


def _headers(*, json_request: bool = False) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    if json_request:
        headers["Content-Type"] = "application/json"
    return headers


def request_bytes(
    url: str,
    *,
    method: str = "GET",
    payload: bytes | None = None,
    accept_json: bool = False,
) -> tuple[int, str, bytes]:
    last_error: Exception | None = None
    for attempt in range(1, HTTP_ATTEMPTS + 1):
        request = urllib.request.Request(
            url,
            data=payload,
            method=method,
            headers=_headers(json_request=accept_json),
        )
        try:
            with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                data = response.read(MAX_TEXT_BYTES + 1)
                if len(data) > MAX_TEXT_BYTES:
                    raise ValueError(f"response exceeded {MAX_TEXT_BYTES} bytes")
                return int(response.status), response.geturl(), data
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as exc:
            last_error = exc
            if attempt < HTTP_ATTEMPTS:
                time.sleep(0.75 * attempt)
    raise RuntimeError(f"{url}: {last_error}")


def request_text(url: str) -> tuple[int, str, str]:
    status, final_url, data = request_bytes(url)
    return status, final_url, data.decode("utf-8", errors="replace")


def request_json(
    url: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
) -> Any:
    payload = None
    if body is not None:
        payload = json.dumps(body, separators=(",", ":")).encode("utf-8")
    _, _, data = request_bytes(
        url,
        method=method,
        payload=payload,
        accept_json=True,
    )
    return json.loads(data.decode("utf-8"))


def raw_url(owner: str, repository: str, branch: str, path: str) -> str:
    quoted_path = "/".join(urllib.parse.quote(part, safe="") for part in path.split("/"))
    return (
        f"https://raw.githubusercontent.com/"
        f"{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(repository, safe='')}/"
        f"{urllib.parse.quote(branch, safe='')}/{quoted_path}"
    )


def load_manifest() -> dict[str, Any]:
    try:
        data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Portfolio manifest is unreadable: {exc}") from exc
    required = {
        "schema_version",
        "owner",
        "profile_repository",
        "canonical_portfolio_url",
        "canonical_linkedin_url",
        "rights_notice",
        "expected_public_repositories",
        "flagship_repositories",
        "expected_pins",
        "forbidden_public_link_fragments",
        "repositories",
    }
    missing = sorted(required - set(data))
    if missing:
        raise SystemExit(f"Portfolio manifest is missing fields: {missing}")
    if data["schema_version"] != 1:
        raise SystemExit("Unsupported portfolio manifest schema")
    return data


def audit_profile_readme(audit: Audit, manifest: dict[str, Any]) -> None:
    try:
        readme = PROFILE_README_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        audit.add("error", "profile", f"README.md is unreadable: {exc}")
        return

    required_text = [
        "# Jerry R. Napier",
        "Information management · Data governance · Analytics · Reliable automation",
        "I turn complex systems into trusted ones.",
        "M.S. in Information Management",
        manifest["canonical_portfolio_url"],
        manifest["canonical_linkedin_url"],
        "## Start here",
        "## Additional portfolio evidence",
        "Additional tools and learning releases",
        "## Working principles",
    ]
    for value in required_text:
        if value not in readme:
            audit.add("error", "profile", f"Missing required profile content: {value}")

    for repository in manifest["repositories"]:
        url = f"https://github.com/{manifest['owner']}/{repository['name']}"
        count = readme.count(url)
        if count != 1:
            audit.add(
                "error",
                "profile",
                f"Expected exactly one link for {repository['name']}; found {count}",
            )

    flagship_markers = [
        "[BotOps Manager]",
        "[Digital Asset Governance Audit]",
        "[MediaTaggerBot]",
    ]
    try:
        positions = [readme.index(marker) for marker in flagship_markers]
    except ValueError as exc:
        audit.add("error", "profile", f"Flagship marker is missing: {exc}")
    else:
        if positions != sorted(positions):
            audit.add("error", "profile", "Flagship project order has drifted")

    lower_readme = readme.lower()
    for fragment in manifest["forbidden_public_link_fragments"]:
        if fragment.lower() in lower_readme:
            audit.add("error", "profile", f"Forbidden public link found: {fragment}")

    repository_links = re.findall(
        rf"https://github\.com/{re.escape(manifest['owner'])}/[A-Za-z0-9._-]+",
        readme,
    )
    duplicates = sorted(
        {link for link in repository_links if repository_links.count(link) > 1}
    )
    if duplicates:
        audit.add("error", "profile", f"Duplicate repository links found: {duplicates}")

    if readme.count("## Start here") != 1:
        audit.add("error", "profile", "Start-here section must appear exactly once")
    if readme.count("<details>") != 1 or readme.count("</details>") != 1:
        audit.add("error", "profile", "Supporting-work disclosure markup is unbalanced")


def audit_public_inventory(audit: Audit, manifest: dict[str, Any]) -> None:
    owner = manifest["owner"]
    url = (
        f"https://api.github.com/users/{urllib.parse.quote(owner, safe='')}/repos"
        "?per_page=100&type=owner&sort=full_name"
    )
    try:
        records = request_json(url)
    except Exception as exc:
        audit.add("error", "inventory", f"Unable to read public repository inventory: {exc}")
        return

    actual = sorted(
        record["name"]
        for record in records
        if not record.get("private", False) and not record.get("fork", False)
    )
    expected = sorted(manifest["expected_public_repositories"])
    missing = sorted(set(expected) - set(actual))
    unexpected = sorted(set(actual) - set(expected))
    if missing:
        audit.add("error", "inventory", f"Expected public repositories are missing: {missing}")
    if unexpected:
        audit.add(
            "error",
            "inventory",
            f"Unreviewed public repositories are outside the manifest: {unexpected}",
        )


def _fetch_required_file(owner: str, name: str, branch: str, path: str) -> tuple[bool, str]:
    try:
        status, _, text = request_text(raw_url(owner, name, branch, path))
    except Exception:
        return False, ""
    return status == 200, text


def audit_repository(
    owner: str,
    specification: dict[str, Any],
    manifest: dict[str, Any],
) -> RepoAuditResult:
    name = specification["name"]
    result = RepoAuditResult(name=name)

    def finding(severity: str, message: str) -> None:
        result.findings.append(Finding(severity, name, message))

    metadata_url = (
        f"https://api.github.com/repos/{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(name, safe='')}"
    )
    try:
        metadata = request_json(metadata_url)
    except Exception as exc:
        finding("error", f"Repository metadata could not be read: {exc}")
        return result

    result.metadata = metadata
    if metadata.get("private"):
        finding("error", "Portfolio repository is not public")
    if metadata.get("archived"):
        finding("error", "Portfolio repository is archived")
    if metadata.get("fork"):
        finding("error", "Portfolio repository unexpectedly became a fork")

    branch = metadata.get("default_branch") or ""
    if branch != "main":
        finding("error", f"Default branch is {branch!r}, expected 'main'")

    if not (metadata.get("description") or "").strip():
        finding("warning", "Repository description is empty")
    if not metadata.get("topics"):
        finding("warning", "Repository topics are empty")

    homepage = (metadata.get("homepage") or "").strip()
    expected_homepage = specification.get("expected_homepage")
    if expected_homepage and homepage.rstrip("/") != expected_homepage.rstrip("/"):
        finding(
            "warning",
            f"About website is {homepage or '(empty)'}; expected {expected_homepage}",
        )
    lower_homepage = homepage.lower()
    for fragment in manifest["forbidden_public_link_fragments"]:
        if fragment.lower() in lower_homepage:
            finding("warning", f"About website still contains retired link: {homepage}")

    required_paths = [
        "README.md",
        "LICENSE.md",
        "SECURITY.md",
        specification["ci_path"],
    ]
    file_text: dict[str, str] = {}
    for path in required_paths:
        exists, text = _fetch_required_file(owner, name, branch, path)
        if not exists:
            finding("error", f"Required file is missing or unreadable: {path}")
        else:
            file_text[path] = text

    readme = file_text.get("README.md", "")
    license_text = file_text.get("LICENSE.md", "")
    workflow = file_text.get(specification["ci_path"], "")
    lower_readme = readme.lower()

    for fragment in manifest["forbidden_public_link_fragments"]:
        if fragment.lower() in lower_readme:
            finding("error", f"README contains forbidden public link: {fragment}")

    if specification.get("require_portfolio_backlink"):
        if manifest["canonical_portfolio_url"] not in readme:
            finding("error", "README is missing the canonical portfolio backlink")

    combined_rights = f"{readme}\n{license_text}"
    if specification["rights_mode"] == "all-rights-reserved":
        if manifest["rights_notice"] not in combined_rights:
            finding("error", "Canonical Gateway rights notice is missing")
    elif specification["rights_mode"] == "mit-sealed":
        if "Gateway Information Group LLC" not in combined_rights:
            finding("error", "Gateway rights holder is missing from the sealed MIT release")
        if "MIT License" not in combined_rights:
            finding("error", "MIT license declaration is missing from the sealed release")
    else:
        finding("error", f"Unknown rights mode: {specification['rights_mode']}")

    if workflow:
        if not re.search(r"(?m)^permissions:\s*\n\s+contents:\s*read\s*$", workflow):
            finding("warning", "CI does not visibly declare read-only contents permission")
        if "timeout-minutes:" not in workflow:
            finding("warning", "CI has no visible job timeout")
        if "persist-credentials: false" not in workflow:
            finding("warning", "CI checkout does not visibly disable persisted credentials")
        if "concurrency:" not in workflow:
            finding("warning", "CI has no visible superseded-run concurrency control")

    return result


def audit_repositories(audit: Audit, manifest: dict[str, Any]) -> None:
    owner = manifest["owner"]
    specifications = manifest["repositories"]
    results: list[RepoAuditResult] = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(audit_repository, owner, specification, manifest): specification["name"]
            for specification in specifications
        }
        for future in as_completed(futures):
            name = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                audit.add("error", name, f"Unexpected repository-audit failure: {exc}")

    for result in sorted(results, key=lambda item: item.name.lower()):
        audit.findings.extend(result.findings)
        metadata = result.metadata
        audit.repository_rows.append(
            {
                "repository": result.name,
                "status": (
                    "ERROR"
                    if any(item.severity == "error" for item in result.findings)
                    else "WARN"
                    if any(item.severity == "warning" for item in result.findings)
                    else "PASS"
                ),
                "description": "set" if (metadata.get("description") or "").strip() else "missing",
                "topics": str(len(metadata.get("topics") or [])),
                "homepage": (metadata.get("homepage") or "").strip() or "—",
            }
        )


def audit_portfolio_site(audit: Audit, manifest: dict[str, Any]) -> None:
    url = manifest["canonical_portfolio_url"]
    try:
        status, final_url, html = request_text(url)
    except Exception as exc:
        audit.add("warning", "portfolio-site", f"Live portfolio check failed: {exc}")
        return

    if status != 200:
        audit.add("warning", "portfolio-site", f"Live portfolio returned HTTP {status}")
    if urllib.parse.urlparse(final_url).scheme != "https":
        audit.add("warning", "portfolio-site", f"Portfolio did not finish on HTTPS: {final_url}")

    lower_html = html.lower()
    if "i turn complex systems into trusted ones" not in lower_html:
        audit.add(
            "warning",
            "portfolio-site",
            "Live HTML did not expose the expected recruiter-facing value statement",
        )
    for fragment in manifest["forbidden_public_link_fragments"]:
        if fragment.lower() in lower_html:
            audit.add("warning", "portfolio-site", f"Retired public link appears in site HTML: {fragment}")
    for fragment in manifest.get("portfolio_privacy_review_fragments", []):
        if fragment.lower() in lower_html:
            audit.add(
                "warning",
                "portfolio-site",
                f"Manual privacy review remains required for site content: {fragment}",
            )


def audit_public_profile_render(audit: Audit, manifest: dict[str, Any]) -> None:
    url = f"https://github.com/{manifest['owner']}"
    try:
        status, _, html = request_text(url)
    except Exception as exc:
        audit.add("warning", "profile-render", f"Signed-out profile render could not be checked: {exc}")
        return
    if status != 200:
        audit.add("warning", "profile-render", f"Signed-out profile returned HTTP {status}")
        return

    lower_html = html.lower()
    if "i turn complex systems into trusted ones" not in lower_html:
        audit.add(
            "warning",
            "profile-render",
            "Signed-out profile HTML did not expose the current value statement; verify caching manually",
        )
    for fragment in manifest["forbidden_public_link_fragments"]:
        if fragment.lower() in lower_html:
            audit.add(
                "warning",
                "profile-render",
                f"Signed-out profile still exposes a retired link: {fragment}",
            )


def audit_pins(audit: Audit, manifest: dict[str, Any]) -> None:
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        audit.add("warning", "pins", "GITHUB_TOKEN is unavailable; pinned repositories were not checked")
        return

    query = """
    query($login: String!) {
      user(login: $login) {
        pinnedItems(first: 6, types: [REPOSITORY]) {
          nodes {
            ... on Repository { name }
          }
        }
      }
    }
    """
    try:
        payload = request_json(
            "https://api.github.com/graphql",
            method="POST",
            body={"query": query, "variables": {"login": manifest["owner"]}},
        )
        if payload.get("errors"):
            raise RuntimeError(payload["errors"])
        actual = [
            node["name"]
            for node in payload["data"]["user"]["pinnedItems"]["nodes"]
            if node and node.get("name")
        ]
    except Exception as exc:
        audit.add("warning", "pins", f"Pinned repositories could not be checked: {exc}")
        return

    expected = manifest["expected_pins"]
    if actual != expected:
        audit.add(
            "warning",
            "pins",
            f"Pinned order needs manual correction. Actual: {actual}; expected: {expected}",
        )


def write_reports(audit: Audit, manifest: dict[str, Any]) -> None:
    lines = [
        "# Portfolio health audit",
        "",
        f"- Critical findings: **{len(audit.errors)}**",
        f"- Manual-review warnings: **{len(audit.warnings)}**",
        f"- Repositories checked: **{len(audit.repository_rows)}**",
        "",
        "## Repository status",
        "",
        "| Repository | Result | Description | Topics | About website |",
        "|---|---|---|---:|---|",
    ]
    for row in audit.repository_rows:
        homepage = row["homepage"].replace("|", "%7C")
        lines.append(
            f"| `{row['repository']}` | {row['status']} | {row['description']} | "
            f"{row['topics']} | {homepage} |"
        )

    if audit.errors:
        lines.extend(["", "## Critical findings", ""])
        lines.extend(
            f"- **{item.area}:** {item.message}"
            for item in sorted(audit.errors, key=lambda item: (item.area, item.message))
        )
    if audit.warnings:
        lines.extend(["", "## Manual-review warnings", ""])
        lines.extend(
            f"- **{item.area}:** {item.message}"
            for item in sorted(audit.warnings, key=lambda item: (item.area, item.message))
        )

    lines.extend(
        [
            "",
            "This workflow is report-only and does not change repository settings, pins, deployments, or external permissions.",
            "",
            manifest["rights_notice"],
        ]
    )
    summary = "\n".join(lines) + "\n"

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "portfolio-audit.md").write_text(summary, encoding="utf-8")
    machine_report = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "owner": manifest["owner"],
        "canonical_portfolio_url": manifest["canonical_portfolio_url"],
        "rights_notice": manifest["rights_notice"],
        "critical_findings": len(audit.errors),
        "manual_review_warnings": len(audit.warnings),
        "repositories_checked": len(audit.repository_rows),
        "repositories": audit.repository_rows,
        "findings": [
            {
                "severity": item.severity,
                "area": item.area,
                "message": item.message,
            }
            for item in sorted(
                audit.findings,
                key=lambda item: (item.severity, item.area, item.message),
            )
        ],
    }
    (OUTPUT_DIR / "portfolio-audit.json").write_text(
        json.dumps(machine_report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(summary)
    step_summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if step_summary:
        try:
            Path(step_summary).write_text(summary, encoding="utf-8")
        except OSError as exc:
            print(f"Unable to write GITHUB_STEP_SUMMARY: {exc}", file=sys.stderr)


def main() -> int:
    manifest = load_manifest()
    audit = Audit()
    audit_profile_readme(audit, manifest)
    audit_public_inventory(audit, manifest)
    audit_repositories(audit, manifest)
    audit_portfolio_site(audit, manifest)
    audit_public_profile_render(audit, manifest)
    audit_pins(audit, manifest)
    write_reports(audit, manifest)
    return 1 if audit.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
