"""Public boundaries for the synthetic Account Analyst adaptation.
Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

try:
    from tests.public_sanitization_patterns import SENSITIVE_PATTERNS
except ModuleNotFoundError:
    from public_sanitization_patterns import SENSITIVE_PATTERNS

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "professional-portfolio" / "account-analytics"


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.scripts = []
        self.elements = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        self.elements.append((tag, attr))
        if "id" in attr:
            self.ids.append(attr["id"])
        if tag == "script":
            self.scripts.append(attr)


class AccountAnalyticsPrivacyTests(unittest.TestCase):
    def test_exact_public_file_surface(self):
        self.assertEqual({p.name for p in DEMO.iterdir()}, {"README.md", "index.html", "analytics.js"})
        for p in DEMO.iterdir():
            self.assertTrue(p.is_file() and not p.is_symlink())
            self.assertLess(p.stat().st_size, 20000)
            text = p.read_bytes().decode("utf-8", "strict")
            self.assertNotIn("\x00", text)
            self.assertIn("Copyright © 2026 Gateway Information Group LLC. All rights reserved.", text)

    def test_sensitive_markers_are_absent(self):
        for path in DEMO.iterdir():
            text = path.read_text(encoding="utf-8")
            for label, pattern in SENSITIVE_PATTERNS.items():
                with self.subTest(file=path.name, pattern=label):
                    self.assertIsNone(pattern.search(text))

    def test_no_network_or_storage_implementation(self):
        js = (DEMO / "analytics.js").read_text(encoding="utf-8")
        for pattern in (r"\bfetch\s*\(", r"\bXMLHttpRequest\b", r"\bWebSocket\b", r"\bsendBeacon\b",
                        r"\blocalStorage\b", r"\bsessionStorage\b", r"\bindexedDB\b", r"document\.cookie",
                        r"\binnerHTML\b", r"\beval\s*\(", r"https?://"):
            self.assertIsNone(re.search(pattern, js), pattern)

    def test_markup_loads_one_local_script(self):
        html = (DEMO / "index.html").read_text(encoding="utf-8")
        parsed = Markup(); parsed.feed(html)
        self.assertEqual(len(parsed.ids), len(set(parsed.ids)))
        self.assertEqual([s.get("src") for s in parsed.scripts], ["analytics.js"])
        self.assertTrue(all("defer" in s for s in parsed.scripts))
        self.assertFalse(any(tag in {"iframe", "form", "object", "embed", "link"} for tag, _ in parsed.elements))
        self.assertFalse(any(key.lower().startswith("on") for _, attrs in parsed.elements for key in attrs))
        self.assertIn("connect-src 'none'", html)
        self.assertIn("Entirely synthetic data.", html)
        self.assertIn('role="alert"', html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn("not a copy of the original workbook", html)

    def test_documentation_labels_new_adaptation(self):
        text = (DEMO / "README.md").read_text(encoding="utf-8")
        for marker in ("not a recovered version", "All twelve records", "Complete-record reporting is an explicit rule",
                       "Source demonstration, not a production release", "No hosted website deployment is claimed",
                       "Physical Windows, Norton", "Source-workbook layout and formula inventory are intentionally omitted"):

            self.assertIn(marker, text)
        for target in re.findall(r"\]\(([^)]+)\)", text):
            self.assertTrue((DEMO / target).resolve().is_relative_to(ROOT))
            self.assertTrue((DEMO / target).exists())


if __name__ == "__main__":
    unittest.main()
