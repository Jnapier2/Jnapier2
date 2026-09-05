from __future__ import annotations

import ipaddress
import re


class _SecretAssignmentDetector:
    """Find credential assignments without crossing lines or flagging safe placeholders."""

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
        [ \t]*(?P<separator>[:=])[ \t]*
        """
    )
    _quoted_value = re.compile(
        r"""^(?P<value>"(?:\\.|[^"\r\n])*"|'(?:\\.|[^'\r\n])*')"""
    )
    _block_indicator = re.compile(
        r"^[|>](?:(?P<indent_first>[1-9])(?P<chomp_after>[+-])?"
        r"|(?P<chomp_first>[+-])(?P<indent_after>[1-9])?)?"
        r"[ \t]*(?:#.*)?$"
    )
    _next_field = re.compile(
        r"""^,[ \t]*(?:(?:["'][^"'\r\n]+["'])|"""
        r"""(?:[A-Za-z_][A-Za-z0-9_. -]*))[ \t]*:"""
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
    def _is_safe_token(cls, value: str, *, quoted: bool = False) -> bool:
        normalized = value.strip()
        sentinels = cls._quoted_sentinels if quoted else cls._bare_sentinels
        return normalized.casefold() in sentinels or any(
            pattern.fullmatch(normalized) for pattern in cls._placeholder_patterns
        )

    @staticmethod
    def _inside_flow_mapping(prefix: str) -> bool:
        """Return True when the key begins inside an unmatched ``{...}`` map."""
        stack: list[str] = []
        quote: str | None = None
        escaped = False
        for character in prefix:
            if quote is not None:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == quote:
                    quote = None
                continue
            if character in {'"', "'"}:
                quote = character
            elif character in "{[":
                stack.append(character)
            elif character == "}" and stack and stack[-1] == "{":
                stack.pop()
            elif character == "]" and stack and stack[-1] == "[":
                stack.pop()
        return "{" in stack

    @classmethod
    def _is_structured_tail(
        cls,
        tail: str,
        separator: str,
        *,
        flow_mapping: bool,
    ) -> bool:
        if not tail:
            return True

        # Comments require separation whitespace. An unspaced hash is literal
        # shell/YAML content and must not hide a suffix such as #hunter2.
        if tail[0] in " \t" and tail.lstrip().startswith("#"):
            return True
        normalized = tail.lstrip()
        if not normalized:
            return True
        if normalized.startswith("#") or separator != ":" or not flow_mapping:
            return False
        if re.fullmatch(r",?[ \t]*(?:#.*)?", normalized):
            return True
        if re.match(r"^[}\]][ \t]*(?:,?[ \t]*(?:#.*)?)?$", normalized):
            return True
        return bool(cls._next_field.match(normalized))

    @classmethod
    def _is_nonsecret_scalar(
        cls,
        raw_value: str,
        separator: str,
        *,
        flow_mapping: bool = False,
    ) -> bool:
        value = raw_value.strip()
        if not value or value.startswith("#"):
            return True

        quoted = cls._quoted_value.match(value)
        if quoted:
            token = quoted.group("value")
            if not cls._is_structured_tail(
                value[quoted.end() :],
                separator,
                flow_mapping=flow_mapping,
            ):
                return False
            return cls._is_safe_token(token[1:-1], quoted=True)

        value = re.sub(r"[ \t]+#.*$", "", value).strip()
        if not value:
            return True
        if cls._is_safe_token(value):
            return True

        if separator == ":" and flow_mapping:
            comma = value.find(",")
            if comma >= 0 and cls._is_structured_tail(
                value[comma:],
                separator,
                flow_mapping=True,
            ):
                return cls._is_safe_token(value[:comma])

            trimmed = value
            while trimmed.endswith(("}", "]")):
                trimmed = trimmed[:-1].rstrip()
                if cls._is_safe_token(trimmed):
                    return True

        return False

    @staticmethod
    def _indent_width(line: str) -> int:
        prefix = line[: len(line) - len(line.lstrip(" \t"))]
        return sum(4 if character == "\t" else 1 for character in prefix)

    @staticmethod
    def _column_width(prefix: str) -> int:
        return sum(4 if character == "\t" else 1 for character in prefix)

    @staticmethod
    def _is_sequence_indicator(value: str) -> bool:
        return value == "-" or value.startswith("- ")

    @classmethod
    def _continuation_line_is_nonsecret(cls, line: str) -> bool:
        value = line.strip()
        if not value or value.startswith("#"):
            return True

        # Sequence markers are structure outside block scalars. Repeated
        # markers can introduce nested sequences.
        while cls._is_sequence_indicator(value):
            if value == "-":
                return True
            value = value[1:].lstrip()
        if not value or value.startswith("#"):
            return True

        return cls._is_nonsecret_scalar(value, ":", flow_mapping=False)

    @classmethod
    def _indented_value_is_nonsecret(
        cls,
        lines: list[str],
        line_index: int,
        key_column: int,
    ) -> bool:
        """Inspect a YAML value continued onto following indented lines."""

        first_index: int | None = None
        content_indent: int | None = None
        indentless_sequence = False

        for candidate_index in range(line_index + 1, len(lines)):
            candidate = lines[candidate_index]
            if not candidate.strip():
                continue

            indent = cls._indent_width(candidate)
            stripped = candidate.lstrip(" \t")

            # Plain YAML comments are not scalar content; keep looking for the
            # first actual value line inside the same mapping scope.
            if stripped.startswith("#"):
                if indent < key_column:
                    return True
                continue

            if indent > key_column:
                first_index = candidate_index
                content_indent = indent
                break

            # YAML permits an indentless sequence as a mapping value, including
            # a bare dash whose item begins on the next line.
            if indent == key_column and cls._is_sequence_indicator(stripped):
                first_index = candidate_index
                content_indent = indent
                indentless_sequence = True
                break

            return True

        if first_index is None or content_indent is None:
            return True

        values: list[str] = []
        for candidate in lines[first_index:]:
            if not candidate.strip():
                continue

            indent = cls._indent_width(candidate)
            stripped = candidate.lstrip(" \t")

            if indentless_sequence:
                if indent < content_indent:
                    break
                if (
                    indent == content_indent
                    and not cls._is_sequence_indicator(stripped)
                ):
                    break
            elif indent < content_indent:
                break

            if stripped.startswith("#") or stripped == "-":
                continue
            values.append(stripped)

        return not values or all(
            cls._continuation_line_is_nonsecret(value) for value in values
        )

    @classmethod
    def _block_line_is_nonsecret(cls, line: str) -> bool:
        value = line.strip()
        if not value:
            return True
        quoted = cls._quoted_value.fullmatch(value)
        if quoted:
            return cls._is_safe_token(value[1:-1], quoted=True)
        return cls._is_safe_token(value)

    @classmethod
    def _block_is_nonsecret(
        cls,
        lines: list[str],
        line_index: int,
        key_column: int,
        indicator: str,
    ) -> bool:
        """Inspect only the YAML block scalar's actual content indentation."""

        indicator_match = cls._block_indicator.fullmatch(indicator.strip())
        explicit_indent: int | None = None
        if indicator_match:
            digit = (
                indicator_match.group("indent_first")
                or indicator_match.group("indent_after")
            )
            if digit:
                explicit_indent = int(digit)

        content_indent = (
            key_column + explicit_indent if explicit_indent is not None else None
        )
        first_index: int | None = None

        for candidate_index in range(line_index + 1, len(lines)):
            candidate = lines[candidate_index]
            if not candidate.strip():
                continue

            indent = cls._indent_width(candidate)
            if content_indent is None:
                if indent <= key_column:
                    return True
                content_indent = indent

            if indent < content_indent:
                return True

            first_index = candidate_index
            break

        if first_index is None or content_indent is None:
            return True

        values: list[str] = []
        for candidate in lines[first_index:]:
            if not candidate.strip():
                continue

            indent = cls._indent_width(candidate)
            if indent < content_indent:
                break
            values.append(candidate.strip())

        return not values or all(
            cls._block_line_is_nonsecret(value) for value in values
        )

    def search(self, text: str) -> re.Match[str] | None:
        lines = text.splitlines()
        for line_index, line in enumerate(lines):
            for match in self._key.finditer(line):
                value = line[match.end() :]
                separator = match.group("separator")
                key_column = self._column_width(line[: match.start()])
                flow_mapping = self._inside_flow_mapping(line[: match.start()])

                if self._block_indicator.fullmatch(value.strip()):
                    if not self._block_is_nonsecret(
                        lines,
                        line_index,
                        key_column,
                        value,
                    ):
                        return match
                elif not value.strip() or value.lstrip().startswith("#"):
                    if not self._indented_value_is_nonsecret(
                        lines,
                        line_index,
                        key_column,
                    ):
                        return match
                elif not self._is_nonsecret_scalar(
                    value,
                    separator,
                    flow_mapping=flow_mapping,
                ):
                    return match
        return None


class _IPv4AddressDetector:
    """Detect raw IPv4 addresses while excluding explicit four-part versions."""

    _candidate = re.compile(
        r"(?<![\d.])(?:25[0-5]|2[0-4]\d|1?\d?\d)"
        r"(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?!\d)(?!\.\d)"
    )
    _version_context = re.compile(
        r"(?i)(?:^|[^A-Za-z0-9])(?:v(?:ersion)?|ver|build|release)"
        r"[ \t:=_\-`*~\[({<]*$"
    )

    def search(self, text: str) -> re.Match[str] | None:
        for match in self._candidate.finditer(text):
            prefix = text[max(0, match.start() - 48) : match.start()]
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
            token = match.group(0).rstrip(".,;!?")
            if token.startswith("["):
                address = token[1 : token.index("]")].split("%", 1)[0]
            else:
                address = token.split("/", 1)[0].split("%", 1)[0]

            # Try the complete candidate first. If prose contributes one extra
            # colon (including the triple-colon case after a compressed address),
            # retry after removing exactly that punctuation character.
            candidates = [address]
            if address.endswith(":"):
                candidates.append(address[:-1])

            for candidate in candidates:
                try:
                    parsed = ipaddress.IPv6Address(candidate)
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
        'password="my pass"',
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
        'password="${TOKEN}",hunter2',
        "password=${TOKEN},hunter2",
        'password="${TOKEN}"#hunter2',
        'password="REDACTED"#hunter2',
        "password: ${TOKEN},suffix:hunter2",
        "password: |\n  hunter2",
        "password: |\n  #hunter2",
        "token: >-\n  secret",
        "- password: |\n    hunter2\n  id: 1",
        "password:\n  hunter2",
        "password:\n  - hunter2",
        "- password:\n    hunter2\n  id: 1",
        "password:\n- hunter2",
        "password:\n-\n  hunter2",
        "- password:\n  -\n    hunter2",
        "password: |2\n  hunter2",
    ),
}


