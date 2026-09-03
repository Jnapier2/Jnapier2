from __future__ import annotations

import ipaddress
import re


class _SecretAssignmentDetector:
    """Find credential assignments without crossing lines or flagging redacted placeholders."""

    _key = re.compile(
        r"""(?ix)
        (?<![A-Za-z0-9_])
        (?P<key_quote>["']?)
        (?:
            api[_ -]?key
            | api[_ -]?secret
            | private[_ -]?key
            | wallet
            | password
            | token
            | aws[_ -]?(?:
                access[_ -]?key[_ -]?id
                | secret[_ -]?access[_ -]?key
                | session[_ -]?token
            )
            | github[_ -]?token
            | gitlab[_ -]?token
            | openai[_ -]?api[_ -]?key
            | slack[_ -]?(?:app[_ -]?token|bot[_ -]?token|user[_ -]?token)
            | npm[_ -]?token
            | pypi[_ -]?token
        )
        (?P=key_quote)
        [ \t]*[:=][ \t]*
        """
    )
    _quoted_value = re.compile(
        r"^(?P<value>\"(?:\\.|[^\"\r\n])*\"|'(?:\\.|[^'\r\n])*')"
    )
    _block_indicator = re.compile(
        r"^[|>](?:(?:[1-9][+-]?)|(?:[+-][1-9]?)|)?[ \t]*(?:#.*)?$"
    )
    _bare_sentinels = {
        "null",
        "none",
        "nil",
        "undefined",
        "~",
        "unset",
        "missing",
        "not_set",
        "not-set",
        "redacted",
        "<redacted>",
        "[redacted]",
        "***",
        "*****",
    }
    _quoted_sentinels = {
        "",
        "redacted",
        "<redacted>",
        "[redacted]",
        "***",
        "*****",
    }
    _placeholder_patterns = (
        re.compile(r"^\$\{[A-Za-z_][A-Za-z0-9_]*\}$"),
        re.compile(r"^\$[A-Za-z_][A-Za-z0-9_]*$"),
        re.compile(r"^%[A-Za-z_][A-Za-z0-9_]*%$"),
        re.compile(r"^\$?\{\{[ \t]*[A-Za-z_][A-Za-z0-9_.-]*[ \t]*\}\}$"),
        re.compile(
            r"^<(?:(?:your|insert|replace)[_-]?)?[A-Za-z_][A-Za-z0-9_.-]*>$",
            re.IGNORECASE,
        ),
    )

    @classmethod
    def _strip_scalar_tail(cls, raw_value: str) -> str:
        value = raw_value.strip()
        if not value or value.startswith("#"):
            return ""

        quoted = cls._quoted_value.match(value)
        if quoted:
            tail = value[quoted.end() :].lstrip()
            if tail and tail[0] not in ",;} ]#":
                return value
            return quoted.group("value")

        value = re.sub(r"[ \t]+#.*$", "", value).strip()
        if not value:
            return ""

        no_trailing_separator = value.rstrip(",;").rstrip()
        if any(
            pattern.fullmatch(no_trailing_separator)
            for pattern in cls._placeholder_patterns
        ):
            return no_trailing_separator

        value = re.split(r"[,;]", value, maxsplit=1)[0].rstrip()
        return value.rstrip("}]").rstrip()

    @classmethod
    def _is_nonsecret_scalar(cls, raw_value: str) -> bool:
        value = cls._strip_scalar_tail(raw_value)
        if not value:
            return True

        quoted = (
            len(value) >= 2
            and value[0] == value[-1]
            and value[0] in {'"', "'"}
        )
        if quoted:
            value = value[1:-1].strip()
            if value.casefold() in cls._quoted_sentinels:
                return True
        elif value.casefold() in cls._bare_sentinels:
            return True

        return any(pattern.fullmatch(value) for pattern in cls._placeholder_patterns)

    @staticmethod
    def _indent_width(line: str) -> int:
        prefix = line[: len(line) - len(line.lstrip(" \t"))]
        return sum(4 if character == "\t" else 1 for character in prefix)

    @classmethod
    def _block_is_nonsecret(cls, lines: list[str], line_index: int) -> bool:
        base_indent = cls._indent_width(lines[line_index])
        values: list[str] = []
        for following in lines[line_index + 1 :]:
            if not following.strip():
                continue
            if cls._indent_width(following) <= base_indent:
                break
            values.append(following.strip())

        return not values or all(cls._is_nonsecret_scalar(value) for value in values)

    def search(self, text: str) -> re.Match[str] | None:
        lines = text.splitlines()
        for line_index, line in enumerate(lines):
            for match in self._key.finditer(line):
                value = line[match.end() :]
                if self._block_indicator.fullmatch(value.strip()):
                    if not self._block_is_nonsecret(lines, line_index):
                        return match
                elif not self._is_nonsecret_scalar(value):
                    return match
        return None


