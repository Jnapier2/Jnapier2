#!/usr/bin/env python3
"""Validate repository-level ownership and security controls for the public profile.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import portfolio_audit

ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = Path(os.environ.get("PORTFOLIO_AUDIT_OUTPUT_DIR", ROOT / "audit-output"))
RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."


def require_text(path: Path, markers: list[str]) -> None:
    if not path.is_file():
        raise SystemExit(
            f"Profile repository governance failure: missing {path.relative_to(ROOT)}"
        )
    text = path.read_text(encoding="utf-8")
    for marker in markers:
        if marker not in text:
            raise SystemExit(
                f"Profile repository governance failure: "
                f"{path.relative_to(ROOT)} lacks {marker!r}"
            )


def load_object(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise SystemExit(
            f"Profile repository governance failure: missing {path.relative_to(ROOT)}"
        )
    try:
        payload: Any = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(
            f"Profile repository governance failure: "
            f"{path.relative_to(ROOT)} is unreadable: {exc}"
        ) from exc
    if not isinstance(payload, dict):
        raise SystemExit(
            f"Profile repository governance failure: "
            f"{path.relative_to(ROOT)} must contain an object"
        )
    return payload


def require_dependency_ledger(path: Path) -> None:
    payload = load_object(path)
    if payload.get("schema_version") != 1:
        raise SystemExit(
            "Profile repository governance failure: dependency schema must be 1"
        )
    if payload.get("rights_notice") != RIGHTS_NOTICE:
        raise SystemExit(
            "Profile repository governance failure: dependency rights notice changed"
        )
    review_scope = payload.get("review_scope")
    if not isinstance(review_scope, str) or not review_scope.startswith(
        "All 18 public repositories"
    ):
        raise SystemExit(
            "Profile repository governance failure: dependency review scope is incomplete"
        )
    status_definitions = payload.get("status_definitions")
    if not isinstance(status_definitions, dict) or not status_definitions.get(
        "sealed_audited_release"
    ):
        raise SystemExit(
            "Profile repository governance failure: sealed-release dependency state is missing"
        )
    projects = payload.get("projects")
    if not isinstance(projects, list) or len(projects) != 18:
        raise SystemExit(
            "Profile repository governance failure: dependency project coverage must be 18"
        )
    repositories = [
        str(item.get("repository") or "")
        for item in projects
        if isinstance(item, dict)
    ]
    if len(repositories) != 18 or len(set(repositories)) != 18 or "" in repositories:
        raise SystemExit(
            "Profile repository governance failure: dependency repository coverage is invalid"
        )
    excluded_private_scope = payload.get("excluded_private_scope")
    if (
        not isinstance(excluded_private_scope, dict)
        or excluded_private_scope.get("status") != "not_part_of_public_inventory"
        or not str(excluded_private_scope.get("note") or "").strip()
    ):
        raise SystemExit(
            "Profile repository governance failure: excluded private scope is not declared"
        )


def require_dependabot_policy(
    path: Path,
    expected_public_repositories: set[str],
) -> None:
    payload = load_object(path)
    if payload.get("schema_version") != 1:
        raise SystemExit(
            "Profile repository governance failure: Dependabot policy schema must be 1"
        )
    if payload.get("rights_notice") != RIGHTS_NOTICE:
        raise SystemExit(
            "Profile repository governance failure: Dependabot rights notice changed"
        )
    if payload.get("auto_merge_policy") != "forbidden":
        raise SystemExit(
            "Profile repository governance failure: dependency auto-merge must be forbidden"
        )
    if not str(payload.get("review_rule") or "").strip():
        raise SystemExit(
            "Profile repository governance failure: dependency review rule is missing"
        )

    records = payload.get("repositories")
    if not isinstance(records, list) or not records:
        raise SystemExit(
            "Profile repository governance failure: monitored repository policy is missing"
        )
    monitored: list[str] = []
    for record in records:
        if not isinstance(record, dict):
            raise SystemExit(
                "Profile repository governance failure: monitored policy record is invalid"
            )
        repository = str(record.get("repository") or "")
        entries = record.get("entries")
        if not repository or not isinstance(entries, list) or not entries:
            raise SystemExit(
                "Profile repository governance failure: monitored policy coverage is incomplete"
            )
        monitored.append(repository)
        ecosystems: list[str] = []
        for entry in entries:
            if not isinstance(entry, dict):
                raise SystemExit(
                    "Profile repository governance failure: ecosystem policy entry is invalid"
                )
            ecosystem = str(entry.get("ecosystem") or "")
            if (
                not ecosystem
                or entry.get("directory") != "/"
                or not str(entry.get("interval") or "")
                or not isinstance(entry.get("open_pull_requests_limit"), int)
            ):
                raise SystemExit(
                    "Profile repository governance failure: ecosystem policy entry is incomplete"
                )
            ecosystems.append(ecosystem)
        if len(ecosystems) != len(set(ecosystems)):
            raise SystemExit(
                "Profile repository governance failure: duplicate ecosystem policy entry"
            )

    absent_records = payload.get("repositories_without_dependabot")
    if not isinstance(absent_records, list) or not absent_records:
        raise SystemExit(
            "Profile repository governance failure: sealed absence policy is missing"
        )
    absent: list[str] = []
    for record in absent_records:
        if not isinstance(record, dict):
            raise SystemExit(
                "Profile repository governance failure: absence policy record is invalid"
            )
        repository = str(record.get("repository") or "")
        reason = str(record.get("reason") or "")
        if not repository or not reason:
            raise SystemExit(
                "Profile repository governance failure: absence policy record is incomplete"
            )
        absent.append(repository)

    names = monitored + absent
    if len(names) != len(set(names)):
        raise SystemExit(
            "Profile repository governance failure: dependency monitoring policy overlaps"
        )
    if not set(names).issubset(expected_public_repositories):
        raise SystemExit(
            "Profile repository governance failure: dependency monitoring references unknown repositories"
        )


def verify_shared_profile_contract() -> dict[str, Any]:
    manifest = portfolio_audit.load_manifest()
    audit = portfolio_audit.Audit()
    portfolio_audit.audit_profile_readme(audit, manifest)
    if audit.errors:
        details = "; ".join(
            f"{item.area}: {item.message}" for item in audit.errors
        )
        raise SystemExit(
            "Profile repository governance failure: "
            f"shared profile contract failed: {details}"
        )
    return manifest


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
            "Kalshi 15-Minute Sell Preview",
        ],
    )
    require_text(
        ROOT / ".github" / "workflows" / "profile-contract.yml",
        [
            "dependabot-policy.json",
            "dependabot_policy_audit.py",
            "Audit per-ecosystem Dependabot policy and auto-merge prohibition",
            RIGHTS_NOTICE,
        ],
    )

    manifest = verify_shared_profile_contract()
    expected_public = {
        str(item)
        for item in manifest.get("expected_public_repositories", [])
        if str(item)
    }
    if len(expected_public) != 18:
        raise SystemExit(
            "Profile repository governance failure: public inventory contract must contain 18 repositories"
        )
    require_dependency_ledger(ROOT / ".github" / "dependency-reconciliation.json")
    require_dependabot_policy(
        ROOT / ".github" / "dependabot-policy.json",
        expected_public,
    )

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
            "dependabot_policy": "PASS",
            "dependency_auto_merge_prohibited": "PASS",
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
