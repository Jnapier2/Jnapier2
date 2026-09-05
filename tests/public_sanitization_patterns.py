from __future__ import annotations

import ipaddress
import re


class _SecretAssignmentDetector:
    """Detect credential assignments while accepting only explicit safe placeholders."""

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
    _bare_sentinels = {
        "null", "none", "nil", "undefined", "~", "unset", "missing",
        "not_set", "not-set", "redacted", "<redacted>", "[redacted]",
        "***", "*****",
    }
    _quoted_sentinels = {
        "", "redacted", "<redacted>", "[redacted]", "***", "*****",
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

    @classmethod
    def _is_safe_scalar(cls, raw: str, *, block_literal: bool = False) -> bool:
        value = raw.strip()
        if not value:
            return True
        if not block_literal and value.startswith("#"):
            return True

        quoted = cls._quoted_value.fullmatch(value)
        if quoted:
            token = quoted.group("value")
            return cls._is_safe_token(token[1:-1], quoted=True)

        if not block_literal:
            value = re.sub(r"[ \t]+#.*$", "", value).strip()
            if not value:
                return True
        return cls._is_safe_token(value)

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
    def _brace_pairs(cls, text: str) -> list[tuple[int, int]]:
        pairs: list[tuple[int, int]] = []
        stack: list[tuple[str, int]] = []
        quote: str | None = None
        escaped = False
        for index, character in enumerate(text):
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
                stack.append((character, index))
            elif character in "}]":
                expected = "{" if character == "}" else "["
                if stack and stack[-1][0] == expected:
                    opener, start = stack.pop()
                    if opener == "{":
                        pairs.append((start, index))
        return pairs

    @staticmethod
    def _top_level_segments(text: str) -> list[str]:
        segments: list[str] = []
        start = 0
        stack: list[str] = []
        quote: str | None = None
        escaped = False
        for index, character in enumerate(text):
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
            elif character in "}]":
                expected = "{" if character == "}" else "["
                if stack and stack[-1] == expected:
                    stack.pop()
            elif character == "," and not stack:
                segments.append(text[start:index])
                start = index + 1
        segments.append(text[start:])
        return segments

    @classmethod
    def _enclosing_flow_map(
        cls,
        text: str,
        key_start: int,
        pairs: list[tuple[int, int]],
    ) -> tuple[int, int] | None:
        candidates = [
            pair for pair in pairs if pair[0] < key_start < pair[1]
        ]
        for start, end in sorted(candidates, key=lambda pair: pair[1] - pair[0]):
            prefix = text[start + 1 : key_start]
            segments = cls._top_level_segments(prefix)
            current = segments[-1].strip()
            previous = [segment.strip() for segment in segments[:-1] if segment.strip()]
            if current:
                continue
            if all(":" in segment for segment in previous):
                return start, end
        return None

    @staticmethod
    def _extract_flow_value(text: str, value_start: int, map_end: int) -> str:
        index = value_start
        while index < map_end and text[index].isspace():
            index += 1
        start = index
        stack: list[str] = []
        quote: str | None = None
        escaped = False
        while index < map_end:
            character = text[index]
            if quote is not None:
                if escaped:
                    escaped = False
                elif character == "\\":
                    escaped = True
                elif character == quote:
                    quote = None
                index += 1
                continue
            if character in {'"', "'"}:
                quote = character
            elif character in "{[":
                stack.append(character)
            elif character in "}]":
                expected = "{" if character == "}" else "["
                if stack and stack[-1] == expected:
                    stack.pop()
                elif not stack:
                    break
            elif character == "," and not stack:
                break
            index += 1
        return text[start:index].strip()

    @classmethod
    def _block_content_is_safe(
        cls,
        lines: list[str],
        indicator_index: int,
        indicator_column: int,
        indicator: str,
    ) -> bool:
        match = cls._block_indicator.fullmatch(indicator.strip())
        explicit_indent: int | None = None
        if match:
            digit = match.group("indent_first") or match.group("indent_after")
            if digit:
                explicit_indent = int(digit)

        content_indent = (
            indicator_column + explicit_indent
            if explicit_indent is not None
            else None
        )

        first: int | None = None
        for index in range(indicator_index + 1, len(lines)):
            line = lines[index]
            if not line.strip():
                continue
            indent = cls._indent_width(line)
            if content_indent is None:
                if indent <= indicator_column:
                    return True
                content_indent = indent
            if indent < content_indent:
                return True
            first = index
            break
        if first is None or content_indent is None:
            return True

        for line in lines[first:]:
            if not line.strip():
                continue
            indent = cls._indent_width(line)
            if indent < content_indent:
                break
            if not cls._is_safe_scalar(line.strip(), block_literal=True):
                return False
        return True

    @classmethod
    def _yaml_continuation_is_safe(
        cls, lines: list[str], key_index: int, key_column: int
   ) -> bool:
        index = key_index + 1
        found = False
        while index < len(lines):
            line = lines[index]
            if not line.strip():
                index += 1
                continue
            indent = cls._indent_width(line)
            stripped = line.lstrip(" \t")
            if stripped.startswith("#"):
                if indent < key_column:
                    break
                index += 1
                continue

            if indent < key_column or (
                indent == key_column
                and not cls._is_sequence_indicator(stripped)
            ):
                break
            found = True

            value = stripped
            sequence_markers = 0
            while cls._is_sequence_indicator(value):
                sequence_markers += 1
                if value == "-":
                    value = ""
                    break
                value = value[1:].lstrip()

            if not value:
                index += 1
                continue

            if cls._block_indicator.fullmatch(value):
                indicator_column = indent + 2 * sequence_markers
                if not cls._block_content_is_safe(
                    lines, index, indicator_column, value
                ):
                    return False
                index += 1
                continue

            if not cls._is_safe_scalar(value):
                return False
            index += 1

        return True if found else True

    def search(self, text: str) -> re.Match[str] | None:
        lines = text.splitlines()
        offsets: list[int] = []
        cursor = 0
        for line in lines:
            offsets.append(cursor)
            cursor += len(line) + 1
        pairs = self._brace_pairs(text)

        for line_index, line in enumerate(lines):
            for match in self._key.finditer(line):
                absolute_start = offsets[line_index] + match.start()
                absolute_end = offsets[line_index] + match.end()
                flow_map = self._enclosing_flow_map(
                    text, absolute_start, pairs
                )
                if flow_map is not None:
                    value = self._extract_flow_value(
                        text, absolute_end, flow_map[1]
                    )
                    if not self._is_safe_scalar(value):
                        return match
                    continue

                value = line[match.end() :]
                key_column = self._column_width(line[: match.start()])
                if self._block_indicator.fullmatch(value.strip()):
                    if not self._block_content_is_safe(
                        lines, line_index, key_column, value
                    ):
                        return match
                elif not value.strip() or value.lstrip().startswith("#"):
                    if not self._yaml_continuation_is_safe(
                        lines, line_index, key_column
                    ):
                        return match
                elif not self._is_safe_scalar(value):
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
    "github_token": ("ghp_" + "A" * 30, "github_pat_" + "A" * 30),
    "gitlab_token": ("glpat-" + "A" * 24,),
    "aws_access_key": ("AKIA" + "ABCDEFGHIJKLMNOP", "ASIA" + "QRSTUVWXYZABCDEF"),
    "google_api_key": ("AIza" + "A" * 35,),
    "slack_token": (
        "xoxb-" + "1234567890-ABCDEFGHIJK",
        "xapp-" + "1-ABCDEFGHIJK-1234567890",
        "xoxe-" + "1-ABCDEFGHIJKKLNPLABCDEF1234567890",
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
        '{"password":\n"hunter2"}',
       "{\n  \"password\": \"hunter2\",\n  \"id\": 1\n}",
        "An opening brace `{` appears here; password: ${TOKEN},suffix:hunter2",
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
        "password:\n- |\n  hunter2",
        "password:\n  |\n    hunter2",
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
    "{\n  \"password\": \"${TOKEN}\",\n  \"id\": 1\n}",
    "password:\n  REDACTED",
    "password:\n  - ${TOKEN}",
    "- password:\n    REDACTED\n  id: 1",
    "password:\n- ${TOKEN}",
    "password:\n-\n  REDACTED",
    "- password:\n  -\n    ${TOKEN}",
    "password: |2\n  REDACTED",
    "- password: |\n    REDACTEDE∆‚ñC¢"¿¢'77v˜&C•∆‚“≈∆‚$TD5DTB"¿¢'77v˜&C•∆‚≈∆‚$TD5DTB"¿¢ê††•4dUÙDE$U55ÙdïÖEU$U2“Ä¢'fW'6ñˆ‚„"„2„B"¿¢'c„"„2„B"¿¢%fW'6ñˆ„¢„#„3„C"¿¢&'Vñ∆B„"„2„B"¿¢'&V∆V6UÛ„"„2„B"¿¢&ï˜fW'6ñˆ„”„"„2„B"¿¢''VÁFñ÷RfW'6ñˆ‚„"„2„F"¿¢'fW'6ñˆ‚¢£„"„2„B¢¢"¿¢&'Vñ∆BÛ„"„2„EÚ"¿¢''VÁFñ÷RfW'6ñˆ‚É„"„2„Bí"¿¢&áGG¢Úı≥££”£ÉÉÚ"¿¢#£¢"¿¢ê