#!/usr/bin/env python3
"""Smoke test for the AfrekaOS Offline local web UI.

Starts the web app in a subprocess, polls /health, then requests /, /status,
and /health. Confirms HTTP 200 and that /health returns valid JSON. Stops the
subprocess cleanly. Does NOT require model files, llama.cpp, or internet.
Standard library only.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOST = "127.0.0.1"
PORT = 8787
BASE = f"http://{HOST}:{PORT}"


def _wait_for_health(timeout: float = 15.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{BASE}/health", timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.4)
    return False


def main() -> int:
    env = dict(os.environ)
    env["AFREKAOS_QWEN_NO_THINK"] = "1"
    # Point model path at a nonexistent file so inference is never attempted;
    # the smoke test only checks page availability, not model output.
    env.setdefault("AFREKAOS_MODEL_PATH", "/nonexistent/smoke_test_model.gguf")

    proc = subprocess.Popen(
        [sys.executable, "-m", "app.web_app"],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    failures: list[str] = []
    try:
        if not _wait_for_health():
            failures.append("server did not become healthy within timeout")
            # Print any stderr for debugging.
            if proc.poll() is not None:
                _, err = proc.communicate(timeout=2)
                print(f"[server exited early] stderr:\n{err.decode(errors='replace')}")
            return 1

        print("[ok] server is healthy")

        # Test routes.
        for path in ("/", "/status", "/health"):
            try:
                with urllib.request.urlopen(f"{BASE}{path}", timeout=5) as r:
                    body = r.read().decode("utf-8", errors="replace")
                    if r.status != 200:
                        failures.append(f"{path} returned {r.status}")
                    else:
                        print(f"[ok] {path} -> 200 ({len(body)} bytes)")
            except Exception as exc:
                failures.append(f"{path} request failed: {exc}")

        # Validate /health is JSON.
        try:
            with urllib.request.urlopen(f"{BASE}/health", timeout=5) as r:
                data = json.loads(r.read().decode("utf-8"))
                for key in ("ok", "product", "model_exists", "retrieval_index_exists"):
                    if key not in data:
                        failures.append(f"/health JSON missing key: {key}")
                print(f"[ok] /health is valid JSON: ok={data.get('ok')}")
        except Exception as exc:
            failures.append(f"/health JSON parse failed: {exc}")

    finally:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

    if failures:
        print("\nSMOKE TEST FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("\nSMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
