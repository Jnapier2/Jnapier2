"""Sandboxed browser smoke test using the runner's installed browser.

No downloads or changes to browser policy. Test-generated files stay in a
project-local temporary directory that is removed after the run.
Copyright © 2026 Gateway Information Group LLC. All rights reserved.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "professional-portfolio" / "account-analytics"
DRIVER = r'''
"use strict";
try {
  const text = id => document.getElementById(id).textContent;
  const check = (ok, label) => { if (!ok) throw new Error(label); };
  const select = (id, value) => { const e=document.getElementById(id); e.value=value; e.dispatchEvent(new Event("change")); };
  check(text("count") === "12", "initial count");
  check(text("spend") === "$165,500", "initial spend");
  check(text("savings") === "$17,750", "initial savings");
  check(text("review") === "2", "initial quality");
  const clientA = document.querySelector("#groups tr").children;
  check(clientA[3].textContent === "$60,000", "client all spend");
  check(clientA[4].textContent === "$52,000", "client eligible spend");
  check(clientA[5].textContent === "$6,500", "client complete savings");
  check(clientA[6].textContent === "12.5%", "client rate denominator");
  select("client", "Client A"); check(text("count") === "4", "client filter");
  select("quality", "Review"); check(text("count") === "1", "quality filter");
  check(text("rate") === "Not available", "incomplete denominator");
  select("type", "Motion"); check(text("count") === "0", "empty filter");
  check(text("rate") === "Not available", "empty denominator");
  document.getElementById("reset").click(); check(text("count") === "12", "reset");
  select("client", "not-a-client"); check(text("count") === "Not available", "invalid input clears stale result");
  check(document.getElementById("records").children.length === 0, "invalid input clears records");
  document.getElementById("reset").click(); check(text("count") === "12", "reset after failure");
  check(text("error") === "", "error cleared");
  check(document.documentElement.scrollWidth <= innerWidth, "body overflow");
  document.body.dataset.viewport = String(innerWidth);
  document.body.dataset.smoke = "PASS";
} catch (e) { document.body.dataset.smoke = "FAIL"; document.body.dataset.failure = e.message; }
'''


def main() -> int:
    browser = next((shutil.which(name) for name in (
        "google-chrome", "google-chrome-stable", "chromium", "chromium-browser"
    ) if shutil.which(name)), None)
    if not browser:
        print("BROWSER SMOKE BLOCKED: no installed Chrome/Chromium; no browser downloaded.")
        return 2
    version = subprocess.run([browser, "--version"], capture_output=True, text=True, timeout=10)
    with tempfile.TemporaryDirectory(prefix=".account-browser-", dir=ROOT) as folder:
        work = Path(folder)
        shutil.copyfile(DEMO / "analytics.js", work / "analytics.js")
        html = (DEMO / "index.html").read_text(encoding="utf-8")
        # Add a same-origin test driver without changing the application or its CSP.
        html = html.replace('</head>', '<script src="smoke.js" defer></script></head>')
        (work / "index.html").write_text(html, encoding="utf-8")
        (work / "smoke.js").write_text(DRIVER, encoding="utf-8")
        results = []
        for width in (1280, 390):
            run = subprocess.run([
                browser, "--headless", "--dump-dom", "--no-first-run",
                f"--user-data-dir={work / ('profile-' + str(width))}",
                f"--window-size={width},1000", (work / "index.html").as_uri()
            ], capture_output=True, text=True, timeout=40)
            passed = run.returncode == 0 and 'data-smoke="PASS"' in run.stdout
            actual = re.search(r'data-viewport="(\d+)"', run.stdout)
            results.append({"requested_width": width, "actual_width": int(actual.group(1)) if actual else None, "passed": passed, "exit_code": run.returncode})
            if not passed:
                # Do not publish raw browser stderr, environment, or private paths.
                print(json.dumps({"browser": version.stdout.strip(), "checks": results,
                                  "result": "FAIL_OR_BLOCKED", "sandbox_disabled": False}))
                return 1
        print(json.dumps({"browser": version.stdout.strip(), "checks": results,
                          "result": "PASS", "sandbox_disabled": False}))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, subprocess.TimeoutExpired):
        print("BROWSER SMOKE BLOCKED: browser unavailable or timed out; no policy or sandbox change attempted.")
        raise SystemExit(2)
