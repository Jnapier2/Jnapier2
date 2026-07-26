#!/usr/bin/env python3
"""Validate public project claims, README boundaries, and the speaking guide.

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
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CLAIMS_PATH = ROOT / ".github" / "public-claims.json"
MANIFEST_PATH = ROOT / ".github" / "portfolio-manifest.json"
GUIDE_PATH = ROOT / "PUBLIC_CLAIMS.md"
PROFILE_README_PATH = ROOT / "README.md"
OUTPUT_DIR = ROOT / "audit-output"
RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
USER_AGENT = "Gateway-Public-Claims-Audit/1.0"
HTTP_TIMEOUT_SECONDS = 20
HTTP_ATTEMPTS = 4
MAX_README_BYTES = 2_000_000
MAX_WORKERS = 4

REQUIRED_POLICY_KEYS = (
    "required_elements",
    "allowed_quantitative_claim_types",
    "private_aggregate_rule",
    "historical_record_rule",
    "configuration_limit_rule",
    "headline_rule",
)
REQUIRED_RECORD_STRINGS = (
    "repository",
    "display_name",
    "claim_class",
    "guide_heading",
    "core_claim",
    "talk_track",
)
REQUIRED_QUANTITATIVE_FIELDS = (
    "label",
    "claim_type",
    "presentation",
    "source",
    "definition",
    "why_it_matters",
    "limitation",
)
ALLOWED_PRESENTATIONS = {"headline", "project_context", "historical_record"}
FORBIDDEN_PROMOTIONAL_PHRASES = (
    "production-ready",
    "guaranteed profit",
    "guarantees profit",
    "zero risk",
    "fully tested on every machine",
)
PRIVATE_AGGREGATE_FRAGMENTS = (
    "38,171-file",
    "838 verified or already-current outcomes",
)


@dataclass(frozen=True)
class Finding:
    severity: str
    repository: str
    area: str
    message: str


def load_object(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return payload


def add(
    findings: list[Finding],
    severity: str,
    repository: str,
    area: str,
    message: str,
) -> None:
    findings.append(Finding(severity, repository, area, message))


def request_bytes(url: str, maximum_bytes: int) -> bytes:
    headers = {
        "Accept": "text/plain, application/vnd.github.raw+json;q=0.9, */*;q=0.1",
        "User-Agent": USER_AGENT,
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token and urllib.parse.urlparse(url).hostname == "api.github.com":
        headers["Authorization"] = f"Bearer {token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"

    last_error: Exception | None = None
    for attempt in range(1, HTTP_ATTEMPTS + 1):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                data = response.read(maximum_bytes + 1)
            if len(data) > maximum_bytes:
                raise ValueError(f"response exceeded {maximum_bytes} bytes")
            return data
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            UnicodeError,
            ValueError,
        ) as exc:
            last_error = exc
            if attempt < HTTP_ATTEMPTS:
                time.sleep(min(8.0, 1.25 * (2 ** (attempt - 1))))
    raise RuntimeError(f"{url}: {last_error}")


def fetch_readme(owner: str, repository: str) -> str:
    if repository == owner:
        return PROFILE_README_PATH.read_text(encoding="utf-8")
    raw_url = (
        "https://raw.githubusercontent.com/"
        f"{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(repository, safe='')}/main/README.md"
    )
    try:
        return request_bytes(raw_url, MAX_README_BYTES).decode("utf-8-sig")
    except Exception as raw_error:
        api_url = (
            "https://api.github.com/repos/"
            f"{urllib.parse.quote(owner, safe='')}/"
            f"{urllib.parse.quote(repository, safe='')}/contents/README.md?ref=main"
        )
        try:
            return request_bytes(api_url, MAX_README_BYTES).decode("utf-8-sig")
        except Exception as api_error:
            raise RuntimeError(
                f"raw fetch failed ({raw_error}); API fallback failed ({api_error})"
            ) from api_error


def validate_structure(
    claims: dict[str, Any],
    manifest: dict[str, Any],
    guide: str,
    findings: list[Finding],
) -> list[dict[str, Any]]:
    if claims.get("schema_version") != 1:
        add(findings, "error", "portfolio", "registry", "schema_version must be 1")
    if claims.get("rights_notice") != RIGHTS_NOTICE:
        add(findings, "error", "portfolio", "registry", "rights notice is missing or changed")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(claims.get("reviewed_on") or "")):
        add(findings, "error", "portfolio", "registry", "reviewed_on must use YYYY-MM-DD")

    owner = str(claims.get("owner") or "").strip()
    if not owner or owner != str(manifest.get("owner") or "").strip():
        add(findings, "error", "portfolio", "registry", "owner differs from portfolio manifest")

    policy = claims.get("policy")
    if not isinstance(policy, dict):
        add(findings, "error", "portfolio", "policy", "policy must be an object")
        policy = {}
    for key in REQUIRED_POLICY_KEYS:
        value = policy.get(key)
        if value is None or value == "" or value == []:
            add(findings, "error", "portfolio", "policy", f"{key} is missing or empty")

    allowed_claim_types = policy.get("allowed_quantitative_claim_types")
    if not isinstance(allowed_claim_types, list) or not all(
        isinstance(item, str) and item.strip() for item in allowed_claim_types
    ):
        add(
            findings,
            "error",
            "portfolio",
            "policy",
            "allowed_quantitative_claim_types must be non-empty strings",
        )
        allowed_claim_types = []

    records = claims.get("repositories")
    if not isinstance(records, list):
        add(findings, "error", "portfolio", "registry", "repositories must be a list")
        return []

    expected = {
        str(item)
        for item in manifest.get("expected_public_repositories", [])
        if str(item)
    }
    names = [
        str(record.get("repository") or "")
        for record in records
        if isinstance(record, dict)
    ]
    actual = {name for name in names if name}
    if len(records) != 18:
        add(findings, "error", "portfolio", "coverage", f"expected 18 records; found {len(records)}")
    if len(names) != len(set(names)) or "" in names:
        add(findings, "error", "portfolio", "coverage", "repository records are duplicated or unnamed")
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        add(findings, "error", "portfolio", "coverage", f"missing repositories: {missing}")
    if extra:
        add(findings, "error", "portfolio", "coverage", f"unexpected repositories: {extra}")

    for record in records:
        if not isinstance(record, dict):
            add(findings, "error", "portfolio", "record", "repository record is not an object")
            continue
        repository = str(record.get("repository") or "(missing)")
        for key in REQUIRED_RECORD_STRINGS:
            value = record.get(key)
            if not isinstance(value, str) or not value.strip():
                add(findings, "error", repository, "record", f"{key} is missing or empty")

        talk_track = str(record.get("talk_track") or "")
        if not 80 <= len(talk_track) <= 700:
            add(
                findings,
                "error",
                repository,
                "talk_track",
                f"talk track length {len(talk_track)} is outside 80-700 characters",
            )
        for phrase in FORBIDDEN_PROMOTIONAL_PHRASES:
            if phrase in f"{record.get('core_claim', '')}\n{talk_track}".lower():
                add(
                    findings,
                    "error",
                    repository,
                    "public_copy",
                    f"contains forbidden promotional phrase: {phrase}",
                )

        for list_key in (
            "evidence_sources",
            "limitations",
            "readme_required_markers",
            "readme_forbidden_markers",
        ):
            value = record.get(list_key)
            if not isinstance(value, list) or not all(
                isinstance(item, str) and item.strip() for item in value
            ):
                if list_key == "readme_forbidden_markers" and value == []:
                    continue
                add(
                    findings,
                    "error",
                    repository,
                    "record",
                    f"{list_key} must contain non-empty strings",
                )
        if not record.get("evidence_sources"):
            add(findings, "error", repository, "evidence", "at least one evidence source is required")
        if not record.get("limitations"):
            add(findings, "error", repository, "limitations", "at least one limitation is required")
        if not record.get("readme_required_markers"):
            add(
                findings,
                "error",
                repository,
                "README",
                "at least one required README marker is needed",
            )

        heading = str(record.get("guide_heading") or "")
        if guide.count(heading) != 1:
            add(
                findings,
                "error",
                repository,
                "guide",
                f"guide heading must appear exactly once; found {guide.count(heading)}",
            )
        if talk_track and guide.count(talk_track) != 1:
            add(
                findings,
                "error",
                repository,
                "guide",
                f"talk track must appear exactly once; found {guide.count(talk_track)}",
            )

        quantitative = record.get("quantitative_claims")
        if not isinstance(quantitative, list):
            add(
                findings,
                "error",
                repository,
                "quantitative_claims",
                "quantitative_claims must be a list",
            )
            continue
        labels: list[str] = []
        for index, item in enumerate(quantitative):
            area = f"quantitative_claims[{index}]"
            if not isinstance(item, dict):
                add(findings, "error", repository, area, "claim must be an object")
                continue
            for key in REQUIRED_QUANTITATIVE_FIELDS:
                value = item.get(key)
                if not isinstance(value, str) or not value.strip():
                    add(findings, "error", repository, area, f"{key} is missing or empty")
            label = str(item.get("label") or "")
            labels.append(label)
            claim_type = str(item.get("claim_type") or "")
            if claim_type not in allowed_claim_types:
                add(
                    findings,
                    "error",
                    repository,
                    area,
                    f"unsupported claim_type: {claim_type!r}",
                )
            presentation = str(item.get("presentation") or "")
            if presentation not in ALLOWED_PRESENTATIONS:
                add(
                    findings,
                    "error",
                    repository,
                    area,
                    f"unsupported presentation: {presentation!r}",
                )
            traceable = item.get("public_traceable")
            if not isinstance(traceable, bool):
                add(
                    findings,
                    "error",
                    repository,
                    area,
                    "public_traceable must be Boolean",
                )
            if presentation == "headline" and traceable is not True:
                add(
                    findings,
                    "error",
                    repository,
                    area,
                    "headline claims must be publicly traceable",
                )
        if len(labels) != len(set(labels)):
            add(
                findings,
                "error",
                repository,
                "quantitative_claims",
                "quantitative claim labels are duplicated",
            )

    private_workspaces = claims.get("private_workspaces")
    if not isinstance(private_workspaces, list) or len(private_workspaces) != 2:
        add(
            findings,
            "error",
            "portfolio",
            "private_workspaces",
            "exactly two private workspace boundaries are required",
        )
    else:
        private_names = {
            str(item.get("repository") or "")
            for item in private_workspaces
            if isinstance(item, dict)
        }
        if private_names != {"-illuminati-card-game", "illuminati-card-game"}:
            add(
                findings,
                "error",
                "portfolio",
                "private_workspaces",
                "private workspace identities are incomplete or changed",
            )
        for item in private_workspaces:
            if not isinstance(item, dict) or not str(item.get("public_claim_boundary") or "").strip():
                add(
                    findings,
                    "error",
                    "portfolio",
                    "private_workspaces",
                    "each private workspace needs a public claim boundary",
                )

    if guide.count(RIGHTS_NOTICE) != 1:
        add(
            findings,
            "error",
            "portfolio",
            "guide",
            "PUBLIC_CLAIMS.md must contain the canonical rights notice exactly once",
        )
    for fragment in PRIVATE_AGGREGATE_FRAGMENTS:
        if fragment.lower() in guide.lower():
            add(
                findings,
                "error",
                "media-tagger-bot",
                "guide",
                f"private aggregate returned to public guide: {fragment}",
            )
    return [record for record in records if isinstance(record, dict)]


def validate_readme(
    owner: str,
    record: dict[str, Any],
) -> tuple[str, list[Finding]]:
    repository = str(record.get("repository") or "")
    findings: list[Finding] = []
    try:
        text = fetch_readme(owner, repository)
    except Exception as exc:
        add(
            findings,
            "error",
            repository,
            "README",
            f"could not read main README: {type(exc).__name__}: {exc}",
        )
        return repository, findings

    for marker in record.get("readme_required_markers", []):
        if marker not in text:
            add(
                findings,
                "error",
                repository,
                "README",
                f"required evidence marker is missing: {marker}",
            )
    lower = text.lower()
    for marker in record.get("readme_forbidden_markers", []):
        if marker.lower() in lower:
            add(
                findings,
                "error",
                repository,
                "README",
                f"retired or unsupported claim is still present: {marker}",
            )
    return repository, findings


def write_reports(
    claims: dict[str, Any],
    records: list[dict[str, Any]],
    findings: list[Finding],
) -> int:
    findings.sort(
        key=lambda item: (
            item.severity != "error",
            item.repository.lower(),
            item.area,
            item.message,
        )
    )
    errors = [item for item in findings if item.severity == "error"]
    generated_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    quantitative_count = sum(
        len(record.get("quantitative_claims") or [])
        for record in records
        if isinstance(record, dict)
    )
    payload = {
        "schema_version": 1,
        "generated_utc": generated_utc,
        "reviewed_on": claims.get("reviewed_on"),
        "result": "PASS" if not errors else "FAIL",
        "repositories_checked": len(records),
        "quantitative_claims_checked": quantitative_count,
        "private_workspace_boundaries_checked": len(claims.get("private_workspaces") or []),
        "error_count": len(errors),
        "findings": [asdict(item) for item in findings],
        "rights_notice": RIGHTS_NOTICE,
    }
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "public-claims-audit.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# Public claims and speaking-guide audit",
        "",
        f"- Result: **{payload['result']}**",
        f"- Public repositories checked: **{payload['repositories_checked']}**",
        f"- Quantitative claims checked: **{payload['quantitative_claims_checked']}**",
        f"- Private workspace boundaries checked: **{payload['private_workspace_boundaries_checked']}**",
        f"- Errors: **{payload['error_count']}**",
        "",
    ]
    if errors:
        lines.extend(["## Action required", ""])
        lines.extend(
            f"- **{item.repository} / {item.area}:** {item.message}"
            for item in errors
        )
    else:
        lines.append(
            "Every public project has a source-backed claim, a plain-language talk track, "
            "an explicit limitation, and README evidence markers. Quantitative claims are "
            "classified so fixture results, configuration limits, historical records, "
            "content scope, and measured outcomes are not presented as interchangeable."
        )
    lines.extend(
        [
            "",
            RIGHTS_NOTICE,
            "",
            "This notice does not replace or infer a software license. "
            "Each linked repository and third-party component retains its own notices, "
            "licenses, and rights.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    (OUTPUT_DIR / "public-claims-audit.md").write_text(markdown, encoding="utf-8")
    print(markdown)
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if summary_path:
        try:
            with Path(summary_path).open("a", encoding="utf-8") as handle:
                handle.write(markdown)
        except OSError as exc:
            print(f"Unable to write GITHUB_STEP_SUMMARY: {exc}", file=sys.stderr)
    return 1 if errors else 0


def main() -> int:
    findings: list[Finding] = []
    try:
        claims = load_object(CLAIMS_PATH)
        manifest = load_object(MANIFEST_PATH)
        guide = GUIDE_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
        print(f"Public claims audit could not start: {exc}", file=sys.stderr)
        return 1

    records = validate_structure(claims, manifest, guide, findings)
    owner = str(claims.get("owner") or "")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(validate_readme, owner, record): str(record.get("repository") or "")
            for record in records
        }
        for future in as_completed(futures):
            repository = futures[future]
            try:
                _, result = future.result()
                findings.extend(result)
            except Exception as exc:
                add(
                    findings,
                    "error",
                    repository,
                    "README",
                    f"unexpected README-audit failure: {type(exc).__name__}: {exc}",
                )

    return write_reports(claims, records, findings)


if __name__ == "__main__":
    raise SystemExit(main())
