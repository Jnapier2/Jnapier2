#!/usr/bin/env python3
"""Validate repository-level ownership and security controls for the public profile.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import portfolio_audit

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "audit-output"
RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."


def require_text(path: Path, markers: list[str]) -> None:
    if not path.is_file():
        raise SystemExit(f"Profile repository governance failure: missing {path.relative_to(ROOT)}")
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            raise SystemExit(
                f"Profile repository governance failure: {path.relative_to(ROOT)} lacks {marker!r}"
            )


def require_dependency_ledger(path: Path) -> None:
    if not path.is_file():
        raise SystemExit(f"Profile repository governance failure: missing {path.relative_to(ROOT)}")
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"Profile repository governance failure: {path.relative_to(ROOT)} is unreadable: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise SystemExit(
            f"Profile repository governance failure: {path.relative_to(ROOT)} must contain an object"
        )
    if payload.get("schema_version") != 1:
        raise SystemExit("Profile repository governance failure: dependency schema must be 1")
    if payload.get("rights_notice") != RIGHTS_NOTICE:
        raise SystemExit("Profile repository governance failure: dependency rights notice changed")
    review_scope = payload.get("review_scope")
    if not isinstance(review_scope, str) or not review_scope.startswith("All 18 public repositories"):
        raise SystemExit("Profile repository governance failure: dependency review scope is incomplete")
    status_definitions = payload.get("status_definitions")
    if not isinstance(status_definitions, dict) or not status_definitions.get("sealed_audited_release"):
        raise SystemExit("Profile repository governance failure: sealed-release dependency state is missing")
    projects = payload.get("projects")
    if not isinstance(projects, list) or len(projects) != 18:
        raise SystemExit("Profile repository governance failure: dependency project coverage must be 18")
    repositories = [
        str(item.get("repository") or "")
        for item in projects
        if isinstance(item, dict)
    ]
    if len(repositories) != 18 or len(set(repositories)) != 18:
        raise SystemExit("Profile repository governance failure: dependency repository coverage is duplicated")
    private_workspaces = payload.get("private_workspaces")
    if not isinstance(private_workspaces, list) or len(private_workspaces) != 2:
        raise SystemExit("Profile repository governance failure: private workspace boundaries are incomplete")


def verify_shared_profile_contract() -> None:
    manifest = portfolio_audit.load_manifest()
    audit = portfolio_audit.Audit()
    portfolio_audit.audit_profile_readme(audit, manifest)
    if audit.errors:
        details = "; ".join(f"{item.area}: {item.message}" for item in audit.errors)
        raise SystemExit(f"Profile repository governance failure: shared profile contract failed: {details}")


def main() -> int:
    require_text(
        ROOT / "LICENSE.md",
        [
            RIGHTS_NOTICE,
            "no permission is granted",
            "Linked project repositories are governed by their own license or rights files.",
            "This notice does not create or replace a software license.",
        ],
    )
    require_text(
        ROOT / "SECURITY.md",
        [
            RIGHTS_NOTICE,
            "private vulnerability reporting",
            "Do not include vulnerability details",
            "Do not test against accounts, systems, data, or services you do not own",
        ],
    )
    require_text(
        ROOT / ".github" / "CODEOWNERS",
        [
            RIGHTS_NOTICE,
            "* @Jnapier2",
            "/README.md @Jnapier2",
            "/.github/ @Jnapier2",
            "/case-studies/ @Jnapier2",
        ],
    )
    require_text(
        ROOT / "README.md",
        [
            "Reliable Project Delivery Framework",
            "Public project release reconciliation",
            "Public dependency reconciliation",
        ],
    )
    require_text(
        ROOT / "DEPENDENCY_RECONCILIATION.md",
        [
            RIGHTS_NOTICE,
            "All 18 public repositories",
            ".github/dependency-reconciliation.json",
            "MediaTaggerBot",
            "Chicago Food Inspection Outcomes",
            "Kalshi 15m Sell Preview",
        ],
    )
    require_dependency_ledger(ROOT / ".github" / "dependency-reconciliation.json")
    verify_shared_profile_contract()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    evidence = {
        "schema_version": 1,
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "repository": "Jnapier2/Jnapier2",
        "controls": {
            "repository_rights": "PASS",
            "security_reporting": "PASS",
            "code_ownership": "PASS",
            "profile_links": "PASS",
            "release_reconciliation": "PASS",
            "dependency_reconciliation": "PASS",
            "shared_profile_contract": "PASS",
        },
        "result": "PASS",
        "rights_notice": RIGHTS_NOTICE,
    }
    (OUTPUT_DIR / "profile-repository-governance.json").write_text(
        json.dumps(evidence, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("Profile repository governance: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
