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
PUBLIC_VERSION = "1.7.0"
SOURCE_BASELINE = "ChatGPT New Thread Project Parameters v2.17.14"
PUBLIC_FILES = (
    ROOT / "PROJECT_FRAMEWORK.md",
    ROOT / "PROJECT_FRAMEWORK_CHECKLIST.md",
    ROOT / "PROJECT_FRAMEWORK_CHANGELOG.md",
    ROOT / "PROJECT_FRAMEWORK_METADATA.json",
)
MARKDOWN_LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")


class ProjectFrameworkTests(unittest.TestCase):
    def test_public_files_are_utf8_without_nul_bytes(self) -> None:
        for path in PUBLIC_FILES:
            with self.subTest(path=path.name):
                self.assertTrue(path.is_file())
                data = path.read_bytes()
                self.assertNotIn(b"\x00", data)
                data.decode("utf-8", errors="strict")

    def test_local_markdown_links_resolve_inside_repository(self) -> None:
        root = ROOT.resolve()
        for path in ROOT.glob("*.md"):
            text = path.read_text(encoding="utf-8")
            for raw_target in MARKDOWN_LINK.findall(text):
                target = raw_target.strip().split("#", 1)[0]
                if not target or "://" in target or target.startswith("mailto:"):
                    continue
                resolved = (path.parent / target).resolve()
                with self.subTest(path=path.name, target=target):
                    self.assertTrue(resolved == root or root in resolved.parents)
                    self.assertTrue(resolved.exists())

    def test_metadata_and_version_contract(self) -> None:
        metadata = json.loads(
            (ROOT / "PROJECT_FRAMEWORK_METADATA.json").read_text(encoding="utf-8")
        )
        self.assertEqual(metadata["asset_id"], "GIG-RPDF-PUBLIC")
        self.assertEqual(metadata["canonical_name"], "Reliable Project Delivery Framework")
        self.assertEqual(metadata["public_version"], PUBLIC_VERSION)
        self.assertEqual(metadata["source_baseline"], SOURCE_BASELINE)
        self.assertEqual(metadata["classification"], "public")
        self.assertEqual(metadata["runtime_dependencies"], [])
        self.assertFalse(metadata["verification"]["package_claim"])
        self.assertFalse(metadata["verification"]["runtime_claim"])
        self.assertEqual(len(metadata["highlights"]), 5)
        self.assertIn(
            "current consumer, protected boundary, or explicit user requirement",
            metadata["highlights"][2],
        )
        method = metadata["verification"]["method"]
        self.assertIn("documented contract presence", method)
        self.assertIn("does not validate a runtime launcher", method)
        self.assertIn("Critical exporter", method)

        framework = (ROOT / "PROJECT_FRAMEWORK.md").read_text(encoding="utf-8")
        checklist = (ROOT / "PROJECT_FRAMEWORK_CHECKLIST.md").read_text(
            encoding="utf-8"
        )
        changelog = (ROOT / "PROJECT_FRAMEWORK_CHANGELOG.md").read_text(
            encoding="utf-8"
        )
        for text in (framework, checklist, changelog):
            self.assertIn(f"v{PUBLIC_VERSION}", text)
        self.assertIn(SOURCE_BASELINE, framework)
        self.assertIn(SOURCE_BASELINE, changelog)
        self.assertIn(
            "current consumer, protected\n  boundary, or explicit user requirement",
            changelog,
        )
        self.assertNotIn(
            "**Source baseline:** ChatGPT New Thread Project Parameters v2.17.9",
            framework,
        )

    def test_framework_contains_required_public_contracts(self) -> None:
        text = (ROOT / "PROJECT_FRAMEWORK.md").read_text(encoding="utf-8")
        required = (
            "## 1. Authority, evidence, and source truth",
            "## 2. Scope, triage, and no-omission coverage",
            "## 3. One canonical identity and a lean file-and-action surface",
            "## 4. Project-local and portable operation",
            "## 6. Critical input assurance",
            "## 7. Release identity and managed-file trust before sensitive startup",
            "## 8. Independent operation across computers",
            "## 11. Privacy-conscious diagnostics and Export20",
            "## 12. Audience-facing copy and technical evidence",
            "## 13. Program-specific risk controls",
            "## 14. Verification and definition of done",
            "## Public boundary",
            "recognized → validated → normalized → mapped → exercised → confirmed",
            "one BAT/CMD filename and one authoritative backend",
            "minimal crash capsule",
            "one isolated full Export20 attempt",
            "does not prompt, recurse, rescan the project",
            "Static documentation tests prove only the documented contract",
        )
        for marker in required:
            self.assertIn(marker, text)

    def test_checklist_contains_release_and_publication_boundaries(self) -> None:
        text = (ROOT / "PROJECT_FRAMEWORK_CHECKLIST.md").read_text(
            encoding="utf-8"
        )
        required = (
            "one BAT/CMD filename and one authoritative backend",
            "current consumer, protected boundary, or explicit user requirement",
            "unexpected duplicate launchers",
            "minimal crash capsule atomically",
            "Attempt only one isolated full Export20",
            "Never prompt, recurse, rescan, rehash managed release files",
            "Lead public copy with the audience, problem, outcome, practical value",
            "Verify every public claim against current lifecycle evidence",
            "Treat static documentation checks as documentation evidence, not runtime proof",
        )
        for marker in required:
            self.assertIn(marker, text)

    def test_public_files_contain_no_sensitive_residue(self) -> None:
        for path in PUBLIC_FILES:
            text = path.read_text(encoding="utf-8")
            for label, pattern in SENSITIVE_PATTERNS.items():
                with self.subTest(path=path.name, pattern=label):
                    self.assertIsNone(pattern.search(text))

    def test_rights_notice_is_present(self) -> None:
        notice = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
        for path in PUBLIC_FILES:
            with self.subTest(path=path.name):
                self.assertIn(notice, path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
