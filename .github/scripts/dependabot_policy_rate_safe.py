#!/usr/bin/env python3
"""Run Dependabot policy checks from bounded public archives and one PR query.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import io
import json
import os
import stat
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from concurrent.futures import ThreadPoolExecutor as OriginalThreadPoolExecutor
from pathlib import PurePosixPath
from typing import Any

import dependabot_policy_audit as core

RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
USER_AGENT = "Gateway-Dependabot-Policy-Rate-Safe/1.0"
HTTP_ATTEMPTS = 4
HTTP_TIMEOUT_SECONDS = 30
MAX_ARCHIVE_BYTES = 50_000_000
MAX_ARCHIVE_FILES = 5_000
MAX_TEXT_BYTES = 5_000_000
ARCHIVE_CACHE: dict[tuple[str, str], dict[str, bytes]] = {}
PULL_CACHE: dict[tuple[str, str], list[dict[str, Any]]] = {}
ORIGINAL_REQUEST_JSON = core.request_json


def bounded_executor(*args: Any, **kwargs: Any) -> OriginalThreadPoolExecutor:
    requested = kwargs.pop("max_workers", None)
    if requested is None and args:
        requested = args[0]
        args = args[1:]
    workers = min(int(requested or 3), 3)
    return OriginalThreadPoolExecutor(workers, *args, **kwargs)


def request_bytes(
    url: str,
    *,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    accept: str = "*/*",
    maximum_bytes: int,
) -> bytes:
    headers = {"Accept": accept, "User-Agent": USER_AGENT}
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if token and urllib.parse.urlparse(url).hostname == "api.github.com":
        headers["Authorization"] = f"Bearer {token}"
        headers["X-GitHub-Api-Version"] = "2022-11-28"
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
                data = response.read(maximum_bytes + 1)
            if len(data) > maximum_bytes:
                raise ValueError(f"response exceeded {maximum_bytes} bytes")
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


def load_archive(owner: str, repository: str) -> dict[str, bytes]:
    key = (owner, repository)
    cached = ARCHIVE_CACHE.get(key)
    if cached is not None:
        return cached

    url = (
        "https://codeload.github.com/"
        f"{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(repository, safe='')}/zip/refs/heads/main"
    )
    data = request_bytes(
        url,
        maximum_bytes=MAX_ARCHIVE_BYTES,
        accept="application/zip, application/octet-stream",
    )
    files: dict[str, bytes] = {}
    with zipfile.ZipFile(io.BytesIO(data)) as archive:
        members = archive.infolist()
        if len(members) > MAX_ARCHIVE_FILES:
            raise ValueError(
                f"{repository}: archive has {len(members)} entries; "
                f"limit is {MAX_ARCHIVE_FILES}"
            )
        for member in members:
            normalized = member.filename.replace("\\", "/")
            path = PurePosixPath(normalized)
            if path.is_absolute() or ".." in path.parts:
                raise ValueError(f"{repository}: unsafe archive path: {normalized}")
            mode = (member.external_attr >> 16) & 0xFFFF
            if mode and stat.S_ISLNK(mode):
                raise ValueError(f"{repository}: archive symlink is not allowed: {normalized}")
            if member.is_dir() or len(path.parts) < 2:
                continue
            relative = PurePosixPath(*path.parts[1:]).as_posix()
            if member.file_size > MAX_TEXT_BYTES:
                continue
            files[relative] = archive.read(member)
    ARCHIVE_CACHE[key] = files
    return files


def fetch_text(
    owner: str,
    repository: str,
    path: str,
    *,
    allow_missing: bool = False,
) -> str | None:
    data = load_archive(owner, repository).get(path)
    if data is None:
        if allow_missing:
            return None
        raise FileNotFoundError(f"{repository}/{path} is missing from main")
    return data.decode("utf-8-sig")


def workflow_paths(owner: str, repository: str) -> list[str]:
    paths = sorted(
        path
        for path in load_archive(owner, repository)
        if path.startswith(".github/workflows/")
        and PurePosixPath(path).suffix.lower() in {".yml", ".yaml"}
    )
    if len(paths) > core.MAX_WORKFLOWS_PER_REPOSITORY:
        raise ValueError(
            f"workflow count {len(paths)} exceeds "
            f"{core.MAX_WORKFLOWS_PER_REPOSITORY}"
        )
    return paths


def load_pull_cache() -> None:
    if PULL_CACHE:
        return
    policy = core.load_json(core.POLICY_PATH)
    owner = str(policy.get("owner") or "")
    records = policy.get("repositories")
    if not owner or not isinstance(records, list):
        raise ValueError("Dependabot policy cannot seed the batched pull-request query")

    repositories = [
        str(record.get("repository") or "")
        for record in records
        if isinstance(record, dict) and record.get("repository")
    ]
    aliases: dict[str, str] = {}
    fields: list[str] = []
    for index, repository in enumerate(repositories):
        alias = f"repo{index}"
        aliases[alias] = repository
        fields.append(
            f'{alias}: repository(owner: {json.dumps(owner)}, '
            f'name: {json.dumps(repository)}) '
            "{ pullRequests(first: 100, states: OPEN, orderBy: "
            "{field: UPDATED_AT, direction: DESC}) "
            "{ nodes { number author { login } autoMergeRequest { enabledAt } } "
            "pageInfo { hasNextPage } } }"
        )
    query = "query DependabotPulls { " + " ".join(fields) + " }"
    token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not token:
        raise RuntimeError("GITHUB_TOKEN is required for the batched pull-request audit")
    payload = json.loads(
        request_bytes(
            "https://api.github.com/graphql",
            method="POST",
            body={"query": query},
            accept="application/vnd.github+json",
            maximum_bytes=4_000_000,
        ).decode("utf-8")
    )
    if not isinstance(payload, dict):
        raise ValueError("GitHub GraphQL response was not an object")
    if payload.get("errors"):
        raise RuntimeError(f"GitHub GraphQL returned errors: {payload['errors']}")
    data = payload.get("data")
    if not isinstance(data, dict):
        raise ValueError("GitHub GraphQL response lacks data")

    for alias, repository in aliases.items():
        node = data.get(alias)
        if not isinstance(node, dict):
            raise ValueError(f"{repository}: GraphQL repository node is unavailable")
        pulls = node.get("pullRequests")
        if not isinstance(pulls, dict):
            raise ValueError(f"{repository}: GraphQL pull-request connection is unavailable")
        page_info = pulls.get("pageInfo")
        if isinstance(page_info, dict) and page_info.get("hasNextPage"):
            raise ValueError(f"{repository}: open pull-request scan exceeds 100 records")
        normalized: list[dict[str, Any]] = []
        for pull in pulls.get("nodes") or []:
            if not isinstance(pull, dict):
                continue
            author = pull.get("author")
            login = str(author.get("login") or "") if isinstance(author, dict) else ""
            if login == "dependabot":
                login = "dependabot[bot]"
            normalized.append(
                {
                    "number": pull.get("number"),
                    "user": {"login": login},
                    "auto_merge": (
                        {}
                        if pull.get("autoMergeRequest") is not None
                        else None
                    ),
                }
            )
        PULL_CACHE[(owner, repository)] = normalized


def request_json(url: str) -> Any:
    parsed = urllib.parse.urlparse(url)
    parts = [urllib.parse.unquote(part) for part in parsed.path.split("/") if part]
    if len(parts) == 4 and parts[0] == "repos" and parts[3] == "pulls":
        load_pull_cache()
        key = (parts[1], parts[2])
        if key not in PULL_CACHE:
            raise ValueError(f"{parts[2]}: batched pull-request query omitted the repository")
        return PULL_CACHE[key]
    return ORIGINAL_REQUEST_JSON(url)


if core.RIGHTS_NOTICE != RIGHTS_NOTICE:
    raise SystemExit("Dependabot policy rights notice changed")

core.ThreadPoolExecutor = bounded_executor
core.fetch_text = fetch_text
core.workflow_paths = workflow_paths
core.request_json = request_json


if __name__ == "__main__":
    raise SystemExit(core.main())
