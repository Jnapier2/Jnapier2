from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

try:
    from tests.public_sanitization_patterns import SENSITIVE_PATTERNS
except ModuleNotFoundError:
    from public_sanitization_patterns import SENSITIVE_PATTERNS


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT / "professional-portfolio"
PUBLIC_FILES = (
    PORTFOLIO / "README.md",
    PORTFOLIO / "data-contract-monitor.md",
    PORTFOLIO / "data-governance-lineage-portal.md",
    PORTFOLIO / "SHOWCASE_METADATA.json",
    PORTFOLIO / "evidence" / "data-contract-monitor-benchmark-review.json",
    PORTFOLIO / "assets" / "data-contract-monitor-architecture.svg",
)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


class ProfessionalPortfolioTests(unittest.TestCase):
    def test_files_are_strict_utf8_without_nul_bytes(self) -> None:
        for path in PUBLIC_FILES:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertTrue(path.is_file())
                data = path.read_bytes()
                self.assertNotIn(b"\x00", data)
                data.decode("utf-8", errors="strict")

    def test_local_markdown_links_resolve_inside_repository(self) -> None:
        root = ROOT.resolve()
        paths = [ROOT / "README.md", *PORTFOLIO.glob("*.md")]
        for path in paths:
            text = path.read_text(encoding="utf-8")
            for raw_target in MARKDOWN_LINK.findall(text):
                target = raw_target.strip().split("#", 1)[0]
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                resolved = (path.parent / target).resolve()
                with self.subTest(path=path.relative_to(ROOT), target=target):
                    self.assertTrue(resolved == root or root in resolved.parents)
                    self.assertTrue(resolved.exists())

    def test_metadata_matches_public_claims(self) -> None:
        metadata = json.loads(
            (PORTFOLIO / "SHOWCASE_METADATA.json").read_text(encoding="utf-8")
        )
        self.assertEqual(metadata["classification"], "public")
        self.assertEqual(len(metadata["projects"]), 2)
        self.assertEqual(len(metadata["development_programs"]), 4)
        by_id = {item["id"]: item for item in metadata["projects"]}

        contract = by_id["data-contract-monitor"]
        self.assertEqual(contract["version"], "0.2.2")
        self.assertEqual(contract["build"], "DCM-0.2.2-B20260829-WINDOWS1")
        self.assertEqual(contract["verification"]["managed_files"], 132)
        self.assertEqual(contract["verification"]["automated_tests"], 72)
        self.assertEqual(contract["repository_url"], "https://github.com/Jnapier2/data-contract-monitor")
        self.assertTrue(contract["release_url"].endswith("/releases/tag/v0.2.2"))
        self.assertEqual(contract["verification"]["synthetic_benchmark"]["source_version"], "0.1.2")
        self.assertEqual(
            contract["verification"]["synthetic_benchmark"]["packaged_median_seconds"],
            0.474686,
        )
        self.assertEqual(
            contract["verification"]["synthetic_benchmark"]["fresh_review_median_seconds"],
            0.588982,
        )
        self.assertIn("public alpha", contract["evidence_class"])

        governance = by_id["data-governance-lineage-portal"]
        self.assertEqual(governance["version"], "0.2.1")
        self.assertEqual(governance["verification"]["managed_files"], 126)
        self.assertEqual(governance["verification"]["automated_tests"], 53)
        self.assertEqual(
            governance["verification"]["exact_artifact_startup"],
            "pass in the independent review environment",
        )
        self.assertIn(
            "not included",
            governance["verification"]["frontend_toolchain_lock"],
        )
        self.assertEqual(
            governance["verification"]["version_0_2_1_windows_bat_execution"],
            "not performed through Windows cmd.exe in the independent review environment",
        )

    def test_case_studies_preserve_evidence_boundaries(self) -> None:
        contract = (PORTFOLIO / "data-contract-monitor.md").read_text(
            encoding="utf-8"
        )
        governance = (
            PORTFOLIO / "data-governance-lineage-portal.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "0.2.2 — public alpha prerelease",
            "72 automated tests passed",
            "0.475-second packaged median",
            "0.589-second independent rerun median",
            "historical local measurements, not v0.2.2 performance claims",
            "## Public boundary",
            "## Limitations",
        ):
            self.assertIn(marker, contract)

        for marker in (
            "Version 0.2.0 remains the field-confirmed Windows rollback baseline",
            "exact v0.2.1 artifact reached a healthy state",
            "does not include a package lock",
            "53 automated tests",
            "## Public boundary",
            "## Limitations",
        ):
            self.assertIn(marker, governance)

    def test_public_marketing_leads_with_outcomes(self) -> None:
        overview = (PORTFOLIO / "README.md").read_text(encoding="utf-8")
        opening = overview[:700].lower()
        self.assertIn("practical tools", opening)
        self.assertNotIn("chatgpt", opening)
        self.assertNotIn("prompt", opening)
        self.assertNotIn("backend strategy", opening)
        self.assertNotIn("tool orchestration", opening)

    def test_public_files_contain_no_sensitive_residue(self) -> None:
        for path in PUBLIC_FILES:
            text = path.read_text(encoding="utf-8")
            for label, pattern in SENSITIVE_PATTERNS.items():
                with self.subTest(path=path.relative_to(ROOT), pattern=label):
                    self.assertIsNone(pattern.search(text))

    def test_rights_notice_is_present(self) -> None:
        notice = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
        for path in PUBLIC_FILES[:-1]:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn(notice, path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
