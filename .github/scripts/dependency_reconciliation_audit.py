#!/usr/bin/env python3
"""Validate portfolio-wide dependency and installation contracts.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
PORTFOLIO_MANIFEST_PATH = ROOT / ".github" / "portfolio-manifest.json"
DEPENDENCY_LEDGER_PATH = ROOT / ".github" / "dependency-reconciliation.json"
OUTPUT_DIR = ROOT / "audit-output"
RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
USER_AGENT = "Gateway-Dependency-Reconciliation-Audit/1.0"
HTTP_TIMEOUT_SECONDS = 20
HTTP_ATTEMPTS = 3
MAX_FILE_BYTES = 5_000_000
ALLOWED_STATUSES = {
    "no_third_party_runtime",
    "exact_pins",
    "hash_locked",
    "bounded_ranges",
    "sealed_audited_release",
}


@dataclass(frozen=True)
class Finding:
    severity: str
    repository: str
    path: str
    message: str


@dataclass
class ProjectResult:
    repository: str
    status: str
    files_checked: int = 0
    absent_paths_checked: int = 0
    findings: list[Finding] = field(default_factory=list)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return payload


def headers() -> dict[str, str]:
    result = {
        "Accept": "application/vnd.github.raw+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        result["Authorization"] = f"Bearer {token}"
    return result


def remote_url(owner: str, repository: str, path: str) -> str:
    quoted_path = "/".join(urllib.parse.quote(part, safe="") for part in path.split("/"))
    return (
        f"https://api.github.com/repos/{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(repository, safe='')}/contents/{quoted_path}?ref=main"
    )


def fetch_remote(owner: str, repository: str, path: str, *, allow_missing: bool) -> str | None:
    url = remote_url(owner, repository, path)
    last_error: Exception | None = None
    for attempt in range(1, HTTP_ATTEMPTS + 1):
        request = urllib.request.Request(url, headers=headers())
        try:
            with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                data = response.read(MAX_FILE_BYTES + 1)
            if len(data) > MAX_FILE_BYTES:
                raise ValueError(f"response exceeded {MAX_FILE_BYTES} bytes")
            return data.decode("utf-8-sig")
        except urllib.error.HTTPError as exc:
            if exc.code == 404 and allow_missing:
                return None
            last_error = exc
        except (urllib.error.URLError, TimeoutError, UnicodeError, ValueError) as exc:
            last_error = exc
        if attempt < HTTP_ATTEMPTS:
            time.sleep(0.75 * attempt)
    raise RuntimeError(f"unable to read {repository}/{path}: {last_error}")


def fetch_text(
    owner: str,
    profile_repository: str,
    repository: str,
    path: str,
    *,
    allow_missing: bool = False,
) -> str | None:
    if repository == profile_repository:
        candidate = ROOT / path
        if not candidate.is_file():
            if allow_missing:
                return None
            raise FileNotFoundError(f"missing local profile file: {path}")
        if candidate.stat().st_size > MAX_FILE_BYTES:
            raise ValueError(f"local profile file exceeds {MAX_FILE_BYTES} bytes: {path}")
        return candidate.read_text(encoding="utf-8-sig")
    return fetch_remote(owner, repository, path, allow_missing=allow_missing)


def nested_value(payload: Any, dotted_key: str) -> tuple[bool, Any]:
    current = payload
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return False, None
        current = current[part]
    return True, current


def add_finding(
    result: ProjectResult,
    severity: str,
    path: str,
    message: str,
) -> None:
    result.findings.append(Finding(severity, result.repository, path, message))


def audit_project(
    owner: str,
    profile_repository: str,
    record: dict[str, Any],
) -> ProjectResult:
    repository = str(record.get("repository") or "").strip()
    status = str(record.get("status") or "").strip()
    result = ProjectResult(repository=repository, status=status)

    if not repository:
        add_finding(result, "error", "", "repository name is missing")
        return result
    if status not in ALLOWED_STATUSES:
        add_finding(result, "error", "", f"unsupported dependency status: {status!r}")
    if not str(record.get("note") or "").strip():
        add_finding(result, "error", "", "dependency note is missing")

    text_checks = record.get("text_checks", [])
    if not isinstance(text_checks, list):
        add_finding(result, "error", "", "text_checks must be a list")
        text_checks = []
    for check in text_checks:
        if not isinstance(check, dict):
            add_finding(result, "error", "", "text check must be an object")
            continue
        path = str(check.get("path") or "").strip()
        if not path:
            add_finding(result, "error", "", "text check path is missing")
            continue
        try:
            text = fetch_text(owner, profile_repository, repository, path)
        except Exception as exc:
            add_finding(result, "error", path, str(exc))
            continue
        assert text is not None
        result.files_checked += 1

        contains = check.get("contains", [])
        absent = check.get("absent", [])
        if not isinstance(contains, list) or not all(isinstance(item, str) for item in contains):
            add_finding(result, "error", path, "contains markers must be strings")
            contains = []
        if not isinstance(absent, list) or not all(isinstance(item, str) for item in absent):
            add_finding(result, "error", path, "absent markers must be strings")
            absent = []
        for marker in contains:
            if marker not in text:
                add_finding(result, "error", path, f"required dependency marker is missing: {marker}")
        for marker in absent:
            if marker in text:
                add_finding(result, "error", path, f"forbidden dependency marker is present: {marker}")

    json_checks = record.get("json_checks", [])
    if not isinstance(json_checks, list):
        add_finding(result, "error", "", "json_checks must be a list")
        json_checks = []
    for check in json_checks:
        if not isinstance(check, dict):
            add_finding(result, "error", "", "JSON check must be an object")
            continue
        path = str(check.get("path") or "").strip()
        if not path:
            add_finding(result, "error", "", "JSON check path is missing")
            continue
        try:
            text = fetch_text(owner, profile_repository, repository, path)
            assert text is not None
            payload = json.loads(text)
        except Exception as exc:
            add_finding(result, "error", path, f"JSON dependency contract is unreadable: {exc}")
            continue
        result.files_checked += 1

        exact = check.get("exact", {})
        absent_keys = check.get("absent_keys", [])
        if not isinstance(exact, dict):
            add_finding(result, "error", path, "exact JSON assertions must be an object")
            exact = {}
        if not isinstance(absent_keys, list) or not all(isinstance(item, str) for item in absent_keys):
            add_finding(result, "error", path, "absent_keys must be strings")
            absent_keys = []
        for dotted_key, expected in exact.items():
            exists, actual = nested_value(payload, str(dotted_key))
            if not exists:
                add_finding(result, "error", path, f"required JSON key is missing: {dotted_key}")
            elif actual != expected:
                add_finding(
                    result,
                    "error",
                    path,
                    f"JSON value differs for {dotted_key}: expected {expected!r}, found {actual!r}",
                )
        for dotted_key in absent_keys:
            exists, _ = nested_value(payload, dotted_key)
            if exists:
                add_finding(result, "error", path, f"unexpected dependency key is present: {dotted_key}")

    absent_paths = record.get("absent_paths", [])
    if not isinstance(absent_paths, list) or not all(isinstance(item, str) for item in absent_paths):
        add_finding(result, "error", "", "absent_paths must be strings")
        absent_paths = []
    for path in absent_paths:
        try:
            value = fetch_text(
                owner,
                profile_repository,
                repository,
                path,
                allow_missing=True,
            )
        except Exception as exc:
            add_finding(result, "error", path, str(exc))
            continue
        result.absent_paths_checked += 1
        if value is not None:
            add_finding(result, "error", path, "unexpected dependency manifest is present")

    if not text_checks and not json_checks and not absent_paths:
        add_finding(result, "error", "", "project record has no dependency checks")
    return result


def write_reports(
    ledger: dict[str, Any],
    results: list[ProjectResult],
    structural_errors: list[str],
) -> tuple[int, int]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    findings = [item for result in results for item in result.findings]
    for message in structural_errors:
        findings.append(Finding("error", "dependency-ledger", "", message))
    findings.sort(
        key=lambda item: (
            item.severity != "error",
            item.repository.lower(),
            item.path,
            item.message,
        )
    )
    errors = [item for item in findings if item.severity == "error"]
    warnings = [item for item in findings if item.severity == "warning"]
    generated_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    payload = {
        "schema_version": 1,
        "generated_utc": generated_utc,
        "owner": ledger.get("owner"),
        "rights_notice": RIGHTS_NOTICE,
        "result": "PASS" if not errors else "FAIL",
        "projects_checked": len(results),
        "files_checked": sum(item.files_checked for item in results),
        "absent_paths_checked": sum(item.absent_paths_checked for item in results),
        "deferred_reviews": ledger.get("deferred_reviews", []),
        "private_workspaces": ledger.get("private_workspaces", []),
        "error_count": len(errors),
        "warning_count": len(warnings),
        "projects": [
            {
                "repository": item.repository,
                "status": item.status,
                "files_checked": item.files_checked,
                "absent_paths_checked": item.absent_paths_checked,
                "error_count": sum(1 for finding in item.findings if finding.severity == "error"),
                "warning_count": sum(1 for finding in item.findings if finding.severity == "warning"),
            }
            for item in results
        ],
        "findings": [asdict(item) for item in findings],
    }
    (OUTPUT_DIR / "dependency-reconciliation.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Dependency reconciliation",
        "",
        f"Generated: `{generated_utc}`",
        "",
        f"- Result: **{payload['result']}**",
        f"- Public repositories checked: **{len(results)}**",
        f"- Dependency evidence files checked: **{payload['files_checked']}**",
        f"- Forbidden/absent paths checked: **{payload['absent_paths_checked']}**",
        f"- Errors: **{len(errors)}**",
        f"- Deferred compatibility reviews: **{len(ledger.get('deferred_reviews', []))}**",
        "",
        "## Repository coverage",
        "",
        "| Repository | Contract | Files | Absent paths | Errors |",
        "|---|---|---:|---:|---:|",
    ]
    for item in results:
        error_count = sum(1 for finding in item.findings if finding.severity == "error")
        lines.append(
            f"| `{item.repository}` | `{item.status}` | {item.files_checked} | "
            f"{item.absent_paths_checked} | {error_count} |"
        )

    if findings:
        lines.extend(["", "## Findings", ""])
        for item in findings:
            location = f"/{item.path}" if item.path else ""
            lines.append(
                f"- **{item.severity.upper()}** `{item.repository}{location}` — {item.message}"
            )
    else:
        lines.extend(["", "## Findings", "", "No dependency-contract drift was found."])

    deferred = ledger.get("deferred_reviews", [])
    if deferred:
        lines.extend(["", "## Explicitly deferred", ""])
        for item in deferred:
            lines.append(
                f"- **{item.get('repository')}: {item.get('dependency')}** — "
                f"{item.get('current')} → {item.get('candidate')}. {item.get('reason')}"
            )

    lines.extend(
        [
            "",
            RIGHTS_NOTICE,
            "",
            "This notice does not replace or infer a software license. Third-party components retain their respective notices and licenses.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    (OUTPUT_DIR / "dependency-reconciliation.md").write_text(markdown, encoding="utf-8")
    print(markdown)

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if summary_path:
        try:
            with Path(summary_path).open("a", encoding="utf-8") as handle:
                handle.write(markdown)
        except OSError as exc:
            print(f"Unable to write GITHUB_STEP_SUMMARY: {exc}", file=sys.stderr)
    return len(errors), len(warnings)


def main() -> int:
    structural_errors: list[str] = []
    try:
        portfolio = load_json(PORTFOLIO_MANIFEST_PATH)
        ledger = load_json(DEPENDENCY_LEDGER_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Dependency reconciliation files are unreadable: {exc}", file=sys.stderr)
        return 1

    if ledger.get("schema_version") != 1:
        structural_errors.append("unsupported dependency reconciliation schema")
    if ledger.get("rights_notice") != RIGHTS_NOTICE:
        structural_errors.append("dependency ledger has the wrong rights notice")
    if ledger.get("owner") != portfolio.get("owner"):
        structural_errors.append("dependency ledger owner differs from portfolio manifest")
    if not isinstance(ledger.get("policy"), dict):
        structural_errors.append("dependency policy must be an object")

    records = ledger.get("projects")
    if not isinstance(records, list):
        structural_errors.append("dependency projects must be a list")
        records = []
    expected = sorted(str(item) for item in portfolio.get("expected_public_repositories", []))
    actual = [str(item.get("repository") or "") for item in records if isinstance(item, dict)]
    duplicates = sorted({name for name in actual if name and actual.count(name) > 1})
    missing = sorted(set(expected) - set(actual))
    unexpected = sorted(set(actual) - set(expected))
    if duplicates:
        structural_errors.append(f"duplicate dependency records: {duplicates}")
    if missing:
        structural_errors.append(f"public repositories missing dependency records: {missing}")
    if unexpected:
        structural_errors.append(f"unexpected dependency records: {unexpected}")

    owner = str(ledger.get("owner") or "")
    profile_repository = str(portfolio.get("profile_repository") or "")
    results: list[ProjectResult] = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = {
            executor.submit(audit_project, owner, profile_repository, record): str(record.get("repository") or "")
            for record in records
            if isinstance(record, dict)
        }
        for future in as_completed(futures):
            repository = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                result = ProjectResult(repository=repository, status="unexpected_failure")
                add_finding(result, "error", "", f"unexpected dependency audit failure: {type(exc).__name__}: {exc}")
                results.append(result)
    results.sort(key=lambda item: item.repository.lower())

    errors, _ = write_reports(ledger, results, structural_errors)
    print(f"Dependency reconciliation: {'PASS' if not errors else 'FAIL'} ({len(results)} projects, {errors} errors)")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
