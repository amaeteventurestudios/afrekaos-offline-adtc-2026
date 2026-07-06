#!/usr/bin/env python3
"""Analyze Task 002C Qwen direct-answer outputs.

Inspects the three retest output files under
artifacts/eval/model-bakeoff/task-002C/ and reports, per file:
  - whether <think> appears
  - whether </think> appears
  - whether there is visible answer text after </think> (or outside think blocks)
  - approximate answer character count outside think blocks
  - whether the answer appears empty or mostly hidden reasoning

Viability verdict:
  - PASS  : at least 2 of 3 outputs produce useful visible answer text
  - FAIL  : outputs remain trapped in thinking mode
  - INCONCLUSIVE : files are missing

Dependency-free. Does not require the model, llama.cpp, or internet.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "artifacts" / "eval" / "model-bakeoff" / "task-002C"

FILES = [
    ("prompt-1", OUT_DIR / "qwen3-1.7b-direct-prompt-1.txt"),
    ("prompt-2", OUT_DIR / "qwen3-1.7b-direct-prompt-2.txt"),
    ("smoke", OUT_DIR / "qwen3-1.7b-direct-smoke.txt"),
]

# Heuristic: llama.cpp log lines and banner noise to exclude from the visible
# answer char count. These are NOT user-facing answer text.
LOG_RE = re.compile(
    r"^(?:[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+|I |W |L |---|>|=|system_info|"
    r"sampler|generate|llama_|common_|chat template|interactive|"
    r"Press|To return|If you want|Not using|"
    r"repeat_last_n|dry_|top_k|top_p|min_p|xtc_|typical_p|top_n_sigma|"
    r"mirostat|adaptive_|frequency_penalty|presence_penalty|repeat_penalty)",
    re.IGNORECASE,
)

# Timestamped log line prefix (e.g. "0.24.055.128 I common_perf_print: ...").
TIMESTAMP_LOG_RE = re.compile(r"^\d+\.\d+\.\d+\.\d+\s+[IWL]\s")

# Minimum visible answer length to count as "useful". Tuned for short
# checklist-style answers; below this the answer is effectively empty.
MIN_USEFUL_CHARS = 60


def _strip_logs(text: str) -> str:
    lines = []
    for ln in text.splitlines():
        s = ln.strip()
        if LOG_RE.match(s):
            continue
        if TIMESTAMP_LOG_RE.match(ln):
            continue
        lines.append(ln)
    return "\n".join(lines).strip()


def visible_answer(text: str) -> str:
    """Return text outside any <think>...</think> blocks (and unclosed <think>)."""
    # Remove closed think blocks.
    out = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    # Remove an unclosed trailing think block.
    out = re.sub(r"<think>.*", "", out, flags=re.DOTALL)
    return _strip_logs(out)


def analyze_file(label: str, path: Path) -> dict:
    if not path.is_file():
        return {
            "label": label,
            "path": str(path),
            "exists": False,
            "think_open": None,
            "think_close": None,
            "answer_chars": 0,
            "answer_preview": "",
            "useful": False,
        }
    raw = path.read_text(encoding="utf-8", errors="replace")
    think_open = "<think>" in raw
    think_close = "</think>" in raw
    answer = visible_answer(raw)
    useful = len(answer) >= MIN_USEFUL_CHARS
    return {
        "label": label,
        "path": str(path),
        "exists": True,
        "think_open": think_open,
        "think_close": think_close,
        "answer_chars": len(answer),
        "answer_preview": answer[:200],
        "useful": useful,
    }


def verdict(results: list[dict]) -> str:
    if not all(r["exists"] for r in results):
        return "INCONCLUSIVE"
    useful_count = sum(1 for r in results if r["useful"])
    if useful_count >= 2:
        return "PASS"
    return "FAIL"


def main() -> int:
    results = [analyze_file(label, path) for label, path in FILES]
    v = verdict(results)

    print("Qwen3 Direct-Mode Output Analysis (Task 002C)")
    print("=" * 48)
    for r in results:
        print(f"\n[{r['label']}] {r['path']}")
        if not r["exists"]:
            print("  MISSING FILE")
            continue
        print(f"  exists            : yes")
        print(f"  <think> present   : {r['think_open']}")
        print(f"  </think> present  : {r['think_close']}")
        print(f"  answer chars      : {r['answer_chars']}")
        print(f"  useful (>={MIN_USEFUL_CHARS}): {r['useful']}")
        prev = r["answer_preview"].replace("\n", " ")
        print(f"  answer preview    : {prev!r}")

    useful_count = sum(1 for r in results if r["useful"])
    print("\n" + "=" * 48)
    print(f"useful outputs: {useful_count}/3")
    print(f"VIABILITY: {v}")
    if v == "PASS":
        print("  -> qwen3-1.7b produced visible answers in direct mode; viable candidate.")
    elif v == "FAIL":
        print("  -> outputs remain trapped in thinking mode or empty; not viable here.")
    else:
        print("  -> retest outputs missing; run scripts/retest_qwen_direct.sh first.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
