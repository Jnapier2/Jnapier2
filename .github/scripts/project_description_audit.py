#!/usr/bin/env python3
"""Validate canonical public project descriptions and report live GitHub drift.

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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / ".github" / "portfolio-manifest.json"
PROFILE_README_PATH = ROOT / "README.md"
OUTPUT_DIR = Path(os.environ.get("PORTFOLIO_AUDIT_OUTPUT_DIR", ROOT / "audit-output"))
RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
HTTP_TIMEOUT_SECONDS = 15
HTTP_ATTEMPTS = 3
USER_AGENT = "Gateway-Project-Description-Audit/1.0"
MIN_DESCRIPTION_CHARS = 60
MAX_DESCRIPTION_CHARS = 220
MIN_PROFILE_SUMMARY_CHARS = 80
MAX_PROFILE_SUMMARY_CHARS = 380
FORBIDDEN_PUBLIC_COPY = (
    "value add",
    "backend speak",
    "prompt strategy",
    "vibe coded",
    "production-ready",
    "guaranteed profit",
    "v0.15.0",
)


def normalize_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def add_finding(collection: list[dict[str, str]], area: str, message: str) -> None:
    collection.append({"area": area, "message": message})


def request_repository_metadata(owner: str, repository: str) -> dict[str, Any]:
    url = (
        f"https://api.github.com/repos/{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(repository, safe='')}"
    )
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token:
        headers["Authorization"] = f"Bearer {token}"

    last_error: Exception | None = None
    for attempt in range(1, HTTP_ATTEMPTS + 1):
        try:
            request = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                payload = json.loads(response.read(2_000_000).decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("GitHub metadata response was not an object")
            return payload
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
            json.JSONDecodeError,
        ) as exc:
            last_error = exc
            if attempt < HTTP_ATTEMPTS:
                time.sleep(0.75 * attempt)
    raise RuntimeError(f"unable to read live repository metadata: {last_error}")


def main() -> int:
    errors: list[dict[str, str]] = []
    warnings: list[dict[str, str]] = []

    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        profile_readme = PROFILE_README_PATH.read_text(encoding="utf-8")
    except (OSError, json.JSONDecodeError) as exc:
        print(f"Project description audit: FAIL ({exc})", file=sys.stderr)
        return 1

    if not isinstance(manifest, dict):
        print("Project description audit: FAIL (manifest must be a JSON object)", file=sys.stderr)
        return 1
    if manifest.get("schema_version") != 1:
        add_finding(errors, "manifest", "portfolio manifest schema must be 1")
    if manifest.get("rights_notice") != RIGHTS_NOTICE:
        add_finding(errors, "manifest", "canonical rights notice is missing or changed")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(manifest.get("description_reviewed_on") or "")):
        add_finding(errors, "manifest", "description_reviewed_on must use YYYY-MM-DD")
    if not isinstance(manifest.get("description_policy"), dict):
        add_finding(errors, "manifest", "description_policy must be an object")

    owner = normalize_text(manifest.get("owner"))
    repositories = manifest.get("repositories")
    if not owner:
        add_finding(errors, "manifest", "owner is missing")
    if not isinstance(repositories, list):
        add_finding(errors, "manifest", "repositories must be a list")
        repositories = []

    rows: list[dict[str, Any]] = []
    names = [normalize_text(item.get("name")) for item in repositories if isinstance(item, dict)]
    duplicate_names = sorted({name for name in names if name and names.count(name) > 1})
    if duplicate_names:
        add_finding(errors, "manifest", f"duplicate repository records: {duplicate_names}")

    expected_names = {
        normalize_text(item)
        for item in manifest.get("expected_public_repositories", [])
        if normalize_text(item) and normalize_text(item) != manifest.get("profile_repository")
    }
    actual_names = {name for name in names if name}
    missing_records = sorted(expected_names - actual_names)
    extra_records = sorted(actual_names - expected_names)
    if missing_records:
        add_finding(errors, "manifest", f"public repositories missing description records: {missing_records}")
    if extra_records:
        add_finding(errors, "manifest", f"unexpected description records: {extra_records}")

    for index, item in enumerate(repositories):
        area = f"record[{index}]"
        if not isinstance(item, dict):
            add_finding(errors, area, "repository record must be an object")
            continue

        name = normalize_text(item.get("name"))
        display_name = normalize_text(item.get("display_name"))
        expected_description = normalize_text(item.get("expected_description"))
        profile_summary = normalize_text(item.get("profile_summary"))
        area = name or area

        for field_name, value in (
            ("name", name),
            ("display_name", display_name),
            ("expected_description", expected_description),
            ("profile_summary", profile_summary),
        ):
            if not value:
                add_finding(errors, area, f"{field_name} is missing")

        if name and not re.fullmatch(r"[A-Za-z0-9._-]+", name):
            add_finding(errors, area, "repository name contains unsupported characters")
        if "\n" in str(item.get("expected_description") or ""):
            add_finding(errors, area, "expected_description must be one line")
        if "\n" in str(item.get("profile_summary") or ""):
            add_finding(errors, area, "profile_summary must be one line")
        if expected_description and not (
            MIN_DESCRIPTION_CHARS <= len(expected_description) <= MAX_DESCRIPTION_CHARS
        ):
            add_finding(
                errors,
                area,
                f"expected_description length {len(expected_description)} is outside "
                f"{MIN_DESCRIPTION_CHARS}-{MAX_DESCRIPTION_CHARS}",
            )
        if profile_summary and not (
            MIN_PROFILE_SUMMARY_CHARS <= len(profile_summary) <= MAX_PROFILE_SUMMARY_CHARS
        ):
            add_finding(
                errors,
                area,
                f"profile_summary length {len(profile_summary)} is outside "
                f"{MIN_PROFILE_SUMMARY_CHARS}-{MAX_PROFILE_SUMMARY_CHARS}",
            )

        lower_copy = f"{expected_description}\n{profile_summary}".lower()
        for forbidden in FORBIDDEN_PUBLIC_COPY:
            if forbidden in lower_copy:
                add_finding(errors, area, f"public description contains forbidden phrase: {forbidden}")

        if expected_description and ("http://" in expected_description or "https://" in expected_description):
            add_finding(errors, area, "expected_description must not contain a URL")
        if expected_description and any(marker in expected_description for marker in ("[", "]", "`", "<", ">")):
            add_finding(errors, area, "expected_description must be plain text")

        if profile_summary:
            summary_count = profile_readme.count(profile_summary)
            if summary_count != 1:
                add_finding(
                    errors,
                    area,
                    f"profile_summary must appear exactly once in README.md; found {summary_count}",
                )
        if name:
            repository_url = f"https://github.com/{owner}/{name}"
            url_count = profile_readme.count(repository_url)
            if url_count != 1:
                add_finding(
                    errors,
                    area,
                    f"repository URL must appear exactly once in README.md; found {url_count}",
                )

        rows.append(
            {
                "repository": name,
                "display_name": display_name,
                "tier": normalize_text(item.get("tier")),
                "expected_description": expected_description,
                "profile_summary": profile_summary,
                "live_description": None,
                "description_match": None,
                "metadata_error": None,
            }
        )

    row_by_name = {row["repository"]: row for row in rows if row["repository"]}
    offline = os.environ.get("DESCRIPTION_AUDIT_OFFLINE", "").strip() == "1"
    if offline:
        for row in row_by_name.values():
            row["metadata_error"] = "offline validation skipped"
    else:
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {
                executor.submit(request_repository_metadata, owner, name): name
                for name in row_by_name
            }
            for future in as_completed(futures):
                name = futures[future]
                row = row_by_name[name]
                try:
                    metadata = future.result()
                except Exception as exc:
                    row["metadata_error"] = str(exc)
                    add_finding(warnings, name, f"live About description could not be checked: {exc}")
                    continue

                live_description = normalize_text(metadata.get("description"))
                row["live_description"] = live_description
                row["description_match"] = live_description == row["expected_description"]
                if not live_description:
                    add_finding(
                        warnings,
                        name,
                        "live GitHub About description is empty; copy the canonical description from the manifest",
                    )
                elif not row["description_match"]:
                    add_finding(
                        warnings,
                        name,
                        "live GitHub About description differs from the canonical reviewed description",
                    )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    status = "FAIL" if errors else "PASS_WITH_METADATA_DRIFT" if warnings else "PASS"
    generated_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    report = {
        "schema_version": 1,
        "generated_utc": generated_utc,
        "owner": owner,
        "description_reviewed_on": manifest.get("description_reviewed_on"),
        "status": status,
        "structural_errors": len(errors),
        "live_metadata_warnings": len(warnings),
        "repositories_checked": len(rows),
        "rights_notice": RIGHTS_NOTICE,
        "repositories": rows,
        "errors": errors,
        "warnings": warnings,
    }
    (OUTPUT_DIR / "project-description-audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# Project description audit",
        "",
        f"- Result: **{status}**",
        f"- Canonical descriptions checked: **{len(rows)}**",
        f"- Structural errors: **{len(errors)}**",
        f"- Live GitHub About-field warnings: **{len(warnings)}**",
        "",
        "## Canonical descriptions",
        "",
        "| Project | Live About match | Canonical description |",
        "|---|---|---|",
    ]
    for row in rows:
        live_state = (
            "unavailable"
            if row["metadata_error"]
            else "yes"
            if row["description_match"]
            else "no"
        )
        description = row["expected_description"].replace("|", "%7C")
        lines.append(f"| {row['display_name']} | {live_state} | {description} |")

    if errors:
        lines.extend(["", "## Structural errors", ""])
        lines.extend(f"- **{item['area']}:** {item['message']}" for item in errors)
    if warnings:
        lines.extend(["", "## Live metadata follow-up", ""])
        lines.extend(f"- **{item['area']}:** {item['message']}" for item in warnings)

    lines.extend(
        [
            "",
            "The source-controlled descriptions are canonical. This audit is report-only and "
            "does not change GitHub repository settings.",
            "",
            RIGHTS_NOTICE,
        ]
    )
    markdown = "\n".join(lines) + "\n"
    (OUTPUT_DIR / "project-description-audit.md").write_text(markdown, encoding="utf-8")
    print(markdown)

    summary_path = os.environ.get("GITHUB_STEP_SUMMARY", "").strip()
    if summary_path:
        try:
            with Path(summary_path).open("a", encoding="utf-8") as handle:
                handle.write(markdown)
        except OSError as exc:
            print(f"Unable to write GITHUB_STEP_SUMMARY: {exc}", file=sys.stderr)

    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
