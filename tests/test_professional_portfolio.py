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
DEVELOPMENT_PAGES = (
    PORTFOLIO / "workflow-case-management-platform.md",
    PORTFOLIO / "policy-procedure-navigator.md",
    PORTFOLIO / "pc-reliability-incident-intelligence-suite.md",
    PORTFOLIO / "operations-intelligence-automation-platform.md",
)
DEVELOPMENT_PROFILE_LINKS = (
    (
        "Workflow and Case Management Platform",
        "professional-portfolio/workflow-case-management-platform.md",
    ),
    (
        "Policy and Procedure Navigator",
        "professional-portfolio/policy-procedure-navigator.md",
    ),
    (
        "PC Reliability & Incident Intelligence Suite",
        "professional-portfolio/pc-reliability-incident-intelligence-suite.md",
    ),
    (
        "Operations Intelligence & Automation Platform",
        "professional-portfolio/operations-intelligence-automation-platform.md",
    ),
)
PUBLIC_FILES = (
    PORTFOLIO / "README.md",
    PORTFOLIO / "data-contract-monitor.md",
    PORTFOLIO / "data-governance-lineage-portal.md",
    *DEVELOPMENT_PAGES,
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
        self.assertEqual(metadata["schema_version"], "1.3")
        self.assertEqual(metadata["classification"], "public")
        self.assertEqual(len(metadata["projects"]), 2)
        self.assertEqual(len(metadata["development_programs"]), 4)
        by_id = {item["id"]: item for item in metadata["projects"]}

        contract = by_id["data-contract-monitor"]
        self.assertEqual(contract["version"], "0.2.2")
        self.assertEqual(contract["build"], "DCM-0.2.2-B20260829-WINDOWS1")
        self.assertEqual(contract["verification"]["managed_files"], 132)
        self.assertEqual(contract["verification"]["automated_tests"], 72)
        self.assertEqual(
            contract["repository_url"],
            "https://github.com/Jnapier2/data-contract-monitor",
        )
        self.assertTrue(contract["release_url"].endswith("/releases/tag/v0.2.2"))
        self.assertEqual(
            contract["verification"]["synthetic_benchmark"]["source_version"],
            "0.1.2",
        )
        self.assertEqual(
            contract["verification"]["synthetic_benchmark"][
                "packaged_median_seconds"
            ],
            0.474686,
        )
        self.assertEqual(
            contract["verification"]["synthetic_benchmark"][
                "fresh_review_median_seconds"
            ],
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

        development = {
            item["id"]: item for item in metadata["development_programs"]
        }
        self.assertEqual(
            set(development),
            {
                "workflow-case-management-platform",
                "policy-procedure-navigator",
                "pc-reliability-incident-intelligence-suite",
                "operations-intelligence-automation-platform",
            },
        )
        for item in development.values():
            self.assertEqual(item["status"], "development-case-study")
            self.assertTrue((ROOT / item["case_study_path"]).is_file())
            self.assertTrue(item["required_gate"])

        workflow = development["workflow-case-management-platform"]
        self.assertEqual(workflow["version"], "0.4.1")
        self.assertEqual(workflow["build"], "WCM-B006")
        self.assertEqual(workflow["verification"]["active_bat_cmd_launchers"], 1)
        self.assertEqual(workflow["verification"]["soak_fault_cases"], 120)
        self.assertEqual(workflow["verification"]["soak_fault_workers"], 8)

        policy = development["policy-procedure-navigator"]
        self.assertEqual(policy["version"], "0.3.2")
        self.assertEqual(
            policy["build"], "PP-GKWA-0.3.2-B20260831-EXPORTENTRY1"
        )
        self.assertEqual(policy["verification"]["distribution_files"], 92)
        self.assertEqual(policy["verification"]["managed_identity"], "80/80 pass")
        self.assertEqual(policy["verification"]["automated_tests"], "67/67 pass")
        self.assertEqual(
            policy["verification"]["synthetic_golden_evaluations"], "5/5 pass"
        )
        self.assertEqual(policy["verification"]["doctor"], "ready")
        self.assertEqual(
            policy["verification"]["unresolved_exact_duplicate_groups"], 0
        )

        reliability = development[
            "pc-reliability-incident-intelligence-suite"
        ]
        self.assertEqual(reliability["version"], "0.2.2")
        self.assertEqual(reliability["build"], "PCRIIS-0.2.2-B20260831-01")
        self.assertEqual(reliability["verification"]["automated_tests"], "83/83 pass")
        self.assertEqual(
            reliability["verification"]["managed_runtime_identity"], "94/94 pass"
        )
        self.assertEqual(reliability["verification"]["active_bat_cmd_launchers"], 1)
        self.assertEqual(
            reliability["verification"]["unresolved_exact_duplicate_groups"], 0
        )
        self.assertEqual(
            reliability["verification"]["simulated_critical_export_items"], 20
        )

        operations = development["operations-intelligence-automation-platform"]
        self.assertEqual(operations["version"], "0.2.1")
        self.assertEqual(
            operations["build"], "OIAP-0.2.1-20260831-FIELDEVIDENCE1"
        )
        self.assertEqual(operations["verification"]["archive_entries"], 97)
        self.assertEqual(operations["verification"]["indexed_source_files"], 93)
        self.assertEqual(operations["verification"]["static_site_entries"], 23)
        self.assertEqual(
            operations["verification"]["application_security_tests"], "26/26 pass"
        )
        self.assertEqual(
            operations["verification"]["platform_tests"], "24/24 pass"
        )

        collection = metadata["collection_package"]
        self.assertEqual(collection["version"], "0.3.0")
        self.assertEqual(collection["archive_entries"], 112)
        self.assertEqual(collection["active_launchers"], 1)
        self.assertEqual(collection["intentional_duplicate_groups"], 7)
        self.assertEqual(
            collection["unresolved_duplicate_implementation_groups"], 0
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

    def test_development_pages_are_truthfully_labeled_and_current(self) -> None:
        for path in DEVELOPMENT_PAGES:
            text = path.read_text(encoding="utf-8")
            lower = text.lower()
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn("development case study", lower)
                self.assertIn("operational source", lower)
                self.assertIn("not published", lower)
                self.assertIn("## current evidence status", lower)
                self.assertIn("## public boundary", lower)
                self.assertIn("## limitations", lower)
                self.assertRegex(lower, r"\bcannot\b")
                self.assertNotIn("production ready", lower)
                self.assertNotIn("fully verified release", lower)

        workflow = (PORTFOLIO / "workflow-case-management-platform.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Version 0.4.1 / `WCM-B006`", workflow)
        self.assertIn("Version 0.3.1 / `WCM-B004`", workflow)
        self.assertIn("120 unique cases across eight workers", workflow)

        policy = (PORTFOLIO / "policy-procedure-navigator.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("Version 0.3.2", policy)
        self.assertIn("80/80 managed identity checks", policy)
        self.assertIn("67/67 automated tests", policy)
        self.assertIn("5/5 synthetic golden evaluations", policy)
        self.assertIn("| Doctor | Ready in the reviewed package |", policy)

        reliability = (
            PORTFOLIO / "pc-reliability-incident-intelligence-suite.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Version 0.2.2", reliability)
        self.assertIn("83/83 automated tests", reliability)
        self.assertIn("94/94 managed runtime-identity checks", reliability)
        self.assertIn("Exactly one BAT/CMD launcher", reliability)
        self.assertIn("simulated Critical export", reliability)

        operations = (
            PORTFOLIO / "operations-intelligence-automation-platform.md"
        ).read_text(encoding="utf-8")
        self.assertIn("Version 0.2.1", operations)
        self.assertIn("97 archive entries", operations)
        self.assertIn("26/26 application and security tests", operations)
        self.assertIn("24/24 platform tests", operations)
        self.assertIn("rather than a Windows/Norton-confirmed public release", operations)

        overview = (PORTFOLIO / "README.md").read_text(encoding="utf-8")
        self.assertIn("Doctor readiness", overview)
        self.assertIn("a simulated bounded Critical export", overview)

    def test_profile_labels_every_development_program(self) -> None:
        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        for display_name, target in DEVELOPMENT_PROFILE_LINKS:
            marker = (
                f"**[{display_name}]({target})** — **Development case study:**"
            )
            with self.subTest(program=display_name):
                self.assertIn(marker, readme)

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
        notice = (
            "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
        )
        for path in PUBLIC_FILES[:-1]:
            with self.subTest(path=path.relative_to(ROOT)):
                self.assertIn(notice, path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
