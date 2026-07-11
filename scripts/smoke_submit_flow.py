#!/usr/bin/env python3
"""Smoke test for the AfrekaOS Offline advisor submit flow (Task 004C).

Starts the local web app with a deliberately nonexistent model (so no real
inference runs), POSTs a demo question to /advisor/daily, confirms the server
returns a 303 redirect to /job/<id>, then GETs the job page and confirms it
shows progress or completion. Stops the server cleanly. Standard library only.
Does NOT require real model inference.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOST = "127.0.0.1"
PORT = int(os.environ.get("AFREKAOS_WEB_PORT", "8787"))
BASE = f"http://{HOST}:{PORT}"


def _wait_for_health(timeout: float = 20.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{BASE}/health", timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def main() -> int:
    env = dict(os.environ)
    env["AFREKAOS_QWEN_NO_THINK"] = "1"
    # Force a nonexistent model so the job fails fast instead of running.
    env["AFREKAOS_MODEL_PATH"] = "/nonexistent/smoke_submit_flow.gguf"
    env["AFREKAOS_UI_TIMEOUT"] = "5"
    env["AFREKAOS_WEB_PORT"] = str(PORT)

    proc = subprocess.Popen(
        [sys.executable, "-m", "app.web_app"],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    failures: list[str] = []
    job_url = None
    try:
        if not _wait_for_health():
            failures.append("server did not become healthy within timeout")
            if proc.poll() is not None:
                _, err = proc.communicate(timeout=2)
                print(f"[server exited early] stderr:\n{err.decode(errors='replace')}")
            return 1
        print("[ok] server is healthy")

        # POST a demo question; do NOT follow the redirect.
        class _NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None

        opener = urllib.request.build_opener(_NoRedirect)
        data = b"question=" + urllib.request.quote(
            "A small shop has low sales and stockouts. Give a short checklist."
        ).encode()
        req = urllib.request.Request(
            f"{BASE}/advisor/daily", data=data, method="POST"
        )
        try:
            opener.open(req, timeout=15)
            failures.append("expected a 303 redirect after POST")
        except urllib.error.HTTPError as exc:
            if exc.code != 303:
                failures.append(f"expected 303, got {exc.code}")
            else:
                loc = exc.headers.get("Location", "")
                if not loc.startswith("/job/"):
                    failures.append(f"Location not /job/: {loc}")
                else:
                    print(f"[ok] POST /advisor/daily -> 303 {loc}")
                    job_url = f"{BASE}{loc}"

        # GET the job page; confirm it renders progress or a result/error.
        if job_url:
            # Give the worker a moment to run (it will fail fast: no model).
            time.sleep(1.5)
            try:
                with urllib.request.urlopen(job_url, timeout=15) as r:
                    body = r.read().decode("utf-8", errors="replace")
                    if r.status != 200:
                        failures.append(f"job page returned {r.status}")
                    else:
                        shows_progress = "30 to 90 seconds" in body
                        shows_error = "runtime error" in body.lower()
                        shows_status = "Runtime status" in body
                        if not (shows_progress or shows_error):
                            failures.append(
                                "job page shows neither progress message nor error"
                            )
                        else:
                            print("[ok] job page shows progress or error")
                        if not shows_status:
                            failures.append("job page missing runtime status panel")
                        else:
                            print("[ok] job page has runtime status panel")
                        if "13 Offline mode" in body:
                            failures.append("job page contains '13 Offline mode'")
                        else:
                            print("[ok] job page has no '13 Offline mode' marker")
            except Exception as exc:
                failures.append(f"job page fetch failed: {exc}")

    finally:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

    if failures:
        print("\nSUBMIT FLOW SMOKE TEST FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("\nSUBMIT FLOW SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())