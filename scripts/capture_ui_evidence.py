#!/usr/bin/env python3
"""Capture UI evidence for AfrekaOS Offline (Task 004B).

Starts the local web app in a subprocess, fetches all key routes, and saves
HTML/JSON snapshots under artifacts/eval/task-004B-ui-evidence/. Confirms HTTP
200 and key labels. Does NOT require model files, llama.cpp, or internet.

Set AFREKAOS_CAPTURE_INFERENCE=1 to also submit one bounded POST to
/advisor/daily (only if model + runtime are available).
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOST = "127.0.0.1"
PORT = 8787
BASE = f"http://{HOST}:{PORT}"
OUT_DIR = REPO_ROOT / "artifacts" / "eval" / "task-004B-ui-evidence"

# Routes to capture: (path, output_filename, optional label to verify in HTML)
ROUTES = [
    ("/", "home.html", "Mission Control"),
    ("/demo", "demo.html", "Demo Scenarios"),
    ("/advisor/daily", "advisor-daily.html", "Daily Operations Advisor"),
    ("/advisor/inventory", "advisor-inventory.html", "Inventory and Stock Check"),
    ("/advisor/cashflow", "advisor-cashflow.html", "Cashflow Pressure Coach"),
    ("/status", "status.html", "Offline System Status"),
]


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


def _fetch(path: str) -> tuple[int, str]:
    with urllib.request.urlopen(f"{BASE}{path}", timeout=8) as r:
        return r.status, r.read().decode("utf-8", errors="replace")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    env = dict(os.environ)
    env["AFREKAOS_QWEN_NO_THINK"] = "1"
    # Point model at a nonexistent path so no inference runs during page capture.
    env.setdefault("AFREKAOS_MODEL_PATH", "/nonexistent/capture_evidence_model.gguf")

    proc = subprocess.Popen(
        [sys.executable, "-m", "app.web_app"],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    failures: list[str] = []
    captured: list[str] = []
    health_data: dict = {}

    try:
        if not _wait_for_health():
            failures.append("server did not become healthy")
            if proc.poll() is not None:
                _, err = proc.communicate(timeout=2)
                print(f"[server exited early] stderr:\n{err.decode(errors='replace')}")
            return _finish(failures, captured, health_data, proc)

        print("[ok] server healthy")

        # Capture /health as JSON.
        try:
            status, body = _fetch("/health")
            if status != 200:
                failures.append(f"/health returned {status}")
            else:
                health_data = json.loads(body)
                (OUT_DIR / "health.json").write_text(body, encoding="utf-8")
                captured.append("health.json")
                for key in ("ok", "product", "model_exists", "retrieval_index_exists"):
                    if key not in health_data:
                        failures.append(f"/health JSON missing key: {key}")
                print(f"[ok] /health -> {status} (valid JSON)")
        except Exception as exc:
            failures.append(f"/health failed: {exc}")

        # Capture HTML routes.
        for path, filename, label in ROUTES:
            try:
                status, body = _fetch(path)
                if status != 200:
                    failures.append(f"{path} returned {status}")
                else:
                    (OUT_DIR / filename).write_text(body, encoding="utf-8")
                    captured.append(filename)
                    if label and label.lower() not in body.lower():
                        failures.append(f"{path}: label '{label}' not found")
                    print(f"[ok] {path} -> {status} ({len(body)} bytes) -> {filename}")
            except Exception as exc:
                failures.append(f"{path} fetch failed: {exc}")

        # Verify demo scenario titles are present.
        demo_html = (OUT_DIR / "demo.html").read_text(encoding="utf-8") if (OUT_DIR / "demo.html").is_file() else ""
        for title in ("Low sales, stockout, supplier delay", "Expansion readiness",
                       "Inventory pressure", "Cash pressure and customer credit"):
            if title.lower() not in demo_html.lower():
                failures.append(f"demo missing scenario title: {title}")

        # Optional inference capture.
        if os.environ.get("AFREKAOS_CAPTURE_INFERENCE", "") == "1":
            # Restore real model path for inference.
            os.environ.pop("AFREKAOS_MODEL_PATH", None)
            # Re-check model availability via /health.
            try:
                status, body = _fetch("/health")
                hd = json.loads(body)
                if hd.get("model_exists") and hd.get("llama_binary", "not detected") != "not detected":
                    print("[inference] submitting bounded POST /advisor/daily ...")
                    data = urllib.parse.urlencode(
                        {"question": "A small shop has low sales, missing fast-moving stock, "
                                     "supplier delay, and customers asking for credit. "
                                     "Give a short operating checklist."}
                    ).encode()
                    req = urllib.request.Request(f"{BASE}/advisor/daily", data=data, method="POST")
                    with urllib.request.urlopen(req, timeout=160) as r:
                        rbody = r.read().decode("utf-8", errors="replace")
                        (OUT_DIR / "daily-result.html").write_text(rbody, encoding="utf-8")
                        captured.append("daily-result.html")
                        print(f"[ok] POST /advisor/daily -> {r.status} ({len(rbody)} bytes)")
                else:
                    print("[inference] skipped: model or runtime not available")
            except Exception as exc:
                print(f"[inference] skipped or failed: {exc}")
        else:
            print("[inference] skipped (set AFREKAOS_CAPTURE_INFERENCE=1 to enable)")

    finally:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

    return _finish(failures, captured, health_data, proc)


def _finish(failures: list[str], captured: list[str], health_data: dict, proc) -> int:
    # Write evidence notes.
    notes = []
    notes.append("# Task 004B UI Evidence Notes")
    notes.append("")
    notes.append(f"- Generated: {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}")
    notes.append(f"- Server: {BASE}")
    notes.append(f"- Health JSON valid: {bool(health_data)}")
    notes.append(f"- Health ok: {health_data.get('ok', 'n/a')}")
    notes.append(f"- Model exists: {health_data.get('model_exists', 'n/a')}")
    notes.append(f"- Retrieval index exists: {health_data.get('retrieval_index_exists', 'n/a')}")
    notes.append(f"- Llama binary: {health_data.get('llama_binary', 'n/a')}")
    notes.append("")
    notes.append("## Files captured")
    notes.append("")
    for f in captured:
        notes.append(f"- {f}")
    if not captured:
        notes.append("- (none)")
    notes.append("")
    notes.append("## Validation")
    notes.append("")
    if failures:
        notes.append("### Failures")
        for f in failures:
            notes.append(f"- {f}")
    else:
        notes.append("All routes returned 200 and key labels were verified.")
    notes.append("")
    notes.append("No fabricated runtime numbers. Static page captures only "
                 "(unless AFREKAOS_CAPTURE_INFERENCE=1 was set).")
    (OUT_DIR / "evidence-notes.md").write_text("\n".join(notes), encoding="utf-8")

    if failures:
        print("\nEVIDENCE CAPTURE FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1
    print(f"\nEVIDENCE CAPTURE PASSED ({len(captured)} files)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