class _IPv4AddressDetector:
    """Detect raw IPv4 addresses while excluding explicit four-part versions."""

    _candidate = re.compile(
        r"(?<![\d.])(?:25[0-5]|2[0-4]\d|1?\d?\d)"
        r"(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?![\d.])"
    )
    _version_context = re.compile(
        r"(?i)(?:^|[^A-Za-z0-9])(?:v(?:ersion)?|ver|build|release)[ \t:=_-]*$"
    )

    def search(self, text: str) -> re.Match[str] | None:
        for match in self._candidate.finditer(text):
            prefix = text[max(0, match.start() - 32) : match.start()]
            if self._version_context.search(prefix):
                continue
            return match
        return None


class _IPv6AddressDetector:
    """Detect raw IPv6 literals, including bracketed scoped endpoint forms."""

    _bracketed = re.compile(
        r"\[(?P<address>[0-9A-Fa-f:.]+)(?:%(?:25)?[A-Za-z0-9_.~-]+)?\]"
        r"(?::[0-9]{1,5})?"
    )
    _plain = re.compile(
        r"(?<![A-Za-z0-9])"
        r"(?P<address>(?:[0-9A-Fa-f]{0,4}:){2,}[0-9A-Fa-f:.]{0,39})"
        r"(?:%[A-Za-z0-9_.~-]+)?(?:/[0-9]{1,3})?"
        r"(?![A-Za-z0-9])"
    )

    def search(self, text: str) -> re.Match[str] | None:
        matches = sorted(
            [*self._bracketed.finditer(text), *self._plain.finditer(text)],
            key=lambda match: match.start(),
        )
        for match in matches:
            token = match.group(0)
            if token.startswith("["):
                address = token[1 : token.index("]")].split("%", 1)[0]
            else:
                address = token.split("/", 1)[0].split("%", 1)[0]
            try:
                parsed = ipaddress.IPv6Address(address)
            except ValueError:
                continue
            if parsed.is_unspecified or parsed.is_loopback:
                continue
            return match
        return None


SENSITIVE_PATTERNS = {
    "personal_windows_path": re.compile(r"[A-Za-z]:\\Users\\", re.IGNORECASE),
    "unix_home_path": re.compile(r"/home/[A-Za-z0-9._-]+", re.IGNORECASE),
    "macos_home_path": re.compile(r"/Users/[A-Za-z0-9._-]+", re.IGNORECASE),
    "private_drive_url": re.compile(r"https://(?:drive|docs)\.google\.com/", re.IGNORECASE),
    "internal_project_id": re.compile(r"\bg-p-[a-f0-9]{12,}\b", re.IGNORECASE),
    "openai_key": re.compile(r"\bsk-(?:proj-)?[A-Za-z0-9_-]{16,}\b"),
    "github_token": re.compile(
        r"\b(?:gh[pousr]_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,})\b"
    ),
    "gitlab_token": re.compile(r"\bglpat-[A-Za-z0-9_-]{20,}\b"),
    "aws_access_key": re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"),
    "google_api_key": re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"),
    "slack_token": re.compile(r"\b(?:xox[a-z]|xapp)-[A-Za-z0-9-]{10,}\b"),
    "npm_token": re.compile(r"\bnpm_[A-Za-z0-9]{20,}\b"),
    "pypi_token": re.compile(r"\bpypi-[A-Za-z0-9_-]{40,}\b"),
    "stripe_secret": re.compile(r"\b(?:sk|rk)_live_[A-Za-z0-9]{16,}\b"),
    "huggingface_token": re.compile(r"\bhf_[A-Za-z0-9]{20,}\b"),
    "private_key_header": re.compile(
        r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"
    ),
    "private_digest": re.compile(r"\b[a-fA-F0-9]{64}\b"),
    "raw_ipv4_address": _IPv4AddressDetector(),
    "raw_ipv6_address": _IPv6AddressDetector(),
    "internal_vault": re.compile(r"ChatGPT_Project_Vault", re.IGNORECASE),
    "private_prompt_file": re.compile(
        r"(?:GLOBAL_CUSTOM_INSTRUCTIONS|PASTE_THIS_IN_NEW_THREAD|PASTE_THIS_DURING_THREAD_UPGRADE)",
        re.IGNORECASE,
    ),
    "operational_secret_assignment": _SecretAssignmentDetector(),
}


