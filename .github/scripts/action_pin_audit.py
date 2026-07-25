#!/usr/bin/env python3
"""Require immutable commit-SHA references in declared portfolio workflows.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / ".github" / "portfolio-manifest.json"
OUTPUT_DIR = ROOT / "audit-output"
RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
USER_AGENT = "Gateway-Portfolio-Action-Pin-Audit/1.0"
SHA40 = re.compile(r"^[0-9a-fA-F]{40}$")
USES = re.compile(r"(?m)^\s*(?:-\s*)?uses:\s*([^@\s]+)@([^\s#]+)")


def load_manifest() -> dict[str, Any]:
    data = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1:
        raise SystemExit("Unsupported portfolio manifest schema")
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
    request = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return response.read(2_000_001).decode("utf-8")
    except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, UnicodeError) as exc:
        raise RuntimeError(f"{repository}:{path}: {exc}") from exc


def audit_workflow(repository: str, path: str, text: str) -> dict[str, Any]:
    references: list[dict[str, str]] = []
    violations: list[str] = []
    for action, reference in USES.findall(text):
        item = {"action": action, "reference": reference}
        references.append(item)
        if action.startswith("./") or action.startswith("docker://"):
            continue
        if not SHA40.fullmatch(reference):
            violations.append(f"{repository}:{path}: {action}@{reference}")
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
        lines.extend([
            "Every declared external Action reference is pinned to a full 40-character commit SHA.",
        ])
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
