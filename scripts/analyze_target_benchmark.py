#!/usr/bin/env python3
"""Analyze target hardware benchmark outputs for AfrekaOS Offline (Task 005C).

Inspects artifacts/submission/target-hardware-benchmark/ and reports:
  - whether all three outputs exist
  - whether outputs contain thinking traps
  - whether outputs contain practical SME terms
  - whether outputs avoid derailment
  - whether outputs avoid forbidden product claims
  - PASS/FAIL/INCONCLUSIVE verdict

Writes: artifacts/submission/target-hardware-benchmark-analysis.md
Standard library only.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BENCH_DIR = REPO_ROOT / "artifacts" / "submission" / "target-hardware-benchmark"
OUT_PATH = REPO_ROOT / "artifacts" / "submission" / "target-hardware-benchmark-analysis.md"

FILES = ["prompt-1-grounded.txt", "prompt-2-grounded.txt", "smoke-grounded.txt"]

DERAILMENT_RE = re.compile(
    r"mendeleev|periodic table|electron config|atomic number|"
    r"electron configuration|period of the elements",
    re.IGNORECASE,
)

FORBIDDEN_RE = re.compile(
    r"\b(?:accounting software|banking software|tax software|"
    r"payroll software|erp system|lending platform)\b",
    re.IGNORECASE,
)

SME_TERMS = [
    "stockout", "supplier", "credit", "cash", "records",
    "inventory", "expansion", "staff",
]

_LOG_RE = re.compile(
    r"^(?:\d+\.\d+\.\d+\.\d+\s+|[IWL]\s+|"
    r"repeat_last_n|dry_|top_k|top_p|min_p|xtc_|typical_p|top_n_sigma|"
    r"mirostat|adaptive_|frequency_penalty|presence_penalty|repeat_penalty|"
    r"sampler|generate|llama_|common_|chat template|interactive|"
    r"Press|To return|If you want|Not using|system_info)",
    re.IGNORECASE,
)

_MIN_VISIBLE = 60


def _read(path: Path) -> str:
    if not path.is_file():
        return ""
    return path.read_text(encoding="utf-8", errors="replace")


def _visible(text: str) -> str:
    out = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    out = re.sub(r"<think>.*", "", out, flags=re.DOTALL)
    return "\n".join(
        ln for ln in out.splitlines()
        if ln.strip() and not _LOG_RE.match(ln.strip())
    ).strip()


def _think_trap(text: str) -> bool:
    after = text.rsplit("</think>", 1)[-1]
    return "<think>" in after and len(after.strip()) > 40


def _contains_think(text: str) -> bool:
    """True if any <think> marker appears (including the empty Qwen template).

    Distinct from _think_trap: the empty non-thinking template block contains
    <think> but is NOT a trap.
    """
    return "<think>" in text


_PROMPT_ECHO_MARKERS = (
    "You are AfrekaOS",
    "Local SME operations context",
    "Answer rules:",
    "Operator question:",
    "BEGIN FINAL OPERATING GUIDANCE",
)
_SOURCE_PATH_RE = re.compile(r"^\s*source:\s+\S+", re.IGNORECASE | re.MULTILINE)


def _prompt_echo(text: str) -> tuple[bool, str]:
    in_answer = any(m in text for m in _PROMPT_ECHO_MARKERS) or bool(
        _SOURCE_PATH_RE.search(text)
    )
    return in_answer, ("echo in answer" if in_answer else "clean")


def analyze_output(path: Path) -> dict:
    raw = _read(path)
    if not raw and not path.is_file():
        return {"exists": False}
    vis = _visible(raw)
    echo_detected, echo_status = _prompt_echo(vis)
    return {
        "exists": path.is_file(),
        "contains_think": _contains_think(raw),
        "think_trap": _think_trap(raw),
        "prompt_echo_detected": echo_detected,
        "prompt_echo_status": echo_status,
        "visible_chars": len(vis),
        "derailment": bool(DERAILMENT_RE.search(vis)),
        "forbidden_claim": bool(FORBIDDEN_RE.search(raw)),
        "sme_terms": sorted(t for t in SME_TERMS if t in vis.lower()),
    }


def analyze_all(bench_dir: Path = BENCH_DIR) -> dict:
    return {f: analyze_output(bench_dir / f) for f in FILES}


def verdict(results: dict) -> str:
    if not all(r.get("exists") for r in results.values()):
        return "INCONCLUSIVE"
    for r in results.values():
        if r.get("think_trap"):
            return "FAIL"
        if r.get("derailment"):
            return "FAIL"
        if r.get("forbidden_claim"):
            return "FAIL"
        if r.get("visible_chars", 0) < _MIN_VISIBLE:
            return "FAIL"
        if len(r.get("sme_terms", [])) < 2:
            return "FAIL"
    return "PASS"


def render(results: dict, v: str) -> str:
    lines = ["# Target Hardware Benchmark Analysis (Task 005C)", ""]
    lines.append(f"- **Verdict:** {v}")
    lines.append("")
    lines.append("## Per-output analysis")
    lines.append("")
    for f in FILES:
        r = results[f]
        lines.append(f"### {f}")
        if not r.get("exists"):
            lines.append("- MISSING")
            lines.append("")
            continue
        lines.append(f"- exists: yes")
        lines.append(f"- think trap: {r['think_trap']}")
        lines.append(f"- visible chars: {r['visible_chars']}")
        lines.append(f"- derailment: {r['derailment']}")
        lines.append(f"- forbidden claim: {r['forbidden_claim']}")
        lines.append(f"- sme terms: {', '.join(r['sme_terms']) or '(none)'}")
        lines.append("")
    lines.append("## Criteria")
    lines.append("")
    lines.append(f"- All 3 outputs must exist (else INCONCLUSIVE)")
    lines.append(f"- No think traps (unclosed <think> with real content)")
    lines.append(f"- No derailment terms (chemistry/MCQ)")
    lines.append(f"- No forbidden product claims (accounting/banking/tax/payroll/ERP/lending)")
    lines.append(f"- Visible answer >= {_MIN_VISIBLE} chars")
    lines.append(f"- At least 2 SME terms per output")
    return "\n".join(lines)


def main() -> int:
    results = analyze_all()
    v = verdict(results)
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(render(results, v), encoding="utf-8")
    print(render(results, v))
    print(f"\nAnalysis written to: {OUT_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
