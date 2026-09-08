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
PUBLIC_VERSION = "1.8.0"
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
        self.assertEqual(metadata["classification"], "public")
        self.assertEqual(metadata["runtime_dependencies"], [])
        self.assertFalse(metadata["verification"]["package_claim"])
        self.assertFalse(metadata["verification"]["runtime_claim"])
        self.assertEqual(len(metadata["highlights"]), 5)
        self.assertEqual(metadata["artifact_type"], "documentation-overview")
        self.assertEqual(set(metadata["files"]), {path.name for path in PUBLIC_FILES})
        self.assertNotIn("source_baseline", metadata)
        for path in PUBLIC_FILES[:3]:
            self.assertIn(f"v{PUBLIC_VERSION}", path.read_text(encoding="utf-8"))

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