CREDENTIAL_FIXTURES = {
    "openai_key": ("sk-proj-" + "A" * 24,),
    "github_token": (
        "ghp_" + "A" * 30,
        "github_pat_" + "A" * 30,
    ),
    "gitlab_token": ("glpat-" + "A" * 24,),
    "aws_access_key": (
        "AKIA" + "ABCDEFGHIJKLMNOP",
        "ASIA" + "QRSTUVWXYZABCDEF",
    ),
    "google_api_key": ("AIza" + "A" * 35,),
    "slack_token": (
        "xoxb-" + "1234567890-ABCDEFGHIJK",
        "xapp-" + "1-ABCDEFGHIJK-1234567890",
        "xoxe-" + "1-ABCDEFGHIJK-1234567890",
    ),
    "npm_token": ("npm_" + "A" * 36,),
    "pypi_token": ("pypi-" + "A" * 48,),
    "stripe_secret": ("sk_live_" + "A" * 24,),
    "huggingface_token": ("hf_" + "A" * 32,),
    "private_key_header": ("-----BEGIN PRIVATE KEY-----",),
    "operational_secret_assignment": (
        "AWS_SECRET_ACCESS_KEY=" + "A" * 40,
        "SLACK_APP_TOKEN=" + "A" * 24,
        "password=hunter2",
        "token=secret",
        "password=\"my pass\"",
        "api_key='x'",
        '"password": "hunter2"',
        "'api_key': 'x'",
        '{"token":"secret"}',
        '{"password": null, "token": "secret"}',
        "password=$PASSWORD-hunter2",
        "token=${TOKEN}secret",
        "api_key=%KEY%actual",
        'password="REDACTED"hunter2',
        'token="${TOKEN}"secret',
        "password: |\n  hunter2",
        "token: >-\n  secret",
    ),
}


PRIVATE_PATH_FIXTURES = {
    "personal_windows_path": (r"C:\Users\example-user\private-project",),
    "unix_home_path": ("/home/example-user/private-project",),
    "macos_home_path": ("/Users/example-user/private-project",),
    "raw_ipv4_address": ("192.0.2.42", "http://192.168.1.2:8080/"),
    "raw_ipv6_address": (
        "fd00::1234",
        "2001:4860:4860::8888",
        "[fe80::1%eth0]",
        "http://[fe80::1%25eth0]:8080/",
    ),
}


SAFE_ASSIGNMENT_FIXTURES = (
    "password:\nid: 1",
    '"password": null',
    "api_key: ~",
    "token: ${TOKEN}",
    "token: ${{ secrets.TOKEN }}",
    "api_key: ''",
    'password: ""',
    "password: # intentionally blank",
    "password: REDACTED",
    "password: |\n  REDACTED",
    "token: >-\n  ${TOKEN}",
    '{"password": null, "token": "${TOKEN}"}',
)


SAFE_ADDRESS_FIXTURES = (
    "version 1.2.3.4",
    "v1.2.3.4",
    "Version: 10.20.30.40",
    "build 1.2.3.4",
    "release_1.2.3.4",
    "api_version=1.2.3.4",
    "http://[::1]:8080/",
    "::",
)
