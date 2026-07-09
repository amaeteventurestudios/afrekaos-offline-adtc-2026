#!/usr/bin/env python3
"""Final validation runner for AfrekaOS Offline (Task 005A).

Runs every repo validation check, captures pass/fail status, and writes a
markdown log to artifacts/submission/final-validation-log.md. Standard library
only. Does not require model inference, llama.cpp, or internet.

The checks include:
  - check_metadata.py
  - check_model_candidates.py
  - build_retrieval_index.py
  - query_retrieval.py
  - preview_grounded_prompt.py
  - analyze_grounded_outputs.py
  - smoke_web.py
  - capture_ui_evidence.py
  - unittest discover
"""

from __future__ import annotations

import os
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SUBMISSION_DIR = REPO_ROOT / "artifacts" / "submission"
LOG_PATH = SUBMISSION_DIR / "final-validation-log.md"

# (command_args, display_name, timeout_seconds)
CHECKS = [
    (["python3", "scripts/check_metadata.py"], "check_metadata", 30),
    (["python3", "scripts/check_model_candidates.py"], "check_model_candidates", 30),
    (["python3", "scripts/build_retrieval_index.py"], "build_retrieval_index", 30),
    (["python3", "scripts/query_retrieval.py"], "query_retrieval", 30),
    (["python3", "scripts/preview_grounded_prompt.py"], "preview_grounded_prompt", 30),
    (["python3", "scripts/analyze_grounded_outputs.py"], "analyze_grounded_outputs", 30),
    (["python3", "scripts/smoke_web.py"], "smoke_web", 60),
    (["python3", "scripts/capture_ui_evidence.py"], "capture_ui_evidence", 60),
    (["python3", "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py"],
     "unittest discover", 120),
]


def _check_pytest() -> bool:
    try:
        import importlib
        importlib.import_module("pytest")
        return True
    except ImportError:
        return False


def main() -> int:
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    now = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
    pytest_available = _check_pytest()

    results: list[dict] = []
    overall_ok = True

    for cmd, name, timeout in CHECKS:
        print(f"\n{'='*60}")
        print(f"[run] {name}")
        print(f"      {' '.join(cmd)}")
        try:
            proc = subprocess.run(
                cmd,
                cwd=str(REPO_ROOT),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=timeout,
                text=True,
            )
            rc = proc.returncode
            stdout_tail = (proc.stdout or "")[-2000:]
            ok = rc == 0
        except subprocess.TimeoutExpired:
            rc = -1
            stdout_tail = f"[timed out after {timeout}s]"
            ok = False
        except Exception as exc:
            rc = -2
            stdout_tail = f"[error: {exc}]"
            ok = False

        status = "PASS" if ok else "FAIL"
        print(f"      -> {status} (rc={rc})")
        if not ok:
            print(stdout_tail[-500:])

        results.append({
            "name": name,
            "command": " ".join(cmd),
            "rc": rc,
            "ok": ok,
            "status": status,
            "output_tail": stdout_tail,
        })
        if not ok:
            overall_ok = False

    # --- Write markdown log --------------------------------------------------
    lines = []
    lines.append("# Final Validation Log — AfrekaOS Offline (Task 005A)")
    lines.append("")
    lines.append(f"- **Date/time:** {now}")
    lines.append(f"- **Overall:** {'PASS' if overall_ok else 'FAIL'}")
    lines.append(f"- **pytest available:** {pytest_available}")
    lines.append(f"- **Model inference required:** no (all checks are non-inference)")
    lines.append(f"- **Cloud dependencies used:** none")
    lines.append("")
    lines.append("## Checks")
    lines.append("")
    lines.append("| # | Check | Command | Exit code | Status |")
    lines.append("|---|-------|---------|-----------|--------|")
    for i, r in enumerate(results, 1):
        cmd_short = r["command"].replace("python3 ", "")
        lines.append(f"| {i} | {r['name']} | `{cmd_short}` | {r['rc']} | {r['status']} |")
    lines.append("")

    # Per-check notes.
    lines.append("## Per-check output (tail)")
    lines.append("")
    for r in results:
        lines.append(f"### {r['name']} — {r['status']}")
        lines.append(f"```\n{r['output_tail'][-800:]}\n```")
        lines.append("")

    lines.append("## Notes")
    lines.append("")
    lines.append("- The unittest suite uses `unittest discover` (standard library).")
    if not pytest_available:
        lines.append("- pytest was **not available**; `unittest discover` was used instead.")
    lines.append("- `smoke_web.py` and `capture_ui_evidence.py` start a local server on "
                 "127.0.0.1:8787 but do **not** call the model.")
    lines.append("- No cloud inference, no external API, no internet required.")
    lines.append("- No fabricated benchmark numbers.")

    LOG_PATH.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n{'='*60}")
    print(f"Validation log: {LOG_PATH}")
    print(f"Overall: {'PASS' if overall_ok else 'FAIL'}")
    return 0 if overall_ok else 1


if __name__ == "__main__":
    sys.exit(main())
