#!/usr/bin/env python3
"""Rendered-text and low-request adapter for the read-only portfolio audit.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import re
import time
import urllib.parse
from html.parser import HTMLParser
from typing import Any

import portfolio_audit as core

API_COOLDOWN_SECONDS = 30
_REPOSITORY_METADATA: dict[str, dict[str, Any]] = {}


class PageTextParser(HTMLParser):
    """Extract visible text and links without executing page content."""

    _IGNORED = {"script", "style", "noscript", "template"}

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self._ignored_depth = 0
        self.text_parts: list[str] = []
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        lower_tag = tag.lower()
        if lower_tag in self._IGNORED:
            self._ignored_depth += 1
            return
        if self._ignored_depth:
            return
        for name, value in attrs:
            if name.lower() == "href" and value:
                self.hrefs.append(value)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() in self._IGNORED and self._ignored_depth:
            self._ignored_depth -= 1

    def handle_data(self, data: str) -> None:
        if not self._ignored_depth and data.strip():
            self.text_parts.append(data)


def parse_page(document: str, base_url: str) -> tuple[str, set[str]]:
    parser = PageTextParser()
    parser.feed(document)
    parser.close()
    visible_text = re.sub(r"\s+", " ", " ".join(parser.text_parts)).strip().lower()
    links = {
        urllib.parse.urljoin(base_url, href).strip().lower()
        for href in parser.hrefs
        if href.strip()
    }
    return visible_text, links


def audit_profile_readme(audit: core.Audit, manifest: dict[str, object]) -> None:
    try:
        readme = core.PROFILE_README_PATH.read_text(encoding="utf-8")
    except OSError as exc:
        audit.add("error", "profile", f"README.md is unreadable: {exc}")
        return

    required_text = [
        "# Jerry R. Napier",
        "Information management · Data governance · Analytics · Reliable automation",
        "I turn complex systems into trusted ones.",
        "M.S. in Information Management",
        str(manifest["canonical_portfolio_url"]),
        str(manifest["canonical_linkedin_url"]),
        "## Start here",
        "## More projects",
        "Additional tools and learning releases",
        "## Working principles",
    ]
    for value in required_text:
        if value not in readme:
            audit.add("error", "profile", f"Missing required profile content: {value}")

    for repository in manifest["repositories"]:
        name = str(repository["name"])
        url = f"https://github.com/{manifest['owner']}/{name}"
        count = readme.count(url)
        if count != 1:
            audit.add(
                "error",
                "profile",
                f"Expected exactly one link for {name}; found {count}",
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
        if str(fragment).lower() in lower_readme:
            audit.add("error", "profile", f"Forbidden public link found: {fragment}")

    repository_links = re.findall(
        rf"https://github\.com/{re.escape(str(manifest['owner']))}/[A-Za-z0-9._-]+",
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


def audit_public_inventory(audit: core.Audit, manifest: dict[str, Any]) -> None:
    owner = str(manifest["owner"])
    url = (
        f"https://api.github.com/users/{urllib.parse.quote(owner, safe='')}/repos"
        "?per_page=100&type=owner&sort=full_name"
    )
    try:
        records = core.request_json(url)
    except Exception as exc:
        audit.add("error", "inventory", f"Unable to read public repository inventory: {exc}")
        return
    if not isinstance(records, list):
        audit.add("error", "inventory", "Public repository inventory was not a list")
        return

    _REPOSITORY_METADATA.clear()
    for record in records:
        if isinstance(record, dict) and record.get("name"):
            _REPOSITORY_METADATA[str(record["name"])] = record

    actual = sorted(
        str(record["name"])
        for record in records
        if isinstance(record, dict)
        and record.get("name")
        and not record.get("private", False)
        and not record.get("fork", False)
    )
    expected = sorted(str(value) for value in manifest["expected_public_repositories"])
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


def audit_repository_from_inventory(
    owner: str,
    specification: dict[str, Any],
    manifest: dict[str, Any],
) -> core.RepoAuditResult:
    name = str(specification["name"])
    result = core.RepoAuditResult(name=name)

    def finding(severity: str, message: str) -> None:
        result.findings.append(core.Finding(severity, name, message))

    metadata = _REPOSITORY_METADATA.get(name)
    if metadata is None:
        finding("error", "Repository metadata is missing from the account inventory response")
        return result

    result.metadata = metadata
    if metadata.get("private"):
        finding("error", "Portfolio repository is not public")
    if metadata.get("archived"):
        finding("error", "Portfolio repository is archived")
    if metadata.get("fork"):
        finding("error", "Portfolio repository unexpectedly became a fork")

    branch = str(metadata.get("default_branch") or "")
    if branch != "main":
        finding("error", f"Default branch is {branch!r}, expected 'main'")

    if not str(metadata.get("description") or "").strip():
        finding("warning", "Repository description is empty")
    if not metadata.get("topics"):
        finding("warning", "Repository topics are empty")

    homepage = str(metadata.get("homepage") or "").strip()
    expected_homepage = specification.get("expected_homepage")
    if expected_homepage and homepage.rstrip("/") != str(expected_homepage).rstrip("/"):
        finding(
            "warning",
            f"About website is {homepage or '(empty)'}; expected {expected_homepage}",
        )
    lower_homepage = homepage.lower()
    for fragment in manifest["forbidden_public_link_fragments"]:
        if str(fragment).lower() in lower_homepage:
            finding("warning", f"About website still contains retired link: {homepage}")

    required_paths = [
        "README.md",
        "LICENSE.md",
        "SECURITY.md",
        str(specification["ci_path"]),
    ]
    file_text: dict[str, str] = {}
    for path in required_paths:
        exists, text = core._fetch_required_file(owner, name, branch, path)
        if not exists:
            finding("error", f"Required file is missing or unreadable: {path}")
        else:
            file_text[path] = text

    readme = file_text.get("README.md", "")
    license_text = file_text.get("LICENSE.md", "")
    workflow = file_text.get(str(specification["ci_path"]), "")
    lower_readme = readme.lower()

    for fragment in manifest["forbidden_public_link_fragments"]:
        if str(fragment).lower() in lower_readme:
            finding("error", f"README contains forbidden public link: {fragment}")

    if specification.get("require_portfolio_backlink"):
        if str(manifest["canonical_portfolio_url"]) not in readme:
            finding("error", "README is missing the canonical portfolio backlink")

    combined_rights = f"{readme}\n{license_text}"
    if specification["rights_mode"] == "all-rights-reserved":
        if str(manifest["rights_notice"]) not in combined_rights:
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


def audit_repositories(audit: core.Audit, manifest: dict[str, Any]) -> None:
    owner = str(manifest["owner"])
    results = [
        audit_repository_from_inventory(owner, specification, manifest)
        for specification in manifest["repositories"]
    ]
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
                "description": "set" if str(metadata.get("description") or "").strip() else "missing",
                "topics": str(len(metadata.get("topics") or [])),
                "homepage": str(metadata.get("homepage") or "").strip() or "—",
            }
        )


def audit_portfolio_site(audit: core.Audit, manifest: dict[str, object]) -> None:
    url = str(manifest["canonical_portfolio_url"])
    try:
        status, final_url, document = core.request_text(url)
    except Exception as exc:
        audit.add("warning", "portfolio-site", f"Live portfolio check failed: {exc}")
        return

    if status != 200:
        audit.add("warning", "portfolio-site", f"Live portfolio returned HTTP {status}")
    if urllib.parse.urlparse(final_url).scheme != "https":
        audit.add("warning", "portfolio-site", f"Portfolio did not finish on HTTPS: {final_url}")

    visible_text, links = parse_page(document, final_url)
    lower_document = document.lower()
    if "i turn complex systems into trusted ones" not in visible_text:
        audit.add(
            "warning",
            "portfolio-site",
            "Rendered portfolio text did not expose the expected public value statement",
        )

    for value in manifest["forbidden_public_link_fragments"]:
        fragment = str(value).lower()
        if fragment in lower_document or any(fragment in link for link in links):
            audit.add("warning", "portfolio-site", f"Retired public link appears in site HTML: {value}")

    for value in manifest.get("portfolio_privacy_review_fragments", []):
        fragment = str(value).lower()
        present = fragment in visible_text or fragment in lower_document or any(
            fragment in link for link in links
        )
        if present:
            audit.add(
                "warning",
                "portfolio-site",
                f"Manual privacy review remains required for site content: {value}",
            )


def audit_public_profile_render(audit: core.Audit, manifest: dict[str, object]) -> None:
    url = f"https://github.com/{manifest['owner']}"
    try:
        status, final_url, document = core.request_text(url)
    except Exception as exc:
        audit.add("warning", "profile-render", f"Signed-out profile render could not be checked: {exc}")
        return
    if status != 200:
        audit.add("warning", "profile-render", f"Signed-out profile returned HTTP {status}")
        return

    visible_text, links = parse_page(document, final_url)
    lower_document = document.lower()
    if "i turn complex systems into trusted ones" not in visible_text:
        audit.add(
            "warning",
            "profile-render",
            "Signed-out profile text did not expose the current value statement; verify caching manually",
        )
    for value in manifest["forbidden_public_link_fragments"]:
        fragment = str(value).lower()
        if fragment in lower_document or any(fragment in link for link in links):
            audit.add(
                "warning",
                "profile-render",
                f"Signed-out profile still exposes a retired link: {value}",
            )


def main() -> int:
    original_attempts = core.HTTP_ATTEMPTS
    core.HTTP_ATTEMPTS = 6
    core.audit_profile_readme = audit_profile_readme
    core.audit_public_inventory = audit_public_inventory
    core.audit_repositories = audit_repositories
    core.audit_portfolio_site = audit_portfolio_site
    core.audit_public_profile_render = audit_public_profile_render
    try:
        print(
            f"Cooling down GitHub API requests for {API_COOLDOWN_SECONDS} seconds "
            "before the low-request portfolio scan."
        )
        time.sleep(API_COOLDOWN_SECONDS)
        return core.main()
    finally:
        core.HTTP_ATTEMPTS = original_attempts


if __name__ == "__main__":
    raise SystemExit(main())
