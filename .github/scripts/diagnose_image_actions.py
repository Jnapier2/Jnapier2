#!/usr/bin/env python3
"""Temporary read-only observer for Image Downloader workflow reconciliation.

Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import json
import os
import urllib.request
from pathlib import Path

URL = "https://api.github.com/repos/Jnapier2/image-downloader/actions/runs?per_page=30"
headers = {
    "Accept": "application/vnd.github+json",
    "User-Agent": "Gateway-Image-Reconciliation-Observer/1.0",
    "X-GitHub-Api-Version": "2022-11-28",
}
token = os.environ.get("GITHUB_TOKEN", "").strip()
if token:
    headers["Authorization"] = f"Bearer {token}"
request = urllib.request.Request(URL, headers=headers)
with urllib.request.urlopen(request, timeout=20) as response:
    payload = json.load(response)
records = []
print("IMAGE_ACTION_RUNS_BEGIN")
for run in payload.get("workflow_runs", []):
    record = {
        "id": run.get("id"),
        "name": run.get("name"),
        "event": run.get("event"),
        "status": run.get("status"),
        "conclusion": run.get("conclusion"),
        "head_branch": run.get("head_branch"),
        "head_sha": run.get("head_sha"),
        "run_number": run.get("run_number"),
        "created_at": run.get("created_at"),
        "updated_at": run.get("updated_at"),
        "jobs_url": run.get("jobs_url"),
        "html_url": run.get("html_url"),
    }
    records.append(record)
    print(json.dumps(record, sort_keys=True))
print("IMAGE_ACTION_RUNS_END")
output = Path("audit-output/image-downloader-actions.json")
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(
    json.dumps(
        {
            "schema_version": 1,
            "repository": "Jnapier2/image-downloader",
            "rights_notice": "Copyright © 2026 Gateway Information Group LLC. All rights reserved.",
            "workflow_runs": records,
        },
        indent=2,
        ensure_ascii=False,
    )
    + "\n",
    encoding="utf-8",
)
