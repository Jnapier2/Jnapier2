from __future__ import annotations

import unittest

try:
    from tests.public_sanitization_patterns import (
        CREDENTIAL_FIXTURES,
        PRIVATE_PATH_FIXTURES,
        SAFE_ADDRESS_FIXTURES,
        SAFE_ASSIGNMENT_FIXTURES,
        SENSITIVE_PATTERNS,
    )
except ModuleNotFoundError:
    from public_sanitization_patterns import (
        CREDENTIAL_FIXTURES,
        PRIVATE_PATH_FIXTURES,
        SAFE_ADDRESS_FIXTURES,
        SAFE_ASSIGNMENT_FIXTURES,
        SENSITIVE_PATTERNS,
    )


class PublicSanitizationPatternTests(unittest.TestCase):
    def test_high_value_credential_formats_are_detected(self) -> None:
        for label, values in CREDENTIAL_FIXTURES.items():
            pattern = SENSITIVE_PATTERNS[label]
            for value in values:
                with self.subTest(pattern=label, value_prefix=value[:12]):
                    self.assertIsNotNone(pattern.search(value))

    def test_private_path_and_address_formats_are_detected(self) -> None:
        for label, values in PRIVATE_PATH_FIXTURES.items():
            pattern = SENSITIVE_PATTERNS[label]
            for value in values:
                with self.subTest(pattern=label, value=value):
                    self.assertIsNotNone(pattern.search(value))

    def test_empty_placeholder_and_redacted_assignments_do_not_match(self) -> None:
        pattern = SENSITIVE_PATTERNS["operational_secret_assignment"]
        for value in SAFE_ASSIGNMENT_FIXTURES:
            with self.subTest(value=value):
                self.assertIsNone(pattern.search(value))

    def test_explicit_versions_and_loopback_ipv6_do_not_match_addresses(self) -> None:
        address_patterns = (
            SENSITIVE_PATTERNS["raw_ipv4_address"],
            SENSITIVE_PATTERNS["raw_ipv6_address"],
        )
        for value in SAFE_ADDRESS_FIXTURES:
            for pattern in address_patterns:
                with self.subTest(value=value, pattern=type(pattern).__name__):
                    self.assertIsNone(pattern.search(value))

    def test_benign_public_language_does_not_match_credentials(self) -> None:
        safe_examples = (
            "Use a secret manager and keep credentials out of public files.",
            "The AWS access-key field is intentionally blank.",
            "GitHub tokens are never included in support exports.",
            "Slack integration remains an optional deployment responsibility.",
            "Passwords must never be committed.",
            "The example uses a loopback endpoint without publishing an address.",
        )
        credential_labels = tuple(CREDENTIAL_FIXTURES)
        for text in safe_examples:
            for label in credential_labels:
                with self.subTest(text=text, pattern=label):
                    self.assertIsNone(SENSITIVE_PATTERNS[label].search(text))


if __name__ == "__main__":
    unittest.main()
