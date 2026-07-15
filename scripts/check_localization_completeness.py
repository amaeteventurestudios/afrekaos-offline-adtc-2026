#!/usr/bin/env python3
"""Audit non-English AfrekaOS pages for major English UI leakage (Task 006C).

Uses the local web server only; it never invokes the model or an external API.
"""
from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PORT = int(os.environ.get("AFREKAOS_WEB_PORT", "8794"))
BASE = f"http://127.0.0.1:{PORT}"
OUT = ROOT / "artifacts/eval/task-006C-localization-audit"
PAGES = [
    ("/advisor/daily?lang=fr", "fr-daily.html"), ("/advisor/inventory?lang=fr", "fr-inventory.html"),
    ("/advisor/cashflow?lang=fr", "fr-cashflow.html"), ("/demo?lang=fr", "fr-demo.html"),
    ("/status?lang=fr", "fr-status.html"), ("/advisor/daily?lang=yo", "yo-daily.html"),
    ("/advisor/inventory?lang=ha", "ha-inventory.html"), ("/advisor/inventory?lang=sw", "sw-inventory.html"),
    ("/advisor/cashflow?lang=pcm", "pcm-cashflow.html"),
]
LEAKS = ["Mission Control", "Demo Scenarios", "Daily Advisor", "Offline Status", "Daily Operations Advisor", "Inventory and Stock Check", "Cashflow Pressure Coach", "Check fast-moving items", "Reason through cash pressure", "Triage low sales", "Your operations question", "Your business question", "Answer language", "Response language", "Get operating guidance", "Operating Guidance", "Runtime Summary", "Runtime Status", "AfrekaOS provides operational guidance only", "This can take 30 to 90 seconds", "Customers are asking for credit", "I have two fast-moving items"]

def fetch(path: str) -> str:
    with urllib.request.urlopen(BASE + path, timeout=10) as response:
        return response.read().decode("utf-8", errors="replace")

def main() -> int:
    env = dict(os.environ, AFREKAOS_WEB_PORT=str(PORT), AFREKAOS_MODEL_PATH="/nonexistent/localization-audit.gguf")
    proc = subprocess.Popen([sys.executable, "-m", "app.web_app"], cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    failures: list[str] = []
    OUT.mkdir(parents=True, exist_ok=True)
    try:
        for _ in range(50):
            try:
                fetch("/health")
                break
            except Exception:
                time.sleep(.2)
        else:
            failures.append("local web app did not become ready")
        for path, name in PAGES:
            if failures:
                break
            body = fetch(path)
            (OUT / name).write_text(body, encoding="utf-8")
            for phrase in LEAKS:
                if phrase in body:
                    failures.append(f"{path}: major English leakage: {phrase!r}")
    finally:
        proc.send_signal(signal.SIGTERM)
        try: proc.wait(timeout=5)
        except subprocess.TimeoutExpired: proc.kill()
    lines = ["# Localization Completeness Report (Task 006C)", "", f"- Pages checked: {len(PAGES)}", f"- Result: {'FAIL' if failures else 'PASS'}", ""]
    lines += [f"- {item}" for item in (failures or ["No major English UI leakage found."])]
    (OUT / "localization-completeness-report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    for item in failures: print(item)
    return 1 if failures else 0

if __name__ == "__main__":
    raise SystemExit(main())
