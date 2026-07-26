#!/usr/bin/env python3
"""Run the public-claims audit with Markdown- and whitespace-normalized README matching.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import re
from typing import Any

import public_claims_audit as core

RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."


def normalize_claim_text(value: str) -> str:
    """Normalize presentation-only Markdown differences while preserving claim words."""
    text = value.replace("**", "").replace("__", "")
    return re.sub(r"\s+", " ", text).strip().lower()


def validate_readme(
    owner: str,
    record: dict[str, Any],
) -> tuple[str, list[core.Finding]]:
    repository = str(record.get("repository") or "")
    findings: list[core.Finding] = []
    try:
        text = core.fetch_readme(owner, repository)
    except Exception as exc:
        core.add(
            findings,
            "error",
            repository,
            "README",
            f"could not read main README: {type(exc).__name__}: {exc}",
        )
        return repository, findings

    normalized_readme = normalize_claim_text(text)
    for marker in record.get("readme_required_markers", []):
        normalized_marker = normalize_claim_text(str(marker))
        if normalized_marker not in normalized_readme:
            core.add(
                findings,
                "error",
                repository,
                "README",
                f"required evidence marker is missing: {marker}",
            )
    for marker in record.get("readme_forbidden_markers", []):
        normalized_marker = normalize_claim_text(str(marker))
        if normalized_marker in normalized_readme:
            core.add(
                findings,
                "error",
                repository,
                "README",
                f"retired or unsupported claim is still present: {marker}",
            )
    return repository, findings


if core.RIGHTS_NOTICE != RIGHTS_NOTICE:
    raise SystemExit("Public claims rights notice changed")

core.MAX_WORKERS = min(core.MAX_WORKERS, 3)
core.validate_readme = validate_readme


if __name__ == "__main__":
    raise SystemExit(core.main())
