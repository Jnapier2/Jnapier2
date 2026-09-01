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
PROGRAM_PAGES = (
    PORTFOLIO / "data-contract-monitor.md",
    PORTFOLIO / "data-governance-lineage-portal.md",
    PORTFOLIO / "workflow-case-management-platform.md",
    PORTFOLIO / "policy-procedure-navigator.md",
    PORTFOLIO / "operations-intelligence-automation-platform.md",
    PORTFOLIO / "pc-reliability-incident-intelligence-suite.md",
)
PUBLIC_FILES = (
    PORTFOLIO / "README.md",
    *PROGRAM_PAGES,
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
        self.assertEqual(metadata["schema_version"], "1.4")
        self.assertEqual(metadata["classification"], "public")
        self.assertEqual(len(metadata["projects"]), 5)
        self.assertEqual(len(metadata["held_programs"]), 1)
        by_id = {item["id"]: item for item in metadata["projects"]}

        contract = by_id["data-contract-monitor"]
        self.assertEqual(contract["version"], "0.3.3")
        self.assertEqual(contract["build"], "DCM-0.3.3-B20260831-WINDOWSFRESHNESS1")
        self.assertEqual(contract["verification"]["managed_files_verified"], 144)
        self.assertEqual(contract["verification"]["automated_tests_passed"], 69)
        self.assertEqual(
            contract["repository_url"],
            "https://github.com/Jnapier2/data-contract-monitor",
        )
        self.assertTrue(contract["release_url"].endswith("/releases/tag/v0.3.3"))

        governance = by_id["data-governance-lineage-portal"]
        self.assertEqual(governance["version"], "0.3.0")
        self.assertEqual(governance["verification"]["managed_files_verified"], 140)
        self.assertEqual(governance["verification"]["source_tests_passed"], 84)
        self.assertEqual(governance["verification"]["typescript_build"], "pass")

        workflow = by_id["workflow-case-management-platform"]
        self.assertEqual(workflow["version"], "0.5.2")
        self.assertEqual(workflow["verification"]["automated_tests_passed"], 68)
        self.assertEqual(workflow["verification"]["managed_files_verified"], 122)

        policy = by_id["policy-procedure-navigator"]
        self.assertEqual(policy["version"], "0.3.2")
        self.assertEqual(policy["verification"]["test_cases_collected"], 67)
        self.assertEqual(policy["verification"]["tests_passed"], 66)
        self.assertEqual(
            policy["verification"]["environment_dependent_tests_skipped"], 1
        )

        operations = by_id["operations-intelligence-platform"]
        self.assertEqual(operations["version"], "0.3.1")
        self.assertEqual(operations["verification"]["http_smoke_checks"], "40/40 pass")
        self.assertEqual(operations["verification"]["managed_files_verified"], 46)

        held = metadata["held_programs"][0]
        self.assertEqual(held["id"], "pc-reliability-incident-intelligence-suite")
        self.assertEqual(held["version"], "0.3.1")
        self.assertEqual(held["automated_tests_passed"], 104)
        self.assertTrue((ROOT / held["case_study_path"]).is_file())

        collection = metadata["collection_package"]
        self.assertEqual(collection["version"], "0.3.0")
        self.assertEqual(collection["active_launchers"], 1)
        self.assertEqual(collection["unresolved_duplicate_implementation_groups"], 0)

    def test_case_studies_preserve_evidence_boundaries(self) -> None:
        contract = (PORTFOLIO / "data-contract-monitor.md").read_text(encoding="utf-8")
        governance = (PORTFOLIO / "data-governance-lineage-portal.md").read_text(
            encoding="utf-8"
        )
        workflow = (PORTFOLIO / "workflow-case-management-platform.md").read_text(
            encoding="utf-8"
        )
        policy = (PORTFOLIO / "policy-procedure-navigator.md").read_text(
            encoding="utf-8"
        )
        operations = (
            PORTFOLIO / "operations-intelligence-automation-platform.md"
        ).read_text(encoding="utf-8")
        reliability = (
            PORTFOLIO / "pc-reliability-incident-intelligence-suite.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "0.3.3 public alpha prerelease",
            "69 tests passed",
            "Historical v0.1.2 synthetic measurements",
            "not presented as v0.3.3 throughput",
            "## Evidence boundary",
        ):
            self.assertIn(marker, contract)

        for marker in (
            "Version | 0.3.0",
            "84/84 source tests",
            "140/140 managed files",
            "Public case study; proprietary implementation",
            "## Evidence boundary",
        ):
            self.assertIn(marker, governance)

        self.assertIn("68 automated tests", workflow)
        self.assertIn("122/122 managed files", workflow)
        self.assertIn("one environment-dependent symbolic-link check skipped", policy)
        self.assertIn("40/40 HTTP smoke checks", operations)
        self.assertIn("104 tests passed", reliability)
        self.assertIn("physical-Windows evidence remains open", reliability)
        self.assertNotIn("production ready", reliability.lower())

    def test_profile_links_current_program_pages(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        targets = (
            "professional-portfolio/workflow-case-management-platform.md",
            "professional-portfolio/policy-procedure-navigator.md",
            "professional-portfolio/operations-intelligence-automation-platform.md",
            "professional-portfolio/pc-reliability-incident-intelligence-suite.md",
        )
        for target in targets:
            with self.subTest(target=target):
                self.assertIn(target, readme)

    def test_public_marketing_leads_with_outcomes(self) -> None:
        overview = (PORTFOLIO / "README.md").read_text(encoding="utf-8")
        opening = overview[:800].lower()
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
