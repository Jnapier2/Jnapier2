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
    "## Evidence at a glance",
    "38,171-file media audit",
    "13,333 public inspection records",
    "26/26 control areas, 40/40 scenario simulations, and 20/20 negative/conflict checks",
    "29 branching support cases across five shifts",
    "## For hiring teams",
    "I’m open to senior roles in analytics, data governance, information management, and reliable automation.",
)

REQUIRED_STRATEGY_MARKERS = (
    "## Objectives",
    "## Benchmark index",
    "## Organic implementation",
    "## Pin strategy",
    "## Maintenance rules",
    "## Success signal",
    "https://docs.github.com/en/account-and-profile/how-tos/profile-customization/managing-your-profile-readme",
    "https://docs.github.com/en/account-and-profile/how-tos/profile-customization/pinning-items-to-your-profile",
    "https://github.com/cassidoo",
    "https://github.com/sdras",
    "https://github.com/anuraghazra",
    "https://github.com/simonw",
    "https://github.com/sindresorhus",
    "https://github.com/abhisheknaiidu/awesome-github-profile-readme",
    "dynamic third-party stat cards",
    "No proposal may auto-merge",
    RIGHTS_NOTICE,
)

FORBIDDEN_README_FRAGMENTS = (
    "github-readme-stats.vercel.app",
    "github-profile-trophy",
    "komarev.com/ghpvc",
    "visitor-badge",
    "wakatime.com/badge",
    "readme-typing-svg",
)

REQUIRED_PIN_ORDER = (
    "`botops-manager`",
    "`digital-asset-governance-case-study`",
    "`media-tagger-bot`",
    "`chicago-food-inspections-analysis`",
    "`avalon-q-supervisor`",
    "`beta-earth`",
)


def read_text(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path.relative_to(ROOT))
    return path.read_text(encoding="utf-8")


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

    for heading in ("## Evidence at a glance", "## For hiring teams"):
        count = readme.count(heading)
        if count != 1:
            errors.append(f"README.md must contain {heading!r} exactly once; found {count}")

    lower_readme = readme.lower()
    for fragment in FORBIDDEN_README_FRAGMENTS:
        if fragment.lower() in lower_readme:
            errors.append(f"README.md contains deferred external widget fragment: {fragment}")

    for marker in REQUIRED_STRATEGY_MARKERS:
        if marker not in strategy:
            errors.append(f"PROFILE_STRATEGY.md lacks required marker: {marker}")

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
        errors.append("PROFILE_STRATEGY.md must contain the canonical rights notice exactly once")

    result = "PASS" if not errors else "FAIL"
    generated_utc = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    payload = {
        "schema_version": 1,
        "generated_utc": generated_utc,
        "result": result,
        "profile_sections_checked": 2,
        "verified_evidence_markers_checked": 4,
        "benchmark_references_checked": 8,
        "pin_entries_checked": 6,
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
        "- Verified evidence markers checked: **4**",
        "- Benchmark references checked: **8**",
        "- Pin entries checked: **6**",
        "",
    ]
    if errors:
        lines.extend(["## Action required", ""])
        lines.extend(f"- {error}" for error in errors)
    else:
        lines.append(
            "The benchmark index, organic profile implementation, verified evidence, "
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
    (OUTPUT_DIR / "profile-strategy-audit.md").write_text(markdown, encoding="utf-8")
    print(markdown)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
