from __future__ import annotations

import unittest

try:
    from tests.public_sanitization_patterns import (
        CREDENTIAL_FIXTURES,
        SENSITIVE_PATTERNS,
    )
except ModuleNotFoundError:
    from public_sanitization_patterns import CREDENTIAL_FIXTURES, SENSITIVE_PATTERNS


class PublicSanitizationPatternTests(unittest.TestCase):
    def test_high_value_credential_formats_are_detected(self) -> None:
        for label, values in CREDENTIAL_FIXTURES.items():
            pattern = SENSITIVE_PATTERNS[label]
            for value in values:
                with self.subTest(pattern=label, value_prefix=value[:12]):
                    self.assertIsNotNone(pattern.search(value))

    def test_benign_public_language_does_not_match_credentials(self) -> None:
        safe_examples = (
            "Use a secret manager and keep credentials out of public files.",
            "The AWS access-key field is intentionally blank.",
            "GitHub tokens are never included in support exports.",
            "Slack integration remains an optional deployment responsibility.",
        )
        credential_labels = tuple(CREDENTIAL_FIXTURES)
        for text in safe_examples:
            for label in credential_labels:
                with self.subTest(text=text, pattern=label):
                    self.assertIsNone(SENSITIVE_PATTERNS[label].search(text))


if __name__ == "__main__":
    unittest.main()
