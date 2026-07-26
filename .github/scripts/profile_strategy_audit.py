#!/usr/bin/env python3
"""Validate the benchmarked GitHub profile strategy and public implementation.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
README_PATH = ROOT / "README.md"
STRATEGY_PATH = ROOT / "PROFILE_STRATEGY.md"
OUTPUT_DIR = ROOT / "audit-output"
RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."

REQUIRED_README_MARKERS = (
    "**Current focus:** Building local-first tools and data systems",
    "## Selected evidence, with context",
    "These are not popularity metrics. Each figure is publicly traceable",
    "[Definitions, sources, limitations, and plain-language explanations]"
    "(PROFILE_STRATEGY.md#evidence-definitions)",
    "Uncertain or preservation-sensitive files remain visible for review instead of being forced into a match.",
    "## For hiring teams",
    "I’m open to senior roles in analytics, data governance, information management, and reliable automation.",
)

REQUIRED_README_ROWS = (
    "| **13,333 public inspection records across three Chicago ZIP codes** | "
    "One row is an inspection, not a restaurant; the study covers 2010–2018 | "
    "Shows reproducible analysis and careful separation of inspection outcomes from facility-risk classification |",
    "| **29 authored cases across five shifts** | "
    "Every case participates in branching state and a full-campaign acceptance test | "
    "Shows product scope, persistent state, accessible interaction, and end-to-end testing |",
    "| **17 public projects reconciled to exact GitHub source** | "
    "Each ledger entry is tied to the version and reviewed default-branch commit actually present | "
    "Shows portfolio-wide version governance and avoids presenting older code as a newer build |",
)

REQUIRED_STRATEGY_MARKERS = (
    "## Objectives",
    "## Benchmark index",
    "## Organic implementation",
    "## Evidence policy",
    "## Evidence definitions",
    "## Pin strategy",
    "## Maintenance rules",
    "## Success signal",
    "A figure belongs on the profile only when all five conditions are met:",
    "Numbers are not included merely because quantified profiles are fashionable.",
    "Private MediaTagger library and outcome totals were removed from the profile",
    "### 13,333 public inspection records across three Chicago ZIP codes",
    "### 29 authored cases across five shifts",
    "### 17 public projects reconciled to exact GitHub source",
    "One row is an inspection, not a unique restaurant.",
    "The figure describes authored product content.",
    "The figure demonstrates portfolio governance.",
    "https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme",
    "https://docs.github.com/en/account-and-profile/how-tos/profile-customization/pinning-items-to-your-profile",
    "https://github.com/cassidoo",
    "https://github.com/sdras",
    "https://github.com/anuraghazra",
    "https://github.com/simonw",
    "https://github.com/sindresorhus",
    "https://github.com/abhisheknaiidu/awesome-github-profile-readme",
    "https://github.com/Jnapier2/chicago-food-inspections-analysis",
    "https://github.com/Jnapier2/inbox-from-hell",
    ".github/release-reconciliation.json",
    "dynamic third-party stat cards",
    RIGHTS_NOTICE,
)

FORBIDDEN_README_FRAGMENTS = (
    "github-readme-stats.vercel.app",
    "github-profile-trophy",
    "komarev.com/ghpvc",
    "visitor-badge",
    "wakatime.com/badge",
    "readme-typing-svg",
    "## Evidence at a glance",
    "38,171-file",
    "838 verified or already-current outcomes",
    "26/26 control areas",
)

FORBIDDEN_STRATEGY_FRAGMENTS = (
    "38,171-file",
    "838 verified or already-current outcomes",
)

REQUIRED_PIN_ORDER = (
    "`botops-manager`",
    "`digital-asset-governance-case-study`",
    "`media-tagger-bot`",
    "`chicago-food-inspections-analysis`",
    "`avalon-q-supervisor`",
    "`beta-earth`",
)

EVIDENCE_DEFINITION_HEADINGS = (
    "### 13,333 public inspection records across three Chicago ZIP codes",
    "### 29 authored cases across five shifts",
    "### 17 public projects reconciled to exact GitHub source",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path.relative_to(ROOT))
    return path.read_text(encoding="utf-8")


def require_exactly_once(text: str, marker: str, area: str, errors: list[str]) -> None:
    count = text.count(marker)
    if count != 1:
        errors.append(f"{area} must contain {marker!r} exactly once; found {count}")


def main() -> int:
    errors: list[str] = []
    try:
        readme = read_text(README_PATH)
        strategy = read_text(STRATEGY_PATH)
    except (OSError, UnicodeError) as exc:
        errors.append(f"required profile file is unreadable: {exc}")
        readme = ""
        strategy = ""

    for marker in REQUIRED_README_MARKERS:
        if marker not in readme:
            errors.append(f"README.md lacks required profile marker: {marker}")

    for row in REQUIRED_README_ROWS:
        require_exactly_once(readme, row, "README.md", errors)

    for heading in ("## Selected evidence, with context", "## For hiring teams"):
        require_exactly_once(readme, heading, "README.md", errors)

    lower_readme = readme.lower()
    for fragment in FORBIDDEN_README_FRAGMENTS:
        if fragment.lower() in lower_readme:
            errors.append(f"README.md contains retired or deferred fragment: {fragment}")

    for marker in REQUIRED_STRATEGY_MARKERS:
        if marker not in strategy:
            errors.append(f"PROFILE_STRATEGY.md lacks required marker: {marker}")

    for heading in EVIDENCE_DEFINITION_HEADINGS:
        require_exactly_once(strategy, heading, "PROFILE_STRATEGY.md", errors)

    if strategy.count("- **Plain-language explanation:**") != 3:
        errors.append(
            "PROFILE_STRATEGY.md must contain exactly three plain-language evidence explanations"
        )
    if strategy.count("- **Limitation:**") != 3:
        errors.append(
            "PROFILE_STRATEGY.md must contain exactly three evidence limitations"
        )

    lower_strategy = strategy.lower()
    for fragment in FORBIDDEN_STRATEGY_FRAGMENTS:
        if fragment.lower() in lower_strategy:
            errors.append(
                f"PROFILE_STRATEGY.md contains a retired private aggregate: {fragment}"
            )

    positions: list[int] = []
    for marker in REQUIRED_PIN_ORDER:
        position = strategy.find(marker)
        if position < 0:
            errors.append(f"PROFILE_STRATEGY.md lacks pin entry: {marker}")
        else:
            positions.append(position)
    if len(positions) == len(REQUIRED_PIN_ORDER) and positions != sorted(positions):
        errors.append("PROFILE_STRATEGY.md pin order has drifted")

    if strategy.count(RIGHTS_NOTICE) != 1:
        errors.append(
            "PROFILE_STRATEGY.md must contain the canonical rights notice exactly once"
        )

    result = "PASS" if not errors else "FAIL"
    generated_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    payload = {
        "schema_version": 1,
        "generated_utc": generated_utc,
        "result": result,
        "profile_sections_checked": 2,
        "public_evidence_rows_checked": len(REQUIRED_README_ROWS),
        "evidence_definitions_checked": len(EVIDENCE_DEFINITION_HEADINGS),
        "benchmark_references_checked": 8,
        "pin_entries_checked": len(REQUIRED_PIN_ORDER),
        "private_aggregate_policy": "excluded from recruiter-facing profile copy",
        "external_widget_policy": "deferred unless owned, bounded, and professionally useful",
        "errors": errors,
        "rights_notice": RIGHTS_NOTICE,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUTPUT_DIR / "profile-strategy-audit.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# GitHub profile strategy audit",
        "",
        f"- Result: **{result}**",
        "- Public profile sections checked: **2**",
        f"- Contextualized evidence rows checked: **{len(REQUIRED_README_ROWS)}**",
        f"- Evidence definitions checked: **{len(EVIDENCE_DEFINITION_HEADINGS)}**",
        "- Benchmark references checked: **8**",
        f"- Pin entries checked: **{len(REQUIRED_PIN_ORDER)}**",
        "- Private aggregate policy: **excluded from recruiter-facing profile copy**",
        "",
    ]
    if errors:
        lines.extend(["## Action required", ""])
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append(
            "The benchmark index, contextualized public evidence, source definitions, "
            "recruiter path, pin strategy, and external-widget boundary are intact."
        )
    lines.extend(
        [
            "",
            RIGHTS_NOTICE,
            "",
            "This notice does not replace or infer a software license. "
            "Third-party components and referenced profiles retain their respective "
            "notices, licenses, and copyrights.",
            "",
        ]
    )
    markdown = "\n".join(lines)
    (OUTPUT_DIR / "profile-strategy-audit.md").write_text(
        markdown,
        encoding="utf-8",
    )
    print(markdown)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
