#!/usr/bin/env python3
"""Run grounded vs ungrounded inference for AfrekaOS Offline (Task 003B).

For each of the two metadata prompts + the smoke prompt:
  - runs ungrounded inference (role + rules, no retrieval)
  - runs grounded inference (role + retrieved context + rules)

Outputs land under artifacts/eval/task-003B-grounded-inference/. Uses Qwen
direct-answer mode by default (/no_think + non-thinking template + -no-cnv).
Bounded generation + subprocess timeout to avoid runaway output. No cloud.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import model_inference, retrieval  # noqa: E402

OUT_DIR = REPO_ROOT / "artifacts" / "eval" / "task-003B-grounded-inference"
SMOKE_PROMPT = (
    "A small shop has low sales, missing fast-moving stock, supplier delay, "
    "and more customers asking for credit. Give a short operating checklist."
)

# Bounded generation to avoid runaway files.
MAX_TOKENS = int(__import__("os").environ.get("AFREKAOS_MAX_TOKENS", "256"))
TIMEOUT = int(__import__("os").environ.get("AFREKAOS_INFER_TIMEOUT", "150"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure the retrieval index exists.
    db = REPO_ROOT / retrieval.DEFAULT_DB_PATH
    index_built = False
    doc_count = 0
    if not db.is_file():
        print("[index missing] building retrieval index first...")
        try:
            summary = retrieval.build_index()
            index_built = True
            doc_count = summary["documents"]
            print(f"[index built] {doc_count} documents")
        except (RuntimeError, ValueError) as exc:
            print(f"ERROR: could not build index: {exc}", file=sys.stderr)
            return 2
    else:
        try:
            doc_count = retrieval.retrieval_summary()["documents"]
        except Exception:
            doc_count = 0

    # Pre-flight: model + binary.
    cfg = model_inference.inference_summary()
    if not cfg["model_exists"]:
        msg = (
            f"[missing model] {cfg['model_path']}\n"
            "Cannot run inference. No outputs generated.\n"
        )
        (OUT_DIR / "runtime-notes.md").write_text(
            f"# Task 003B Runtime Notes\n\n- {_now()}\n\n{msg}\n",
            encoding="utf-8",
        )
        print(msg.strip(), file=sys.stderr)
        return 1
    if not cfg["llama_binary"]:
        msg = "[missing llama binary] set LLAMA_CPP_BIN or install llama.cpp\n"
        (OUT_DIR / "runtime-notes.md").write_text(
            f"# Task 003B Runtime Notes\n\n- {_now()}\n\n{msg}\n",
            encoding="utf-8",
        )
        print(msg.strip(), file=sys.stderr)
        return 1

    meta = json.loads((REPO_ROOT / "metadata.json").read_text(encoding="utf-8"))
    prompts = [
        ("prompt-1", meta["test_prompts"][0]["prompt"]),
        ("prompt-2", meta["test_prompts"][1]["prompt"]),
        ("smoke", SMOKE_PROMPT),
    ]

    now = _now()
    results: list[dict] = []
    for tag, question in prompts:
        print(f"\n>>> {tag}")
        ungrounded = model_inference.run_ungrounded(
            question,
            output_path=str(OUT_DIR / f"{tag}-ungrounded.txt"),
            max_tokens=MAX_TOKENS,
            timeout_seconds=TIMEOUT,
        )
        grounded = model_inference.run_grounded(
            question,
            output_path=str(OUT_DIR / f"{tag}-grounded.txt"),
            max_tokens=MAX_TOKENS,
            timeout_seconds=TIMEOUT,
        )
        results.append(
            {
                "tag": tag,
                "question": question,
                "ungrounded": ungrounded,
                "grounded": grounded,
            }
        )
        print(
            f"    ungrounded: ok={ungrounded['ok']} think={ungrounded['contains_think']} "
            f"visible={ungrounded['visible_answer_chars']}"
        )
        print(
            f"    grounded  : ok={grounded['ok']} think={grounded['contains_think']} "
            f"visible={grounded['visible_answer_chars']}"
        )

    # --- runtime-notes.md ----------------------------------------------------
    _scrape = lambda pat, f: _grep(pat, OUT_DIR / f)

    notes = []
    notes.append("# Task 003B Runtime Notes")
    notes.append("")
    notes.append(f"- **Date/time:** {now}")
    notes.append(f"- **Model path:** {cfg['model_path']}")
    notes.append(f"- **llama binary:** {cfg['llama_binary']}")
    notes.append(f"- **Command family:** {cfg['command_family']}")
    notes.append(f"- **Index built this run:** {index_built}")
    notes.append(f"- **Documents indexed:** {doc_count}")
    notes.append(f"- **Qwen template present:** {cfg['qwen_template_present']}")
    notes.append(f"- **/no_think env (AFREKAOS_QWEN_NO_THINK):** {cfg['qwen_no_think_env']}")
    notes.append(f"- **Max tokens:** {MAX_TOKENS}, timeout: {TIMEOUT}s")
    notes.append("")
    notes.append("## Per-prompt comparison")
    notes.append("")
    notes.append("| Prompt | Mode | ok | <think> | visible chars | timed out |")
    notes.append("|--------|------|----|---------|---------------|-----------|")
    for r in results:
        for mode in ("ungrounded", "grounded"):
            d = r[mode]
            notes.append(
                f"| {r['tag']} | {mode} | {d['ok']} | {d['contains_think']} | "
                f"{d['visible_answer_chars']} | {d['timed_out']} |"
            )
    notes.append("")
    # Timing scraped from real output (prompt-1 grounded as a representative).
    notes.append("## Visible timing / TPS / memory (scraped from actual output)")
    notes.append("")
    any_timing = False
    for tag in ("prompt-1", "prompt-2", "smoke"):
        for mode in ("ungrounded", "grounded"):
            f = OUT_DIR / f"{tag}-{mode}.txt"
            tps = _grep(r"[0-9]+\.[0-9]+ tokens per second", f)
            if tps:
                any_timing = True
                notes.append(f"- {tag}-{mode} generation tokens/sec: {tps}")
    if not any_timing:
        notes.append("- No timing stats found in output.")
    notes.append("")
    notes.append("No fabricated numbers. All stats scraped from real llama.cpp output.")
    (OUT_DIR / "runtime-notes.md").write_text("\n".join(notes), encoding="utf-8")

    # --- comparison.md -------------------------------------------------------
    comp = []
    comp.append("# Task 003B Grounded vs Ungrounded Comparison")
    comp.append("")
    comp.append(f"- Generated: {now}")
    comp.append(f"- Model: {cfg['model_path']}")
    comp.append(f"- Binary: {cfg['llama_binary']} ({cfg['command_family']})")
    comp.append("")
    comp.append("## Summary table")
    comp.append("")
    comp.append("| Prompt | Mode | visible chars | <think> |")
    comp.append("|--------|------|---------------|---------|")
    for r in results:
        for mode in ("ungrounded", "grounded"):
            d = r[mode]
            comp.append(
                f"| {r['tag']} | {mode} | {d['visible_answer_chars']} | {d['contains_think']} |"
            )
    comp.append("")
    comp.append(
        "Run `python3 scripts/analyze_grounded_outputs.py` for the "
        "derailment/SME-term verdict on prompt-1."
    )
    (OUT_DIR / "comparison.md").write_text("\n".join(comp), encoding="utf-8")

    print(f"\nOutputs written under: {OUT_DIR}")
    return 0


def _grep(pattern: str, path: Path) -> str:
    import re

    if not path.is_file():
        return ""
    text = path.read_text(encoding="utf-8", errors="replace")
    m = re.findall(pattern, text)
    return m[-1] if m else ""


if __name__ == "__main__":
    sys.exit(main())
