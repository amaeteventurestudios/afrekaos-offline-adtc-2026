#!/usr/bin/env python3
"""Smoke test for AfrekaOS full UI localization (Task 006B).

Starts the local web app (no model required), requests pages with ?lang=
parameters, and verifies the UI renders in the selected language. Also saves
HTML snapshots under artifacts/eval/task-006B-ui-localization/. Standard
library only. Does NOT call the model, the internet, or require llama.cpp.
"""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOST = "127.0.0.1"
PORT = int(os.environ.get("AFREKAOS_WEB_PORT", "8793"))
BASE = f"http://{HOST}:{PORT}"
OUT_DIR = REPO_ROOT / "artifacts" / "eval" / "task-006B-ui-localization"


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


def _fetch(path: str) -> str:
    url = f"{BASE}{path}"
    with urllib.request.urlopen(url, timeout=10) as r:
        return r.read().decode("utf-8", errors="replace")


def main() -> int:
    env = dict(os.environ)
    env["AFREKAOS_MODEL_PATH"] = "/nonexistent/ui_loc_smoke.gguf"
    env["AFREKAOS_WEB_PORT"] = str(PORT)

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
            failures.append("server did not become healthy")
            if proc.poll() is not None:
                _, err = proc.communicate(timeout=2)
                print(f"[server exited] {err.decode(errors='replace')[:500]}")
            return 1
        print("[ok] server is healthy")

        OUT_DIR.mkdir(parents=True, exist_ok=True)

        # --- French pages ---
        checks = [
            ("/?lang=fr", "fr-home.html", [
                ("Tableau de bord", True),
                ("Mission Control", False),
                ("langswitch", True),
                ("local uniquement", True),
            ]),
            ("/advisor/daily?lang=fr", "fr-daily-advisor.html", [
                ("Obtenir des conseils", True),
                ("Votre question", True),
                ("Get operating guidance", False),
            ]),
            ("/demo?lang=fr", "fr-demo.html", [
                ("Scénarios de démo", True),
                ("Lancer ce scénario", True),
                ("Demo Scenarios", False),
            ]),
            ("/status?lang=fr", "fr-status.html", [
                ("Statut du système hors ligne", True),
                ("Offline System Status", False),
            ]),
            ("/advisor/daily?lang=pcm", "pcm-daily-advisor.html", [
                ("Get business guide", True),
                ("Your business matter", True),
                ("Mission Control", False),
            ]),
            ("/advisor/daily?lang=yo", "yo-daily-advisor.html", [
                ("Ìdarí iṣẹ́", True),
                ("langswitch", True),
            ]),
        ]

        for path, fname, asserts in checks:
            body = _fetch(path)
            (OUT_DIR / fname).write_text(body, encoding="utf-8")
            for needle, should_exist in asserts:
                present = needle in body
                if should_exist and not present:
                    failures.append(f"{path}: expected '{needle}' but not found")
                elif not should_exist and present:
                    failures.append(f"{path}: '{needle}' should NOT appear")
            print(f"[ok] {path} -> {fname}")

        # --- Language selector present on every page ---
        for path in ("/", "/demo", "/advisor/daily", "/advisor/inventory",
                     "/advisor/cashflow", "/status"):
            body = _fetch(path)
            if "langswitch" not in body:
                failures.append(f"{path}: global language selector missing")
        print("[ok] language selector present on all pages")

        # --- English default ---
        body = _fetch("/")
        if "Mission Control" not in body:
            failures.append("English default missing 'Mission Control'")
        else:
            print("[ok] English default renders correctly")

    finally:
        proc.send_signal(signal.SIGTERM)
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

    # Write notes.
    (OUT_DIR / "localization-smoke-notes.md").write_text(
        "# UI Localization Smoke Notes (Task 006B)\n\n"
        f"- Port: {PORT}\n"
        f"- Languages tested: fr, pcm, yo, en; advisor descriptions and prompts checked by the 006C audit\n"
        f"- Snapshots saved: {len(list(OUT_DIR.glob('*.html')))}\n"
        f"- No model inference required.\n",
        encoding="utf-8",
    )

    if failures:
        print("\nUI LOCALIZATION SMOKE TEST FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("\nUI LOCALIZATION SMOKE TEST PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
