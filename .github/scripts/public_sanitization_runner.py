#!/usr/bin/env python3
"""Run the public sanitation audit with reviewed coverage and exception policy.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import public_sanitization_audit as audit

ROOT = Path(__file__).resolve().parents[2]
ALLOWLIST_PATH = ROOT / ".github" / "public-sanitization-allowlist.json"


def load_allowlist() -> tuple[set[tuple[str, str, str]], dict[tuple[str, str, str], str]]:
    payload = json.loads(ALLOWLIST_PATH.read_text(encoding="utf-8"))
    if payload.get("schema_version") != 1:
        raise SystemExit("Unsupported public sanitation allowlist schema")
    keys: set[tuple[str, str, str]] = set()
    reasons: dict[tuple[str, str, str], str] = {}
    for item in payload.get("entries", []):
        key = (str(item["repository"]), str(item["path"]), str(item["rule"]))
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

    audit.MAX_FILE_BYTES = 5_000_000
    audit.ALLOWED_EMAIL_DOMAINS.update({"example.invalid", "external-api.kalshi.com"})
    audit.UNIX_USER_PATH = re.compile(r"/(?:home|Users)/([A-Za-z0-9._-]+)/")
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
    result = audit.main()

    stale = sorted(allowed - observed)
    if stale:
        for key in stale:
            print(f"Stale sanitation allowlist entry: {key} — {reasons[key]}")
        return 1
    print(f"Reviewed sanitation exceptions applied: {len(observed)}")
    return result


if __name__ == "__main__":
    raise SystemExit(main())
