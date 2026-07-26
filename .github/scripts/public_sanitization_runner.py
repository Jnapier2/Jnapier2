#!/usr/bin/env python3
"""Run the public sanitation audit with reviewed coverage and exception policy.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import public_sanitization_audit as audit

ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_PATH = ROOT / ".github" / "public-sanitization-allowlist.json"
RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."


def load_allowlist() -> tuple[set[tuple[str, str, str]], dict[tuple[str, str, str], str]]:
    try:
        payload: Any = json.loads(ALLOWLIST_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"Public sanitation allowlist is unreadable: {exc}") from exc

    if not isinstance(payload, dict):
        raise SystemExit("Public sanitation allowlist must contain a JSON object")
    if payload.get("schema_version") != 1:
        raise SystemExit("Unsupported public sanitation allowlist schema")
    if payload.get("rights_notice") != RIGHTS_NOTICE:
        raise SystemExit("Public sanitation allowlist rights notice is missing or changed")

    entries = payload.get("entries")
    if not isinstance(entries, list):
        raise SystemExit("Public sanitation allowlist entries must be a list")

    keys: set[tuple[str, str, str]] = set()
    reasons: dict[tuple[str, str, str], str] = {}
    for index, item in enumerate(entries):
        if not isinstance(item, dict):
            raise SystemExit(f"Public sanitation allowlist entry {index} must be an object")
        repository = str(item.get("repository", "")).strip()
        path = str(item.get("path", "")).strip()
        rule = str(item.get("rule", "")).strip()
        if not repository or not path or not rule:
            raise SystemExit(
                f"Public sanitation allowlist entry {index} requires repository, path, and rule"
            )
        key = (repository, path, rule)
        if key in keys:
            raise SystemExit(f"Duplicate public sanitation allowlist entry: {key}")
        reason = str(item.get("reason", "")).strip()
        if not reason:
            raise SystemExit(f"Public sanitation allowlist entry lacks a reason: {key}")
        keys.add(key)
        reasons[key] = reason
    return keys, reasons


def main() -> int:
    allowed, reasons = load_allowlist()
    observed: set[tuple[str, str, str]] = set()

    original_add_finding = audit.add_finding
    original_max_file_bytes = audit.MAX_FILE_BYTES
    original_allowed_domains = set(audit.ALLOWED_EMAIL_DOMAINS)
    original_unix_user_path = audit.UNIX_USER_PATH
    original_public_copy_patterns = list(audit.PUBLIC_COPY_PATTERNS)

    audit.MAX_FILE_BYTES = 5_000_000
    audit.ALLOWED_EMAIL_DOMAINS.update({"example.invalid", "external-api.kalshi.com"})
    audit.UNIX_USER_PATH = re.compile(r"/(?:home|Users)/([A-Za-z0-9._-]+)/")
    if not any(rule == "copy.recruiter_meta" for rule, _ in audit.PUBLIC_COPY_PATTERNS):
        audit.PUBLIC_COPY_PATTERNS.append(
            ("copy.recruiter_meta", re.compile(r"(?i)\brecruiters?\b"))
        )

    def filtered_add_finding(result: audit.RepositoryResult, **kwargs: object) -> None:
        key = (
            result.repository,
            str(kwargs.get("path", "")),
            str(kwargs.get("rule", "")),
        )
        if key in allowed:
            observed.add(key)
            return
        original_add_finding(result, **kwargs)

    audit.add_finding = filtered_add_finding
    try:
        result = audit.main()
    finally:
        audit.add_finding = original_add_finding
        audit.MAX_FILE_BYTES = original_max_file_bytes
        audit.ALLOWED_EMAIL_DOMAINS.clear()
        audit.ALLOWED_EMAIL_DOMAINS.update(original_allowed_domains)
        audit.UNIX_USER_PATH = original_unix_user_path
        audit.PUBLIC_COPY_PATTERNS[:] = original_public_copy_patterns

    stale = sorted(allowed - observed)
    if stale:
        for key in stale:
            print(f"Stale sanitation allowlist entry: {key} — {reasons[key]}")
        return 1
    print(f"Reviewed sanitation exceptions applied: {len(observed)}")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
