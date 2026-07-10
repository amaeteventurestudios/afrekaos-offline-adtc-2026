#!/usr/bin/env python3
"""Target inference benchmark for AfrekaOS Offline (Task 005C).

Runs bounded grounded inference for the two metadata prompts + smoke prompt on
the current machine, capturing wall-clock timing and llama.cpp's printed
TPS/memory. Standard library only. No cloud. No fabricated numbers.

Outputs: artifacts/submission/target-hardware-benchmark/
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

OUT_DIR = REPO_ROOT / "artifacts" / "submission" / "target-hardware-benchmark"

SMOKE_PROMPT = (
    "A small shop has low sales, missing fast-moving stock, supplier delay, "
    "and more customers asking for credit. Give a short operating checklist."
)

MAX_TOKENS = int(os.environ.get("AFREKAOS_TARGET_MAX_TOKENS", "256"))
TIMEOUT = int(os.environ.get("AFREKAOS_TARGET_TIMEOUT", "180"))

_THINK_RE = re.compile(r"<think>")


def _resolve_llama() -> str:
    for name in ("llama-completion", "llama-cli", "llama"):
        found = shutil.which(name)
        if found:
            return found
    return ""


def _supports_flag(binary: str, flag: str) -> bool:
    try:
        r = subprocess.run(
            [binary, "--help"], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            stdin=subprocess.DEVNULL, timeout=15, text=True,
        )
        return flag in (r.stdout or "")
    except Exception:
        return False


def _has_think_trap(text: str) -> bool:
    """Unclosed <think> with real content after last </think>."""
    after = text.rsplit("</think>", 1)[-1]
    return "<think>" in after and len(after.strip()) > 40


def _scrape(pattern: str, text: str) -> str:
    m = re.findall(pattern, text)
    return m[-1] if m else ""


def main() -> int:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Ensure retrieval index.
    db = REPO_ROOT / "data" / "afrekaos_fts.sqlite"
    if not db.is_file():
        print("[index missing] building...")
        from app import retrieval
        retrieval.build_index()

    # Load prompts.
    meta = json.loads((REPO_ROOT / "metadata.json").read_text(encoding="utf-8"))
    prompts = [
        ("prompt-1", meta["test_prompts"][0]["prompt"]),
        ("prompt-2", meta["test_prompts"][1]["prompt"]),
        ("smoke", SMOKE_PROMPT),
    ]

    binary = _resolve_llama()
    model_path = REPO_ROOT / "model" / "afrekaos.gguf"
    if not model_path.is_file():
        msg = f"[missing model] {model_path}\nCannot run benchmark.\n"
        (OUT_DIR / "runtime-notes.md").write_text(msg, encoding="utf-8")
        print(msg.strip(), file=sys.stderr)
        return 1
    if not binary:
        msg = "[missing llama binary] cannot run benchmark.\n"
        (OUT_DIR / "runtime-notes.md").write_text(msg, encoding="utf-8")
        print(msg.strip(), file=sys.stderr)
        return 1

    # Build Qwen direct-mode args.
    template = REPO_ROOT / "templates" / "qwen3_nonthinking.jinja"
    extra: list[str] = []
    if template.is_file() and _supports_flag(binary, "--chat-template-file"):
        extra += ["--jinja", "--chat-template-file", str(template)]
    if Path(binary).name == "llama-completion" and _supports_flag(binary, "-no-cnv"):
        extra += ["-no-cnv"]

    from app import prompt_context

    no_think = os.environ.get("AFREKAOS_QWEN_NO_THINK", "") == "1"
    results: list[dict] = []

    for tag, question in prompts:
        prompt = prompt_context.build_grounded_prompt(question, limit=5)
        if no_think:
            prompt = f"{prompt} /no_think"
        out_file = OUT_DIR / f"{tag}-grounded.txt"

        print(f"\n>>> {tag} (bounded {MAX_TOKENS} tokens, timeout {TIMEOUT}s)")
        wall_start = time.time()
        timed_out = False
        rc = -1
        try:
            proc = subprocess.run(
                [binary, "-m", str(model_path)] + extra + [
                    "-p", prompt, "-n", str(MAX_TOKENS), "-t", "4", "--temp", "0.7",
                ],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                timeout=TIMEOUT,
                text=True,
            )
            rc = proc.returncode
            output = proc.stdout or ""
        except subprocess.TimeoutExpired:
            timed_out = True
            output = (proc.stdout if isinstance(proc, bytes) else "") or ""
            if isinstance(output, bytes):
                output = output.decode("utf-8", errors="replace")
        except Exception as exc:
            output = f"[error: {exc}]"
        wall = time.time() - wall_start

        out_file.write_text(output, encoding="utf-8")
        tps = _scrape(r"[0-9]+\.[0-9]+ tokens per second", output)
        pe_tps = _scrape_pattern(output, r"prompt eval time.*?([0-9]+\.[0-9]+) tokens per second")
        mem = ""
        for line in output.splitlines():
            if "host memory" in line.lower():
                mem = line.strip()
                break
        think_trap = _has_think_trap(output)

        r = {
            "tag": tag, "rc": rc, "timed_out": timed_out,
            "wall_seconds": round(wall, 2),
            "output_chars": len(output),
            "gen_tps": tps or "not found",
            "prompt_eval_tps": pe_tps or "not found",
            "memory": mem or "not found",
            "think_trap": think_trap,
        }
        results.append(r)
        print(f"    rc={rc} wall={wall:.1f}s chars={len(output)} "
              f"gen_tps={tps or '?'} think_trap={think_trap} timed_out={timed_out}")

    # --- runtime-notes.md ---
    notes = ["# Target Hardware Benchmark — Runtime Notes", ""]
    notes.append(f"- **Model:** {model_path}")
    notes.append(f"- **Binary:** {binary} ({Path(binary).name})")
    notes.append(f"- **No-think:** {no_think}")
    notes.append(f"- **Template:** {template.is_file()}")
    notes.append(f"- **Max tokens:** {MAX_TOKENS}, timeout: {TIMEOUT}s")
    notes.append("")
    notes.append("| Prompt | rc | wall (s) | chars | gen tps | think trap | timed out |")
    notes.append("|--------|----|----------|-------|---------|------------|-----------|")
    for r in results:
        notes.append(f"| {r['tag']} | {r['rc']} | {r['wall_seconds']} | "
                      f"{r['output_chars']} | {r['gen_tps']} | {r['think_trap']} | {r['timed_out']} |")
    notes.append("")
    notes.append("No fabricated numbers. All stats scraped from real llama.cpp output "
                 "or measured by Python wall-clock.")
    (OUT_DIR / "runtime-notes.md").write_text("\n".join(notes), encoding="utf-8")

    # --- benchmark-summary.md ---
    passed = all(r["rc"] == 0 and not r["timed_out"] and not r["think_trap"] for r in results)
    verdict = "PASS" if passed else "FAIL"
    summary = ["# Target Hardware Benchmark — Summary", ""]
    summary.append(f"- **Verdict:** {verdict}")
    summary.append(f"- **Prompts run:** {len(results)}")
    summary.append(f"- **All completed (rc=0, no timeout):** {all(r['rc'] == 0 and not r['timed_out'] for r in results)}")
    summary.append(f"- **Any think trap:** {any(r['think_trap'] for r in results)}")
    summary.append("")
    for r in results:
        summary.append(f"## {r['tag']}")
        summary.append(f"- rc: {r['rc']}")
        summary.append(f"- wall-clock: {r['wall_seconds']}s")
        summary.append(f"- output chars: {r['output_chars']}")
        summary.append(f"- generation tps: {r['gen_tps']}")
        summary.append(f"- prompt-eval tps: {r['prompt_eval_tps']}")
        summary.append(f"- memory: {r['memory']}")
        summary.append(f"- think trap: {r['think_trap']}")
        summary.append("")
    (OUT_DIR / "benchmark-summary.md").write_text("\n".join(summary), encoding="utf-8")

    print(f"\nVerdict: {verdict}")
    print(f"Outputs: {OUT_DIR}")
    return 0 if passed else 1


def _scrape_pattern(text: str, pattern: str) -> str:
    m = re.search(pattern, text, re.DOTALL)
    return m.group(1) if m else ""


if __name__ == "__main__":
    sys.exit(main())