PRIVATE_PATH_FIXTURES = {
    "personal_windows_path": (r"C:\Users\example-user\private-project",),
    "unix_home_path": ("/home/example-user/private-project",),
    "macos_home_path": ("/Users/example-user/private-project",),
    "raw_ipv4_address": (
        "192.0.2.42",
        "http://192.168.1.2:8080/",
        "Endpoint 192.168.1.2.",
    ),
    "raw_ipv6_address": (
        "fd00::1234",
        "2001:4860:4860::8888",
        "[fe80::1%eth0]",
        "http://[fe80::1%25eth0]:8080/",
        "Endpoint 2001:db8::1.",
        "Endpoint 2001:db8::1: the service failed",
        "Endpoint 2001:db8::: the service failed",
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
    '{"password":"${TOKEN}","id":1}',
    "password:\n  REDACTED",
    "password:\n  - ${TOKEN}",
    "- password:\n    REDACTED\n  id: 1",
    "password:\n- ${TOKEN}",
    "password:\n-\n  REDACTED",
    "- password:\n  -\n    ${TOKEN}",
    "password: |2\n  REDACTED",
    "- password: |\n    REDACTED\n   # explanatory comment\n  id: 1",
)


SAFE_ADDRESS_FIXTURES = (
    "version 1.2.3.4",
    "v1.2.3.4",
    "Version: 10.20.30.40",
    "build 1.2.3.4",
    "release_1.2.3.4",
    "api_version=1.2.3.4",
    "runtime version `1.2.3.4`",
    "version **1.2.3.4**",
    "build _1.2.3.4_",
    "runtime version (1.2.3.4)",
    "http://[::1]:8080/",
    "::",
)
