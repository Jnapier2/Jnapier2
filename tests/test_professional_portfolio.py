from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PORTFOLIO = ROOT / "professional-portfolio"
PUBLIC_FILES = (
    PORTFOLIO / "README.md",
    PORTFOLIO / "data-contract-monitor.md",
    PORTFOLIO / "data-governance-lineage-portal.md",
    PORTFOLIO / "SHOWCASE_METADATA.json",
    PORTFOLIO / "assets" / "data-contract-monitor-architecture.svg",
)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SENSITIVE_PATTERNS = {
    "personal_windows_path": re.compile(r"[A-Za-z]:\\Users\\", re.IGNORECASE),
    "unix_home_path": re.compile(r"/home/[A-Za-z0-9._-]+", re.IGNORECASE),
    "private_drive_url": re.compile(r"https://(?:drive|docs)\.google\.com/", re.IGNORECASE),
    "internal_project_id": re.compile(r"\bg-p-[a-f0-9]{12,}\b", re.IGNORECASE),
    "openai_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{16,}\b"),
    "github_token": re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
    "private_key_header": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
    "private_digest": re.compile(r"\b[a-fA-F0-9]{64}\b"),
    "operational_secret_assignment": re.compile(
        r"(?i)\b(?:api[_ -]?key|api[_ -]?secret|private[_ -]?key|wallet|password|token)\b\s*[:=]\s*\S+"
    ),
}


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
        by_id = {item["id"]: item for item in metadata["projects"]}

        contract = by_id["data-contract-monitor"]
        self.assertEqual(contract["version"], "0.1.2")
        self.assertEqual(contract["verification"]["managed_files"], 115)
        self.assertEqual(contract["verification"]["automated_tests"], 44)
        self.assertIn("Windows working save state", contract["evidence_class"])

        governance = by_id["data-governance-lineage-portal"]
        self.assertEqual(governance["version"], "0.2.1")
        self.assertEqual(governance["verification"]["managed_files"], 126)
        self.assertEqual(governance["verification"]["automated_tests"], 53)
        self.assertEqual(
            governance["verification"]["version_0_2_1_windows_bat_execution"],
            "not performed in the independent review environment",
        )

    def test_case_studies_preserve_evidence_boundaries(self) -> None:
        contract = (PORTFOLIO / "data-contract-monitor.md").read_text(
            encoding="utf-8"
        )
        governance = (
            PORTFOLIO / "data-governance-lineage-portal.md"
        ).read_text(encoding="utf-8")

        for marker in (
            "User-confirmed Windows working save state",
            "44 automated tests passed",
            "## Public boundary",
            "## Limitations",
        ):
            self.assertIn(marker, contract)

        for marker in (
            "Version 0.2.0 remains the field-confirmed Windows rollback baseline",
            "version 0.2.1 BAT was not physically executed",
            "53 automated tests",
            "## Public boundary",
            "## Limitations",
        ):
            self.assertIn(marker, governance)

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
