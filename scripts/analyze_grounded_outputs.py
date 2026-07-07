#!/usr/bin/env python3
"""Analyze Task 003B grounded vs ungrounded inference outputs.

Inspects outputs under artifacts/eval/task-003B-grounded-inference/ and reports:
  - whether each output exists
  - whether each contains <think>
  - visible answer char count
  - whether prompt-1 grounded output stays on SME operations
  - whether prompt-1 grounded output contains derailment terms
  - whether grounded output uses retrieved SME context terms
  - PASS/FAIL/INCONCLUSIVE verdict on prompt-1 grounding

Dependency-free. No external services.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = REPO_ROOT / "artifacts" / "eval" / "task-003B-grounded-inference"

TAGS = ["prompt-1", "prompt-2", "smoke"]
MODES = ["ungrounded", "grounded"]

# Derailment terms from the Task 002C prompt-1 failure.
DERAILMENT_RE = re.compile(
    r"mendeleev|periodic table|electron config|atomic number|"
    r"electron configuration|period of the elements",
    re.IGNORECASE,
)

# SME operating terms we expect grounding to surface.
SME_TERMS = [
    "stockout", "supplier", "credit", "cash", "records",
    "inventory", "expansion", "staff",
]

# llama.cpp log line prefixes to exclude from visible answer char count.
# Matches both "0.03.738.563 I ..." and "I common_perf..." styles.
_LOG_PREFIX_RE = re.compile(
    r"^(?:\d+\.\d+\.\d+\.\d+\s+|"
    r"[IWL]\s+|"
    r"repeat_last_n|dry_|top_k|top_p|min_p|xtc_|typical_p|top_n_sigma|"
    r"mirostat|adaptive_|frequency_penalty|presence_penalty|repeat_penalty|"
    r"sampler|generate|llama_|common_|chat template|interactive|"
    r"Press|To return|If you want|Not using|system_info|"
    r"system prompt|warming up|threadpool|backend init|fitting params|"
    r"control-looking|load the model|llama_completion)",
    re.IGNORECASE,
)

# Also drop lines that are just the echoed prompt header (role/rules/context).
_PROMPT_HEADER_RE = re.compile(
    r"^(?:You are AfrekaOS|Operator question:|Answer rules:|Local SME operations context|"
    r"Answer:|\d+\.\s+\[|source:|Give practical|Stay strictly|Do NOT|"
    r"Do not invent|Do not include|Answer as|Where the operator)",
    re.IGNORECASE,
)

MIN_VISIBLE_CHARS = 60


def _read(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _has_thinking_trap(text: str) -> bool:
    """True only if there's an UNCLOSED <think> with real reasoning content.

    The non-thinking template emits an empty <think>\\n\\n</think> block (which
    is the intended direct-mode mechanism, NOT a trap). A real trap is an
    unclosed <think> followed by substantial reasoning with no </think>.
    Mere mentions of '<think>' in answer-rule text are also not a trap.
    """
    # Find all <think>...</think> pairs and remove them (these are fine).
    remaining = re.sub(r"<think>\s*</think>", "", text)
    # Also remove any rule lines that mention <think> as text.
    remaining = re.sub(r"<think>", "", remaining.split("</think>")[-1] if "</think>" in remaining else "")
    # After removing pairs, is there a leftover <think> with real content?
    # Re-check the full text for an unclosed <think>.
    after_last_close = text.rsplit("</think>", 1)[-1]
    return "<think>" in after_last_close and len(after_last_close.strip()) > 40


def _visible_answer(text: str) -> str:
    out = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    out = re.sub(r"<think>.*", "", out, flags=re.DOTALL)
    lines = []
    for ln in out.splitlines():
        s = ln.strip()
        if not s:
            continue
        if _LOG_PREFIX_RE.match(s):
            continue
        if _PROMPT_HEADER_RE.match(s):
            continue
        lines.append(ln)
    return "\n".join(lines).strip()


def analyze_output(path: Path) -> dict:
    raw = _read(path)
    if not raw and not path.is_file():
        return {"exists": False}
    answer = _visible_answer(raw)
    return {
        "exists": path.is_file(),
        "contains_think": _has_thinking_trap(raw),
        "visible_answer_chars": len(answer),
        "answer_preview": answer[:200],
        "has_derailment": bool(DERAILMENT_RE.search(answer)),
        "sme_terms_found": sorted(
            t for t in SME_TERMS if t.lower() in answer.lower()
        ),
    }


def analyze_all(out_dir: Path = OUT_DIR) -> dict:
    results = {}
    for tag in TAGS:
        results[tag] = {}
        for mode in MODES:
            results[tag][mode] = analyze_output(out_dir / f"{tag}-{mode}.txt")
    return results


def verdict(results: dict) -> str:
    """PASS/FAIL/INCONCLUSIVE based on prompt-1 grounded output."""
    try:
        p1g = results["prompt-1"]["grounded"]
    except KeyError:
        return "INCONCLUSIVE"
    if not p1g.get("exists"):
        return "INCONCLUSIVE"
    answer_chars = p1g.get("visible_answer_chars", 0)
    has_think = p1g.get("contains_think", False)
    has_derailment = p1g.get("has_derailment", False)
    sme_terms = p1g.get("sme_terms_found", [])

    if answer_chars < MIN_VISIBLE_CHARS:
        return "FAIL"
    if has_think:
        return "FAIL"
    if has_derailment:
        return "FAIL"
    if len(sme_terms) < 2:
        return "FAIL"
    return "PASS"


def main() -> int:
    results = analyze_all()
    v = verdict(results)

    print("AfrekaOS Grounded Output Analysis (Task 003B)")
    print("=" * 52)
    for tag in TAGS:
        for mode in MODES:
            r = results[tag][mode]
            label = f"{tag}-{mode}"
            if not r.get("exists"):
                print(f"\n[{label}] MISSING")
                continue
            print(f"\n[{label}]")
            print(f"  exists            : yes")
            print(f"  <think> present   : {r['contains_think']}")
            print(f"  visible chars     : {r['visible_answer_chars']}")
            print(f"  derailment terms  : {r['has_derailment']}")
            print(f"  sme terms found   : {', '.join(r['sme_terms_found']) or '(none)'}")
            prev = r["answer_preview"].replace("\n", " ")
            print(f"  answer preview    : {prev!r}")

    print("\n" + "=" * 52)
    print(f"PROMPT-1 GROUNDING VERDICT: {v}")
    if v == "PASS":
        print("  -> grounded prompt-1 produced visible SME answer, no <think>, "
              "no derailment, includes SME terms.")
    elif v == "FAIL":
        print("  -> grounded prompt-1 still derailed, empty, trapped in <think>, "
              "or lacks SME terms.")
    else:
        print("  -> output files missing; run scripts/run_grounded_inference.py first.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
