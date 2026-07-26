#!/usr/bin/env python3
"""Require immutable commit-SHA references in declared portfolio workflows.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import json
import os
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / ".github" / "portfolio-manifest.json"
OUTPUT_DIR = ROOT / "audit-output"
RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
USER_AGENT = "Gateway-Portfolio-Action-Pin-Audit/1.1"
HTTP_TIMEOUT_SECONDS = 20
HTTP_ATTEMPTS = 3
MAX_WORKFLOW_BYTES = 2_000_000
SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")
USES_LINE = re.compile(r"(?m)^\s*(?:-\s*)?uses:\s*([^#\r\n]+?)(?:\s+#.*)?$")


def load_manifest() -> dict[str, Any]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise SystemExit("Unsupported portfolio manifest schema")
    if data.get("rights_notice") != RIGHTS_NOTICE:
        raise SystemExit("Portfolio manifest rights notice is missing or changed")
    return data


def fetch_workflow(owner: str, repository: str, path: str) -> str:
    quoted_path = "/".join(urllib.parse.quote(part, safe="") for part in path.split("/"))
    url = (
        f"https://api.github.com/repos/{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(repository, safe='')}/contents/{quoted_path}?ref=main"
    )
    headers = {
        "Accept": "application/vnd.github.raw+json",
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
                data = response.read(MAX_WORKFLOW_BYTES + 1)
            if len(data) > MAX_WORKFLOW_BYTES:
                raise ValueError(f"workflow exceeds {MAX_WORKFLOW_BYTES} bytes")
            return data.decode("utf-8")
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
    raise RuntimeError(f"{repository}:{path}: {last_error}")


def parse_uses_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1].strip()
    return value


def audit_workflow(repository: str, path: str, text: str) -> dict[str, Any]:
    references: list[dict[str, str]] = []
    violations: list[str] = []

    for raw_value in USES_LINE.findall(text):
        value = parse_uses_value(raw_value)
        if value.startswith("./"):
            references.append({"action": value, "reference": "local"})
            continue
        if value.startswith("docker://"):
            references.append({"action": value, "reference": "container"})
            continue
        if "@" not in value:
            references.append({"action": value, "reference": ""})
            violations.append(f"{repository}:{path}: malformed uses value {value!r}")
            continue

        action, reference = value.rsplit("@", 1)
        action = action.strip()
        reference = reference.strip()
        references.append({"action": action, "reference": reference})
        if not action or not SHA40.fullmatch(reference):
            violations.append(f"{repository}:{path}: {action or '(missing action)'}@{reference}")

    if not references:
        violations.append(f"{repository}:{path}: no Action references found")
    return {
        "repository": repository,
        "workflow": path,
        "references": references,
        "violations": violations,
    }


def main() -> int:
    manifest = load_manifest()
    owner = str(manifest["owner"])
    targets = [
        (str(item["name"]), str(item["ci_path"]))
        for item in manifest["repositories"]
    ]
    targets.append((str(manifest["profile_repository"]), ".github/workflows/profile-contract.yml"))

    results: list[dict[str, Any]] = []
    errors: list[str] = []
    for repository, path in sorted(set(targets)):
        try:
            workflow = fetch_workflow(owner, repository, path)
            result = audit_workflow(repository, path, workflow)
        except Exception as exc:
            result = {
                "repository": repository,
                "workflow": path,
                "references": [],
                "violations": [str(exc)],
            }
        results.append(result)
        errors.extend(result["violations"])

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    report = {
        "schema_version": 1,
        "owner": owner,
        "rights_notice": RIGHTS_NOTICE,
        "workflow_count": len(results),
        "status": "PASS" if not errors else "ACTION_NEEDED",
        "violations": errors,
        "workflows": results,
    }
    (OUTPUT_DIR / "action-pin-audit.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# GitHub Action pin audit",
        "",
        f"Status: **{report['status']}**",
        f"Workflows checked: **{len(results)}**",
        f"Violations: **{len(errors)}**",
        "",
    ]
    if errors:
        lines.extend(["## Action required", ""] + [f"- `{item}`" for item in errors])
    else:
        lines.append("Every declared external Action reference is pinned to a full 40-character commit SHA.")
    lines.extend(["", RIGHTS_NOTICE, ""])
    (OUTPUT_DIR / "action-pin-audit.md").write_text("\n".join(lines), encoding="utf-8")

    if errors:
        for item in errors:
            print(f"[ACTION] {item}")
        return 1
    print(f"[PASS] {len(results)} declared workflows use immutable Action commit references")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
