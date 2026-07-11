#!/usr/bin/env python3
"""Prepare visual evidence for AfrekaOS Offline (Task 005B).

Standard library only. No browser automation, no Playwright/Selenium/
pyppeteer/npm, no external dependencies. Does NOT fabricate PNG screenshots.

What it does:
  1. Starts the local web app in a subprocess.
  2. Verifies /, /demo, /status, and /health return HTTP 200.
  3. Copies (or summarizes) existing HTML/JSON route snapshots from
     artifacts/eval/task-004B-ui-evidence/ into
     artifacts/submission/visual-evidence/ (as *_snapshot.html / *_snapshot.json
     copies plus an index), so the visual-evidence directory is self-contained.
  4. Writes a prep log to
     artifacts/submission/visual-evidence/visual-evidence-prep-log.md.

Writes:
  artifacts/submission/visual-evidence/visual-evidence-prep-log.md
"""

from __future__ import annotations

import json
import os
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOST = "127.0.0.1"
PORT = 8787
BASE = f"http://{HOST}:{PORT}"

UI_EVIDENCE_DIR = REPO_ROOT / "artifacts" / "eval" / "task-004B-ui-evidence"
VISUAL_DIR = REPO_ROOT / "artifacts" / "submission" / "visual-evidence"
PREP_LOG = VISUAL_DIR / "visual-evidence-prep-log.md"

# Snapshot files we expect to already exist (from capture_ui_evidence.py).
EXPECTED_SNAPSHOTS = [
    "home.html",
    "demo.html",
    "advisor-daily.html",
    "advisor-inventory.html",
    "advisor-cashflow.html",
    "status.html",
    "health.json",
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


def _check_route(path: str) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(f"{BASE}{path}", timeout=5) as r:
            body = r.read()
            return (r.status == 200, f"{r.status} ({len(body)} bytes)")
    except Exception as exc:
        return (False, f"request failed: {exc}")


def _copy_snapshots() -> dict:
    """Copy existing HTML/JSON snapshots into the visual-evidence dir."""
    summary = {"copied": [], "missing": []}
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)
    snap_dir = VISUAL_DIR / "route-snapshots"
    snap_dir.mkdir(parents=True, exist_ok=True)
    for name in EXPECTED_SNAPSHOTS:
        src = UI_EVIDENCE_DIR / name
        if src.is_file():
            dst = snap_dir / name
            shutil.copyfile(src, dst)
            summary["copied"].append(name)
        else:
            summary["missing"].append(name)
    return summary


def _build_snapshot_index(copied: list[str], missing: list[str]) -> str:
    lines = []
    lines.append("# Route Snapshots — copied by prepare_visual_evidence.py")
    lines.append("")
    lines.append("These are copies of the HTML/JSON route snapshots captured by "
                 "`scripts/capture_ui_evidence.py`. They are NOT screenshots — "
                 "they prove each route renders and returns correct content. "
                 "For real PNG screenshots, follow "
                 "`../screenshot-checklist.md` manually.")
    lines.append("")
    lines.append("| File | Route |")
    lines.append("|------|-------|")
    route_map = {
        "home.html": "/ (Mission Control)",
        "demo.html": "/demo (Demo Scenarios)",
        "advisor-daily.html": "/advisor/daily (Daily Operations Advisor)",
        "advisor-inventory.html": "/advisor/inventory (Inventory and Stock Check)",
        "advisor-cashflow.html": "/advisor/cashflow (Cashflow Pressure Coach)",
        "status.html": "/status (Offline System Status)",
        "health.json": "/health (JSON)",
    }
    for name in copied:
        lines.append(f"| `{name}` | {route_map.get(name, '—')} |")
    if missing:
        lines.append("")
        lines.append("## Missing (not captured)")
        for name in missing:
            lines.append(f"- `{name}`")
    return "\n".join(lines) + "\n"


def main() -> int:
    VISUAL_DIR.mkdir(parents=True, exist_ok=True)

    started_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    log_lines: list[str] = []
    log_lines.append("# Visual Evidence Prep Log — AfrekaOS Offline (Task 005B)")
    log_lines.append("")
    log_lines.append(f"- Generated: {started_at}")
    log_lines.append(f"- Server: {BASE}")
    log_lines.append("- Dependency check: standard library only (no browser automation).")

    failures: list[str] = []

    # Start the server.
    env = dict(os.environ)
    env["AFREKAOS_QWEN_NO_THINK"] = "1"
    env.setdefault("AFREKAOS_MODEL_PATH", "/nonexistent/visual_evidence_prep.gguf")
    proc = subprocess.Popen(
        [sys.executable, "-m", "app.web_app"],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    route_results: list[tuple[str, bool, str]] = []
    try:
        if not _wait_for_health():
            failures.append("server did not become healthy within timeout")
            if proc.poll() is not None:
                _, err = proc.communicate(timeout=2)
                log_lines.append(f"- [server exited early] stderr: "
                                 f"{err.decode(errors='replace')}")
            return _finish(log_lines, failures)
        log_lines.append("- [ok] server is healthy")

        for path in ("/", "/demo", "/status", "/health"):
            ok, detail = _check_route(path)
            route_results.append((path, ok, detail))
            tag = "ok" if ok else "FAIL"
            log_lines.append(f"- [{tag}] {path} -> {detail}")
            if not ok:
                failures.append(f"{path} did not return 200")

        # Validate /health JSON.
        try:
            with urllib.request.urlopen(f"{BASE}/health", timeout=5) as r:
                data = json.loads(r.read().decode("utf-8"))
                log_lines.append(f"- [ok] /health is valid JSON: ok={data.get('ok')}")
        except Exception as exc:
            failures.append(f"/health JSON parse failed: {exc}")
            log_lines.append(f"- [FAIL] /health JSON parse failed: {exc}")

    finally:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

    # Copy/summarize existing snapshots.
    snap = _copy_snapshots()
    log_lines.append(f"- snapshots copied: {len(snap['copied'])}")
    if snap["missing"]:
        log_lines.append(f"- snapshots missing: {', '.join(snap['missing'])}")
        failures.append(f"missing snapshots: {snap['missing']}")
    index_path = VISUAL_DIR / "route-snapshots" / "README.md"
    index_path.write_text(
        _build_snapshot_index(snap["copied"], snap["missing"]), encoding="utf-8")

    # Screenshots/video are manual; record honestly.
    png_count = len(list(VISUAL_DIR.glob("*.png")))
    mp4_count = len(list(VISUAL_DIR.glob("*.mp4"))) + len(list(VISUAL_DIR.glob("*.webm")))
    log_lines.append(f"- PNG screenshots present in this dir: {png_count}")
    log_lines.append(f"- video files present in this dir: {mp4_count}")
    log_lines.append("- screenshots/video: instructions only unless PNG/MP4/WebM "
                     "files are present above (none fabricated by this script).")

    return _finish(log_lines, failures)


def _finish(log_lines: list[str], failures: list[str]) -> int:
    log_lines.append("")
    if failures:
        log_lines.append("## Result: FAIL")
        log_lines.append("")
        for f in failures:
            log_lines.append(f"- {f}")
    else:
        log_lines.append("## Result: VISUAL EVIDENCE PREP PASSED")
        log_lines.append("")
        log_lines.append("All routes returned 200 and existing route snapshots "
                         "were copied. PNG screenshots and demo video remain "
                         "manual capture steps (see screenshot-checklist.md and "
                         "demo-video-shot-list.md). Nothing was fabricated.")
    PREP_LOG.write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    print("\n".join(log_lines))
    print(f"\nPrep log written to: {PREP_LOG}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
