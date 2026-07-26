#!/usr/bin/env python3
"""Run release reconciliation with batched heads and raw public source markers.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

import release_reconciliation_audit as core

RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
USER_AGENT = "Gateway-Release-Reconciliation-Rate-Safe/1.0"
HTTP_ATTEMPTS = 4
HTTP_TIMEOUT_SECONDS = 20
MAX_RESPONSE_BYTES = 4_000_000
HEAD_CACHE: dict[tuple[str, str], str] = {}


def request_bytes(
    url: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    accept: str = "application/vnd.github+json",
) -> bytes:
    headers = {
        "Accept": accept,
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token and urllib.parse.urlparse(url).hostname == "api.github.com":
        headers["Authorization"] = f"Bearer {token}"
    payload = None
    if body is not None:
        payload = json.dumps(body, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"

    last_error: Exception | None = None
    for attempt in range(1, HTTP_ATTEMPTS + 1):
        request = urllib.request.Request(
            url,
            data=payload,
            method=method,
            headers=headers,
        )
        try:
            with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                data = response.read(MAX_RESPONSE_BYTES + 1)
            if len(data) > MAX_RESPONSE_BYTES:
                raise ValueError(f"response exceeded {MAX_RESPONSE_BYTES} bytes")
            return data
        except (
            urllib.error.HTTPError,
            urllib.error.URLError,
            TimeoutError,
            ValueError,
        ) as exc:
            last_error = exc
            if attempt < HTTP_ATTEMPTS:
                time.sleep(min(8.0, 1.5 * (2 ** (attempt - 1))))
    raise RuntimeError(f"{url}: {last_error}")


def load_head_cache() -> None:
    if HEAD_CACHE:
        return
    ledger = core.load_json(core.LEDGER_PATH)
    owner = str(ledger.get("owner") or "")
    projects = ledger.get("projects")
    if not owner or not isinstance(projects, list):
        raise ValueError("release ledger cannot seed the batched head query")

    repositories = [
        str(item.get("repository") or "")
        for item in projects
        if isinstance(item, dict) and item.get("repository")
    ]
    fields: list[str] = []
    alias_to_repo: dict[str, str] = {}
    for index, repository in enumerate(repositories):
        alias = f"repo{index}"
        alias_to_repo[alias] = repository
        fields.append(
            f'{alias}: repository(owner: {json.dumps(owner)}, name: {json.dumps(repository)}) '
            "{ defaultBranchRef { target { ... on Commit { oid } } } }"
        )
    query = "query PortfolioHeads { " + " ".join(fields) + " }"
    payload = json.loads(
        request_bytes(
            "https://api.github.com/graphql",
            method="POST",
            body={"query": query},
        ).decode("utf-8")
    )
    if not isinstance(payload, dict):
        raise ValueError("GitHub GraphQL response was not an object")
    if payload.get("errors"):
        raise RuntimeError(f"GitHub GraphQL returned errors: {payload['errors']}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise ValueError("GitHub GraphQL response lacks data")

    for alias, repository in alias_to_repo.items():
        node = data.get(alias)
        try:
            oid = str(node["defaultBranchRef"]["target"]["oid"]).lower()
        except (KeyError, TypeError) as exc:
            raise ValueError(f"{repository}: default branch head is unavailable") from exc
        if not core.SHA40_RE.fullmatch(oid):
            raise ValueError(f"{repository}: GraphQL head is not a 40-character SHA")
        HEAD_CACHE[(owner, repository)] = oid


def fetch_public_main_head(owner: str, repository: str) -> str:
    load_head_cache()
    try:
        return HEAD_CACHE[(owner, repository)]
    except KeyError as exc:
        raise ValueError(f"{repository}: batched head query omitted the repository") from exc


def fetch_public_file(owner: str, repository: str, path: str) -> str:
    quoted_path = "/".join(
        urllib.parse.quote(part, safe="") for part in path.split("/")
    )
    url = (
        "https://raw.githubusercontent.com/"
        f"{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(repository, safe='')}/main/{quoted_path}"
    )
    return request_bytes(url, accept="text/plain, */*;q=0.1").decode("utf-8-sig")


if core.RIGHTS_NOTICE != RIGHTS_NOTICE:
    raise SystemExit("Release reconciliation rights notice changed")

core.fetch_public_main_head = fetch_public_main_head
core.fetch_public_file = fetch_public_file


if __name__ == "__main__":
    raise SystemExit(core.main())
