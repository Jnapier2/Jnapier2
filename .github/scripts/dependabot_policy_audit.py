#!/usr/bin/env python3
"""Validate per-ecosystem Dependabot policy and prohibit dependency auto-merge.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import io
import json
import os
import re
import stat
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
POLICY_PATH = ROOT / ".github" / "dependabot-policy.json"
PORTFOLIO_MANIFEST_PATH = ROOT / ".github" / "portfolio-manifest.json"
OUTPUT_DIR = Path(os.environ.get("PORTFOLIO_AUDIT_OUTPUT_DIR", ROOT / "audit-output"))
RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
USER_AGENT = "Gateway-Dependabot-Policy-Audit/2.0"
HTTP_ATTEMPTS = 4
HTTP_TIMEOUT_SECONDS = 30
MAX_ARCHIVE_BYTES = 50_000_000
MAX_ARCHIVE_FILES = 5_000
MAX_ARCHIVE_UNCOMPRESSED_BYTES = 150_000_000
MAX_TEXT_BYTES = 5_000_000
MAX_API_BYTES = 5_000_000
MAX_WORKFLOWS_PER_REPOSITORY = 100
ARCHIVE_CACHE: dict[tuple[str, str], dict[str, bytes]] = {}

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
        "automatic merge GitHub Action",
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
    policy_mode: str
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


def add_finding(
    result: RepositoryResult,
    severity: str,
    path: str,
    message: str,
) -> None:
    result.findings.append(Finding(severity, result.repository, path, message))


def request_bytes(
    url: str,
    *,
    accept: str,
    maximum_bytes: int,
) -> bytes:
    headers = {
        "Accept": accept,
        "User-Agent": USER_AGENT,
    }
    if urllib.parse.urlparse(url).hostname == "api.github.com":
        headers["X-GitHub-Api-Version"] = "2022-11-28"
        token = os.environ.get("GITHUB_TOKEN", "").strip()
        if token:
            headers["Authorization"] = f"Bearer {token}"

    last_error: Exception | None = None
    for attempt in range(1, HTTP_ATTEMPTS + 1):
        request = urllib.request.Request(url, headers=headers)
        try:
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
            retryable = not isinstance(exc, urllib.error.HTTPError) or exc.code in {
                403,
                408,
                429,
                500,
                502,
                503,
                504,
            }
            if attempt < HTTP_ATTEMPTS and retryable:
                time.sleep(min(8.0, 0.75 * (2 ** (attempt - 1))))
                continue
            break
    raise RuntimeError(f"{url}: {last_error}")


def request_json(url: str) -> Any:
    return json.loads(
        request_bytes(
            url,
            accept="application/vnd.github+json",
            maximum_bytes=MAX_API_BYTES,
        ).decode("utf-8")
    )


def load_archive(owner: str, repository: str) -> dict[str, bytes]:
    key = (owner, repository)
    cached = ARCHIVE_CACHE.get(key)
    if cached is not None:
        return cached

    url = (
        "https://codeload.github.com/"
        f"{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(repository, safe='')}/zip/refs/heads/main"
    )
    data = request_bytes(
        url,
        accept="application/zip, application/octet-stream",
        maximum_bytes=MAX_ARCHIVE_BYTES,
    )
    files: dict[str, bytes] = {}
    total_uncompressed = 0
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = archive.infolist()
        if len(members) > MAX_ARCHIVE_FILES:
            raise ValueError(
                f"archive has {len(members)} entries; limit is {MAX_ARCHIVE_FILES}"
            )
        for member in members:
            normalized = member.filename.replace("\\", "/")
            path = PurePosixPath(normalized)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"unsafe archive path: {normalized}")
            mode = (member.external_attr >> 16) & 0xFFFF
            if mode and stat.S_ISLNK(mode):
                raise ValueError(f"archive symlink is not allowed: {normalized}")
            if member.is_dir() or len(path.parts) < 2:
                continue
            total_uncompressed += member.file_size
            if total_uncompressed > MAX_ARCHIVE_UNCOMPRESSED_BYTES:
                raise ValueError(
                    "archive uncompressed size exceeds "
                    f"{MAX_ARCHIVE_UNCOMPRESSED_BYTES} bytes"
                )
            relative = PurePosixPath(*path.parts[1:]).as_posix()
            if relative in files:
                raise ValueError(f"duplicate archive path: {relative}")
            if member.file_size <= MAX_TEXT_BYTES:
                files[relative] = archive.read(member)
    ARCHIVE_CACHE[key] = files
    return files


def fetch_text(
    owner: str,
    repository: str,
    path: str,
    *,
    allow_missing: bool = False,
) -> str | None:
    data = load_archive(owner, repository).get(path)
    if data is None:
        if allow_missing:
            return None
        raise FileNotFoundError(f"{repository}/{path} is missing from main")
    return data.decode("utf-8-sig")


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


def executable_workflow_text(text: str) -> str:
    return "\n".join(
        line for line in text.splitlines() if not line.lstrip().startswith("#")
    )


def workflow_paths(files: dict[str, bytes]) -> list[str]:
    paths = sorted(
        path
        for path in files
        if path.startswith(".github/workflows/")
        and PurePosixPath(path).suffix.lower() in {".yml", ".yaml"}
    )
    if len(paths) > MAX_WORKFLOWS_PER_REPOSITORY:
        raise ValueError(
            f"workflow count {len(paths)} exceeds {MAX_WORKFLOWS_PER_REPOSITORY}"
        )
    return paths


def audit_auto_merge(owner: str, result: RepositoryResult) -> None:
    files = load_archive(owner, result.repository)
    for path in workflow_paths(files):
        data = files[path]
        if len(data) > MAX_TEXT_BYTES:
            raise ValueError(f"workflow exceeds {MAX_TEXT_BYTES} bytes: {path}")
        text = data.decode("utf-8-sig")
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

    url = (
        f"https://api.github.com/repos/{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(result.repository, safe='')}/pulls?state=open&per_page=100"
    )
    pulls = request_json(url)
    if not isinstance(pulls, list):
        raise ValueError("open pull-request response was not a list")
    if len(pulls) == 100:
        raise ValueError("open pull-request scan reached the first-page limit")
    for pull in pulls:
        if not isinstance(pull, dict):
            continue
        user = pull.get("user")
        login = str(user.get("login") or "") if isinstance(user, dict) else ""
        if login not in {"dependabot[bot]", "dependabot"}:
            continue
        result.open_dependabot_prs_checked += 1
        if pull.get("auto_merge") is not None:
            add_finding(
                result,
                "error",
                f"pulls/{pull.get('number')}",
                "an open Dependabot pull request has auto-merge enabled",
            )


def audit_monitored_repository(
    owner: str,
    record: dict[str, Any],
) -> RepositoryResult:
    repository = str(record.get("repository") or "").strip()
    result = RepositoryResult(repository=repository, policy_mode="monitored")
    expected = record.get("entries")
    if not repository:
        add_finding(result, "error", "", "repository name is missing")
        return result
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

    for ecosystem in sorted(set(expected_by_ecosystem) & set(actual_by_ecosystem)):
        expected_item = expected_by_ecosystem[ecosystem]
        actual_item = actual_by_ecosystem[ecosystem]
        for field_name in ("directory", "interval", "open_pull_requests_limit"):
            expected_value = expected_item.get(field_name)
            actual_value = actual_item.get(field_name)
            if actual_value != expected_value:
                add_finding(
                    result,
                    "error",
                    ".github/dependabot.yml",
                    f"{ecosystem} {field_name} differs: "
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


def audit_absent_repository(
    owner: str,
    record: dict[str, Any],
) -> RepositoryResult:
    repository = str(record.get("repository") or "").strip()
    result = RepositoryResult(repository=repository, policy_mode="required-absent")
    if not repository:
        add_finding(result, "error", "", "repository name is missing")
        return result
    reason = str(record.get("reason") or "").strip()
    if not reason:
        add_finding(result, "error", "", "absence reason is missing")
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
                "policy_mode": item.policy_mode,
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
            "Every declared ecosystem block matches its cadence and PR limit, "
            "sealed-release absence rules hold, and no dependency auto-merge mechanism was found."
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
        portfolio = load_json(PORTFOLIO_MANIFEST_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Dependabot policy inputs are unreadable: {exc}", file=sys.stderr)
        return 1

    if policy.get("schema_version") != 1:
        structural_errors.append("unsupported Dependabot policy schema")
    if policy.get("rights_notice") != RIGHTS_NOTICE:
        structural_errors.append("Dependabot policy has the wrong rights notice")
    if policy.get("auto_merge_policy") != "forbidden":
        structural_errors.append("auto_merge_policy must be 'forbidden'")
    if not str(policy.get("review_rule") or "").strip():
        structural_errors.append("review_rule is missing")

    owner = str(policy.get("owner") or "").strip()
    if not owner:
        structural_errors.append("owner is missing")
    if owner != str(portfolio.get("owner") or ""):
        structural_errors.append("policy owner differs from portfolio owner")

    expected_public = {
        str(item)
        for item in portfolio.get("expected_public_repositories", [])
        if str(item)
    }
    records = policy.get("repositories")
    if not isinstance(records, list):
        structural_errors.append("repositories must be a list")
        records = []
    monitored_names = [
        str(record.get("repository") or "")
        for record in records
        if isinstance(record, dict)
    ]
    duplicates = sorted(
        {name for name in monitored_names if name and monitored_names.count(name) > 1}
    )
    if duplicates:
        structural_errors.append(f"duplicate monitored repositories: {duplicates}")

    absent_records = policy.get("repositories_without_dependabot", [])
    if not isinstance(absent_records, list):
        structural_errors.append("repositories_without_dependabot must be a list")
        absent_records = []
    absent_names = [
        str(record.get("repository") or "")
        for record in absent_records
        if isinstance(record, dict)
    ]
    if len(absent_names) != len(absent_records):
        structural_errors.append("every absence record must be an object")
    absent_duplicates = sorted(
        {name for name in absent_names if name and absent_names.count(name) > 1}
    )
    if absent_duplicates:
        structural_errors.append(f"duplicate absence repositories: {absent_duplicates}")
    overlap = sorted(set(monitored_names) & set(absent_names))
    if overlap:
        structural_errors.append(
            f"repositories cannot be both monitored and required absent: {overlap}"
        )
    unknown = sorted((set(monitored_names) | set(absent_names)) - expected_public)
    if unknown:
        structural_errors.append(f"policy references unknown public repositories: {unknown}")

    results: list[RepositoryResult] = []
    for record in records:
        if isinstance(record, dict):
            results.append(audit_monitored_repository(owner, record))
    for record in absent_records:
        if isinstance(record, dict):
            results.append(audit_absent_repository(owner, record))
    results.sort(key=lambda item: item.repository.lower())

    errors = write_reports(policy, results, structural_errors)
    print(
        f"Dependabot policy audit: {'PASS' if not errors else 'FAIL'} "
        f"({len(results)} repositories, {errors} errors)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
