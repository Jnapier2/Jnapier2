from __future__ import annotations

import re


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
    "raw_ipv4_address": re.compile(
        r"(?<![\d.])(?:25[0-5]|2[0-4]\d|1?\d?\d)"
        r"(?:\.(?:25[0-5]|2[0-4]\d|1?\d?\d)){3}(?![\d.])"
    ),
    "internal_vault": re.compile(r"ChatGPT_Project_Vault", re.IGNORECASE),
    "private_prompt_file": re.compile(
        r"(?:GLOBAL_CUSTOM_INSTRUCTIONS|PASTE_THIS_IN_NEW_THREAD|PASTE_THIS_DURING_THREAD_UPGRADE)",
        re.IGNORECASE,
    ),
    "operational_secret_assignment": re.compile(
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
        \s*[:=]\s*
        (?:
            "(?:\\.|[^"\r\n])+"
            | '(?:\\.|[^'\r\n])+'
            | [^\s,;}\]\r\n]+
        )
        """
    ),
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
    ),
}


PRIVATE_PATH_FIXTURES = {
    "personal_windows_path": (r"C:\Users\example-user\private-project",),
    "unix_home_path": ("/home/example-user/private-project",),
    "macos_home_path": ("/Users/example-user/private-project",),
    "raw_ipv4_address": ("192.0.2.42",),
}
