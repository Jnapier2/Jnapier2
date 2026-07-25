#!/usr/bin/env python3
"""Validate public repository release representation against the declared ledger.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import base64
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
LEDGER_PATH = ROOT / ".github" / "release-reconciliation.json"
PORTFOLIO_MANIFEST_PATH = ROOT / ".github" / "portfolio-manifest.json"
RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
ALLOWED_STATUSES = {
    "current",
    "nonversioned_current",
    "github_source_authority",
    "github_source_only",
    "verified_successor_pending_exact_transfer",
    "verified_successor_under_reconciliation",
    "verified_successor_unavailable",
}
PENDING_STATUSES = {
    "verified_successor_pending_exact_transfer",
    "verified_successor_under_reconciliation",
    "verified_successor_unavailable",
}
HTTP_TIMEOUT_SECONDS = 15
HTTP_ATTEMPTS = 3


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must contain a JSON object")
    return data


def github_headers() -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "Gateway-Release-Reconciliation-Audit/1.0",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def fetch_public_file(owner: str, repository: str, path: str) -> str:
    quoted_path = "/".join(urllib.parse.quote(part, safe="") for part in path.split("/"))
    url = (
        f"https://api.github.com/repos/{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(repository, safe='')}/contents/{quoted_path}?ref=main"
    )
    last_error: Exception | None = None
    for attempt in range(1, HTTP_ATTEMPTS + 1):
        try:
            request = urllib.request.Request(url, headers=github_headers())
            with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                payload = json.loads(response.read(4_000_000).decode("utf-8"))
            if payload.get("encoding") != "base64" or not isinstance(payload.get("content"), str):
                raise ValueError("GitHub did not return base64 file content")
            return base64.b64decode(payload["content"], validate=False).decode("utf-8-sig")
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt < HTTP_ATTEMPTS:
                time.sleep(0.75 * attempt)
    raise RuntimeError(f"unable to read {repository}/{path}: {last_error}")


def workflow_message(level: str, message: str) -> None:
    print(f"::{level}::{message}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []

    try:
        ledger = load_json(LEDGER_PATH)
        portfolio = load_json(PORTFOLIO_MANIFEST_PATH)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Release reconciliation files are unreadable: {exc}", file=sys.stderr)
        return 1

    if ledger.get("schema_version") != 1:
        errors.append("unsupported release reconciliation schema")
    if ledger.get("rights_notice") != RIGHTS_NOTICE:
        errors.append("release reconciliation ledger has the wrong rights notice")

    projects = ledger.get("projects")
    if not isinstance(projects, list):
        errors.append("release reconciliation projects must be a list")
        projects = []

    expected = sorted(item["name"] for item in portfolio.get("repositories", []) if isinstance(item, dict) and item.get("name"))
    actual_names = [item.get("repository") for item in projects if isinstance(item, dict)]
    duplicates = sorted({name for name in actual_names if name and actual_names.count(name) > 1})
    if duplicates:
        errors.append(f"duplicate release reconciliation repositories: {duplicates}")
    missing = sorted(set(expected) - set(actual_names))
    unexpected = sorted(set(actual_names) - set(expected))
    if missing:
        errors.append(f"repositories missing from release reconciliation: {missing}")
    if unexpected:
        errors.append(f"unexpected release reconciliation repositories: {unexpected}")

    owner = str(ledger.get("owner") or "")
    if owner != portfolio.get("owner"):
        errors.append("release reconciliation owner does not match portfolio manifest")

    for item in projects:
        if not isinstance(item, dict):
            errors.append("release reconciliation contains a non-object project record")
            continue
        repository = str(item.get("repository") or "")
        status = str(item.get("status") or "")
        represented = item.get("represented_version")
        latest = item.get("latest_verified_version")
        marker = item.get("source_marker")

        if status not in ALLOWED_STATUSES:
            errors.append(f"{repository}: unsupported status {status!r}")
            continue
        if not str(item.get("note") or "").strip():
            errors.append(f"{repository}: explanatory note is missing")

        if status in PENDING_STATUSES:
            if not represented or not latest or represented == latest:
                errors.append(f"{repository}: pending status requires distinct represented and latest versions")
            warnings.append(f"{repository}: GitHub represents {represented}; latest verified is {latest} ({status})")
        elif represented is not None and latest is not None and represented != latest:
            errors.append(f"{repository}: non-pending status has version drift {represented} != {latest}")

        if marker is not None:
            if not isinstance(marker, dict) or not marker.get("path") or not marker.get("text"):
                errors.append(f"{repository}: source marker is incomplete")
                continue
            try:
                source = fetch_public_file(owner, repository, str(marker["path"]))
            except Exception as exc:
                errors.append(f"{repository}: {exc}")
                continue
            if str(marker["text"]) not in source:
                errors.append(
                    f"{repository}: declared represented version marker is absent from {marker['path']}: {marker['text']}"
                )

    summary_lines = [
        "# Release reconciliation",
        "",
        f"- Public project records: **{len(projects)}**",
        f"- Structural/version errors: **{len(errors)}**",
        f"- Explicit pending or blocked successors: **{len(warnings)}**",
        "",
    ]
    if warnings:
        summary_lines.append("## Pending or blocked successors")
        summary_lines.extend(f"- {message}" for message in warnings)
        summary_lines.append("")
    summary_lines.append(RIGHTS_NOTICE)

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if summary_path:
        with Path(summary_path).open("a", encoding="utf-8") as handle:
            handle.write("\n".join(summary_lines) + "\n")

    for message in warnings:
        workflow_message("warning", message)
    for message in errors:
        workflow_message("error", message)

    if errors:
        print(f"Release reconciliation: FAIL ({len(errors)} error(s), {len(warnings)} warning(s))")
        return 1
    print(f"Release reconciliation: PASS ({len(projects)} projects, {len(warnings)} explicit pending/blocked successor(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
