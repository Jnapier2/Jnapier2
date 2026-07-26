#!/usr/bin/env python3
"""Validate per-ecosystem Dependabot policy and prohibit automatic dependency merges.

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
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / ".github" / "dependabot-policy.json"
OUTPUT_DIR = ROOT / "audit-output"
RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
USER_AGENT = "Gateway-Dependabot-Policy-Audit/1.0"
HTTP_TIMEOUT_SECONDS = 20
HTTP_ATTEMPTS = 3
MAX_RESPONSE_BYTES = 5_000_000
MAX_WORKFLOWS_PER_REPOSITORY = 100

AUTO_MERGE_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("GitHub CLI pull-request merge", re.compile(r"\bgh\s+pr\s+merge\b", re.IGNORECASE)),
    (
        "GraphQL auto-merge mutation",
        re.compile(r"\benablePullRequestAutoMerge\b", re.IGNORECASE),
    ),
    (
        "pull-request merge API call",
        re.compile(r"\b(?:github\.rest\.|octokit\.rest\.)?pulls\.merge\s*\(", re.IGNORECASE),
    ),
    (
        "auto-merge GitHub Action",
        re.compile(
            r"(?im)^\s*(?:-\s*)?uses:\s*[^#\n]*(?:auto[-_]?merge|automerge|merge-pull-request)"
        ),
    ),
    (
        "GitHub pull merge endpoint",
        re.compile(r"/pulls/[^\s'\"}]+/merge\b", re.IGNORECASE),
    ),
)


@dataclass(frozen=True)
class Finding:
    severity: str
    repository: str
    path: str
    message: str


@dataclass
class RepositoryResult:
    repository: str
    expected_entries: int = 0
    actual_entries: int = 0
    workflow_files_checked: int = 0
    open_dependabot_prs_checked: int = 0
    findings: list[Finding] = field(default_factory=list)


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return payload


def request_bytes(url: str, *, accept: str = "application/vnd.github+json") -> bytes:
    headers = {
        "Accept": accept,
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last_error: Exception | None = None
    for attempt in range(1, HTTP_ATTEMPTS + 1):
        request = urllib.request.Request(url, headers=headers)
        try:
            with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                data = response.read(MAX_RESPONSE_BYTES + 1)
            if len(data) > MAX_RESPONSE_BYTES:
                raise ValueError(f"response exceeded {MAX_RESPONSE_BYTES} bytes")
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
                time.sleep(0.75 * attempt)
    raise RuntimeError(f"{url}: {last_error}")


def request_json(url: str) -> Any:
    return json.loads(request_bytes(url).decode("utf-8"))


def repository_url(owner: str, repository: str, suffix: str) -> str:
    return (
        f"https://api.github.com/repos/{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(repository, safe='')}/{suffix}"
    )


def fetch_text(owner: str, repository: str, path: str, *, allow_missing: bool = False) -> str | None:
    quoted_path = "/".join(urllib.parse.quote(part, safe="") for part in path.split("/"))
    url = repository_url(owner, repository, f"contents/{quoted_path}?ref=main")
    try:
        return request_bytes(url, accept="application/vnd.github.raw+json").decode("utf-8-sig")
    except RuntimeError as exc:
        if allow_missing and "HTTP Error 404" in str(exc):
            return None
        raise


def scalar(value: str) -> str:
    compact = value.strip()
    if len(compact) >= 2 and compact[0] == compact[-1] and compact[0] in {'"', "'"}:
        compact = compact[1:-1]
    return compact.strip()


def parse_dependabot(text: str) -> tuple[int | None, list[dict[str, Any]]]:
    version_match = re.search(r"(?m)^version:\s*['\"]?(\d+)['\"]?\s*(?:#.*)?$", text)
    version = int(version_match.group(1)) if version_match else None

    entries: list[dict[str, Any]] = []
    in_updates = False
    current: dict[str, Any] | None = None
    schedule_indent: int | None = None

    for number, raw_line in enumerate(text.splitlines(), start=1):
        if "\t" in raw_line:
            raise ValueError(f"line {number} contains a tab")
        stripped = raw_line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        indent = len(raw_line) - len(raw_line.lstrip(" "))

        if indent == 0:
            if stripped == "updates:":
                in_updates = True
                continue
            if in_updates:
                break
            continue
        if not in_updates:
            continue

        start = re.fullmatch(r"-\s*package-ecosystem:\s*(.+)", stripped)
        if start:
            if current is not None:
                entries.append(current)
            current = {
                "ecosystem": scalar(start.group(1)),
                "directory": None,
                "interval": None,
                "open_pull_requests_limit": None,
            }
            schedule_indent = None
            continue
        if current is None:
            continue

        if stripped.startswith("directory:"):
            current["directory"] = scalar(stripped.split(":", 1)[1])
            continue
        if stripped == "schedule:":
            schedule_indent = indent
            continue
        if stripped.startswith("interval:") and schedule_indent is not None and indent > schedule_indent:
            current["interval"] = scalar(stripped.split(":", 1)[1])
            continue
        if stripped.startswith("open-pull-requests-limit:"):
            raw_value = scalar(stripped.split(":", 1)[1])
            try:
                current["open_pull_requests_limit"] = int(raw_value)
            except ValueError as exc:
                raise ValueError(
                    f"open-pull-requests-limit is not an integer: {raw_value!r}"
                ) from exc

    if current is not None:
        entries.append(current)
    return version, entries


def workflow_paths(owner: str, repository: str) -> list[str]:
    payload = request_json(repository_url(owner, repository, "git/trees/main?recursive=1"))
    if not isinstance(payload, dict):
        raise ValueError("recursive tree response was not an object")
    if payload.get("truncated"):
        raise ValueError("recursive tree response was truncated")
    paths = sorted(
        str(item.get("path") or "")
        for item in payload.get("tree", [])
        if isinstance(item, dict)
        and item.get("type") == "blob"
        and str(item.get("path") or "").startswith(".github/workflows/")
        and Path(str(item.get("path") or "")).suffix.lower() in {".yml", ".yaml"}
    )
    if len(paths) > MAX_WORKFLOWS_PER_REPOSITORY:
        raise ValueError(
            f"workflow count {len(paths)} exceeds {MAX_WORKFLOWS_PER_REPOSITORY}"
        )
    return paths


def executable_workflow_text(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )


def add_finding(
    result: RepositoryResult,
    severity: str,
    path: str,
    message: str,
) -> None:
    result.findings.append(Finding(severity, result.repository, path, message))


def audit_auto_merge(owner: str, result: RepositoryResult) -> None:
    for path in workflow_paths(owner, result.repository):
        text = fetch_text(owner, result.repository, path)
        assert text is not None
        result.workflow_files_checked += 1
        executable = executable_workflow_text(text)
        for label, pattern in AUTO_MERGE_PATTERNS:
            if pattern.search(executable):
                add_finding(
                    result,
                    "error",
                    path,
                    f"automatic merge mechanism is forbidden: {label}",
                )

    pulls = request_json(
        repository_url(owner, result.repository, "pulls?state=open&per_page=100")
    )
    if not isinstance(pulls, list):
        raise ValueError("open pull-request response was not a list")
    if len(pulls) == 100:
        add_finding(
            result,
            "error",
            "pulls",
            "open pull-request scan reached the first-page limit",
        )
    for pull in pulls:
        if not isinstance(pull, dict):
            continue
        user = pull.get("user")
        login = str(user.get("login") or "") if isinstance(user, dict) else ""
        if login != "dependabot[bot]":
            continue
        result.open_dependabot_prs_checked += 1
        if pull.get("auto_merge") is not None:
            add_finding(
                result,
                "error",
                f"pulls/{pull.get('number')}",
                "an open Dependabot pull request has auto-merge enabled",
            )


def audit_repository(owner: str, record: dict[str, Any]) -> RepositoryResult:
    repository = str(record.get("repository") or "").strip()
    result = RepositoryResult(repository=repository)
    if not repository:
        add_finding(result, "error", "", "repository name is missing")
        return result

    expected = record.get("entries")
    if not isinstance(expected, list) or not expected:
        add_finding(result, "error", "", "entries must be a non-empty list")
        return result
    result.expected_entries = len(expected)

    try:
        text = fetch_text(owner, repository, ".github/dependabot.yml")
        assert text is not None
        version, actual = parse_dependabot(text)
    except Exception as exc:
        add_finding(
            result,
            "error",
            ".github/dependabot.yml",
            f"Dependabot policy could not be read: {type(exc).__name__}: {exc}",
        )
        return result

    result.actual_entries = len(actual)
    if version != 2:
        add_finding(
            result,
            "error",
            ".github/dependabot.yml",
            f"Dependabot schema must be 2, found {version!r}",
        )

    expected_by_ecosystem: dict[str, dict[str, Any]] = {}
    for item in expected:
        if not isinstance(item, dict):
            add_finding(result, "error", "", "expected entry must be an object")
            continue
        ecosystem = str(item.get("ecosystem") or "").strip()
        if not ecosystem:
            add_finding(result, "error", "", "expected ecosystem is missing")
        elif ecosystem in expected_by_ecosystem:
            add_finding(result, "error", "", f"duplicate expected ecosystem: {ecosystem}")
        else:
            expected_by_ecosystem[ecosystem] = item

    actual_by_ecosystem: dict[str, dict[str, Any]] = {}
    for item in actual:
        ecosystem = str(item.get("ecosystem") or "").strip()
        if not ecosystem:
            add_finding(
                result,
                "error",
                ".github/dependabot.yml",
                "an update block lacks package-ecosystem",
            )
        elif ecosystem in actual_by_ecosystem:
            add_finding(
                result,
                "error",
                ".github/dependabot.yml",
                f"duplicate actual ecosystem: {ecosystem}",
            )
        else:
            actual_by_ecosystem[ecosystem] = item

    missing = sorted(set(expected_by_ecosystem) - set(actual_by_ecosystem))
    unexpected = sorted(set(actual_by_ecosystem) - set(expected_by_ecosystem))
    if missing:
        add_finding(
            result,
            "error",
            ".github/dependabot.yml",
            f"expected ecosystems are missing: {missing}",
        )
    if unexpected:
        add_finding(
            result,
            "error",
            ".github/dependabot.yml",
            f"unexpected ecosystems are present: {unexpected}",
        )

    field_map = {
        "directory": "directory",
        "interval": "interval",
        "open_pull_requests_limit": "open_pull_requests_limit",
    }
    for ecosystem in sorted(set(expected_by_ecosystem) & set(actual_by_ecosystem)):
        expected_item = expected_by_ecosystem[ecosystem]
        actual_item = actual_by_ecosystem[ecosystem]
        for policy_name, parsed_name in field_map.items():
            expected_value = expected_item.get(policy_name)
            actual_value = actual_item.get(parsed_name)
            if actual_value != expected_value:
                add_finding(
                    result,
                    "error",
                    ".github/dependabot.yml",
                    f"{ecosystem} {policy_name} differs: "
                    f"expected {expected_value!r}, found {actual_value!r}",
                )

    try:
        audit_auto_merge(owner, result)
    except Exception as exc:
        add_finding(
            result,
            "error",
            ".github/workflows",
            f"auto-merge audit could not complete: {type(exc).__name__}: {exc}",
        )
    return result


def audit_absent_repository(owner: str, repository: str) -> RepositoryResult:
    result = RepositoryResult(repository=repository)
    try:
        text = fetch_text(
            owner,
            repository,
            ".github/dependabot.yml",
            allow_missing=True,
        )
    except Exception as exc:
        add_finding(
            result,
            "error",
            ".github/dependabot.yml",
            f"absence check could not complete: {type(exc).__name__}: {exc}",
        )
        return result
    if text is not None:
        add_finding(
            result,
            "error",
            ".github/dependabot.yml",
            "Dependabot configuration must remain absent for this sealed release",
        )
    return result


def write_reports(
    policy: dict[str, Any],
    results: list[RepositoryResult],
    structural_errors: list[str],
) -> int:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    findings = [item for result in results for item in result.findings]
    findings.extend(
        Finding("error", "dependabot-policy", "", message)
        for message in structural_errors
    )
    findings.sort(
        key=lambda item: (
            item.severity != "error",
            item.repository.lower(),
            item.path,
            item.message,
        )
    )
    errors = [item for item in findings if item.severity == "error"]
    generated_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    payload = {
        "schema_version": 1,
        "generated_utc": generated_utc,
        "owner": policy.get("owner"),
        "rights_notice": RIGHTS_NOTICE,
        "result": "PASS" if not errors else "FAIL",
        "repositories_checked": len(results),
        "ecosystem_entries_checked": sum(item.actual_entries for item in results),
        "workflow_files_checked": sum(item.workflow_files_checked for item in results),
        "open_dependabot_prs_checked": sum(
            item.open_dependabot_prs_checked for item in results
        ),
        "error_count": len(errors),
        "repositories": [
            {
                "repository": item.repository,
                "expected_entries": item.expected_entries,
                "actual_entries": item.actual_entries,
                "workflow_files_checked": item.workflow_files_checked,
                "open_dependabot_prs_checked": item.open_dependabot_prs_checked,
                "error_count": sum(
                    1 for finding in item.findings if finding.severity == "error"
                ),
            }
            for item in results
        ],
        "findings": [asdict(item) for item in findings],
    }
    (OUTPUT_DIR / "dependabot-policy-audit.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Dependabot policy audit",
        "",
        f"Generated: `{generated_utc}`",
        "",
        f"- Result: **{payload['result']}**",
        f"- Repositories checked: **{payload['repositories_checked']}**",
        f"- Ecosystem entries checked: **{payload['ecosystem_entries_checked']}**",
        f"- Workflow files checked for automatic merge: **{payload['workflow_files_checked']}**",
        f"- Open Dependabot PRs checked: **{payload['open_dependabot_prs_checked']}**",
        f"- Errors: **{payload['error_count']}**",
        "",
        "## Findings",
        "",
    ]
    if findings:
        for item in findings:
            location = f"/{item.path}" if item.path else ""
            lines.append(
                f"- **{item.severity.upper()}** `{item.repository}{location}` — {item.message}"
            )
    else:
        lines.append(
            "Every ecosystem block matches its declared cadence and PR limit, "
            "and no automatic dependency-merge mechanism was found."
        )
    lines.extend(
        [
            "",
            RIGHTS_NOTICE,
            "",
            "This notice does not replace or infer a software license. "
            "Third-party components retain their respective notices and licenses.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    (OUTPUT_DIR / "dependabot-policy-audit.md").write_text(
        markdown,
        encoding="utf-8",
    )
    print(markdown)

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if summary_path:
        try:
            with Path(summary_path).open("a", encoding="utf-8") as handle:
                handle.write(markdown)
        except OSError as exc:
            print(f"Unable to write GITHUB_STEP_SUMMARY: {exc}", file=sys.stderr)
    return len(errors)


def main() -> int:
    structural_errors: list[str] = []
    try:
        policy = load_json(POLICY_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Dependabot policy is unreadable: {exc}", file=sys.stderr)
        return 1

    if policy.get("schema_version") != 1:
        structural_errors.append("unsupported Dependabot policy schema")
    if policy.get("rights_notice") != RIGHTS_NOTICE:
        structural_errors.append("Dependabot policy has the wrong rights notice")
    if policy.get("auto_merge_policy") != "forbidden":
        structural_errors.append("auto_merge_policy must be 'forbidden'")

    owner = str(policy.get("owner") or "").strip()
    if not owner:
        structural_errors.append("owner is missing")

    records = policy.get("repositories")
    if not isinstance(records, list):
        structural_errors.append("repositories must be a list")
        records = []
    names = [
        str(record.get("repository") or "")
        for record in records
        if isinstance(record, dict)
    ]
    duplicates = sorted({name for name in names if name and names.count(name) > 1})
    if duplicates:
        structural_errors.append(f"duplicate monitored repositories: {duplicates}")

    absent = policy.get("repositories_without_dependabot", [])
    if not isinstance(absent, list) or not all(isinstance(item, str) for item in absent):
        structural_errors.append("repositories_without_dependabot must be strings")
        absent = []
    overlap = sorted(set(names) & set(absent))
    if overlap:
        structural_errors.append(
            f"repositories cannot be both monitored and absent: {overlap}"
        )

    results: list[RepositoryResult] = []
    with ThreadPoolExecutor(max_workers=6) as executor:
        futures: dict[Any, str] = {}
        for record in records:
            if isinstance(record, dict):
                name = str(record.get("repository") or "")
                futures[executor.submit(audit_repository, owner, record)] = name
        for repository in absent:
            futures[
                executor.submit(audit_absent_repository, owner, repository)
            ] = repository
        for future in as_completed(futures):
            repository = futures[future]
            try:
                results.append(future.result())
            except Exception as exc:
                result = RepositoryResult(repository=repository)
                add_finding(
                    result,
                    "error",
                    "",
                    f"unexpected policy-audit failure: {type(exc).__name__}: {exc}",
                )
                results.append(result)
    results.sort(key=lambda item: item.repository.lower())

    errors = write_reports(policy, results, structural_errors)
    print(
        f"Dependabot policy audit: {'PASS' if not errors else 'FAIL'} "
        f"({len(results)} repositories, {errors} errors)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
