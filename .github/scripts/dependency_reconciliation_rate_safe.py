#!/usr/bin/env python3
"""Run dependency reconciliation with raw public-file retrieval.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import time
import urllib.error
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor as OriginalThreadPoolExecutor
from typing import Any

import dependency_reconciliation_audit as core

RIGHTS_NOTICE = "Copyright © 2026 Gateway Information Group LLC. All rights reserved."
USER_AGENT = "Gateway-Dependency-Reconciliation-Rate-Safe/1.0"
HTTP_ATTEMPTS = 4
HTTP_TIMEOUT_SECONDS = 20
MAX_FILE_BYTES = 5_000_000


def bounded_executor(*args: Any, **kwargs: Any) -> OriginalThreadPoolExecutor:
    requested = kwargs.pop("max_workers", None)
    if requested is None and args:
        requested = args[0]
        args = args[1:]
    workers = min(int(requested or 4), 4)
    return OriginalThreadPoolExecutor(workers, *args, **kwargs)


def fetch_remote(
    owner: str,
    repository: str,
    path: str,
    *,
    allow_missing: bool,
) -> str | None:
    quoted_path = "/".join(
        urllib.parse.quote(part, safe="") for part in path.split("/")
    )
    url = (
        "https://raw.githubusercontent.com/"
        f"{urllib.parse.quote(owner, safe='')}/"
        f"{urllib.parse.quote(repository, safe='')}/main/{quoted_path}"
    )
    last_error: Exception | None = None
    for attempt in range(1, HTTP_ATTEMPTS + 1):
        request = urllib.request.Request(
            url,
            headers={
                "Accept": "text/plain, */*;q=0.1",
                "User-Agent": USER_AGENT,
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=HTTP_TIMEOUT_SECONDS) as response:
                data = response.read(MAX_FILE_BYTES + 1)
            if len(data) > MAX_FILE_BYTES:
                raise ValueError(f"response exceeded {MAX_FILE_BYTES} bytes")
            return data.decode("utf-8-sig")
        except urllib.error.HTTPError as exc:
            if exc.code == 404 and allow_missing:
                return None
            last_error = exc
        except (
            urllib.error.URLError,
            TimeoutError,
            UnicodeError,
            ValueError,
        ) as exc:
            last_error = exc
        if attempt < HTTP_ATTEMPTS:
            time.sleep(min(8.0, 1.5 * (2 ** (attempt - 1))))
    raise RuntimeError(f"unable to read {repository}/{path}: {last_error}")


if core.RIGHTS_NOTICE != RIGHTS_NOTICE:
    raise SystemExit("Dependency reconciliation rights notice changed")

core.ThreadPoolExecutor = bounded_executor
core.fetch_remote = fetch_remote


if __name__ == "__main__":
    raise SystemExit(core.main())
