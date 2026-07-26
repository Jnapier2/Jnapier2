#!/usr/bin/env python3
"""Run the rendered portfolio audit with bounded GitHub rate-limit recovery.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import time
from concurrent.futures import ThreadPoolExecutor as OriginalThreadPoolExecutor
from typing import Any

import portfolio_audit as core
import portfolio_audit_html as rendered

ORIGINAL_REQUEST_BYTES = core.request_bytes


def bounded_executor(*args: Any, **kwargs: Any) -> OriginalThreadPoolExecutor:
    requested = kwargs.get("max_workers")
    if requested is None and args:
        requested = args[0]
        args = args[1:]
    workers = min(int(requested or 3), 3)
    return OriginalThreadPoolExecutor(workers, *args, **kwargs)


def rate_safe_request_bytes(*args: Any, **kwargs: Any) -> tuple[int, str, bytes]:
    last_error: RuntimeError | None = None
    for outer_attempt in range(1, 4):
        try:
            return ORIGINAL_REQUEST_BYTES(*args, **kwargs)
        except RuntimeError as exc:
            message = str(exc)
            if "HTTP Error 403" not in message and "HTTP Error 429" not in message:
                raise
            last_error = exc
            if outer_attempt < 3:
                time.sleep(2 ** outer_attempt)
    assert last_error is not None
    raise last_error


core.HTTP_ATTEMPTS = max(core.HTTP_ATTEMPTS, 5)
core.HTTP_TIMEOUT_SECONDS = max(core.HTTP_TIMEOUT_SECONDS, 20)
core.ThreadPoolExecutor = bounded_executor
core.request_bytes = rate_safe_request_bytes


if __name__ == "__main__":
    raise SystemExit(rendered.main())
