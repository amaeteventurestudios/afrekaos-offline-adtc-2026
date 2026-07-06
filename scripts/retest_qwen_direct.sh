#!/usr/bin/env bash
#
# retest_qwen_direct.sh
# AfrekaOS Offline - Task 002C Qwen3 direct-answer retest.
#
# Retests qwen3-1.7b-q4-k-m with non-thinking / direct-answer controls to fix
# the Task 002B failure (thinking mode consumed the whole token budget).
#
# Controls:
#   AFREKAOS_QWEN_NO_THINK=1   append /no_think to Qwen prompts (soft switch)
#   --jinja --chat-template-file templates/qwen3_nonthinking.jinja  (hard switch)
#
# Binary resolution: LLAMA_CPP_BIN if set; else prefer llama-completion (it
# supports -no-cnv and --chat-template-file), then llama-cli, then llama.
#
# Outputs land under artifacts/eval/model-bakeoff/task-002C/.
# Fully offline. stdin redirected from /dev/null so the script cannot hang.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
OUT_DIR="${REPO_ROOT}/artifacts/eval/model-bakeoff/task-002C"
mkdir -p "${OUT_DIR}"

MODEL="${AFREKAOS_MODEL_PATH:-${REPO_ROOT}/model/candidates/qwen3-1.7b-q4-k-m.gguf}"
TEMPLATE="${REPO_ROOT}/templates/qwen3_nonthinking.jinja"
NOTES="${OUT_DIR}/qwen3-1.7b-direct-runtime-notes.md"
NOW="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"

# --- Resolve llama binary ----------------------------------------------------
resolve_llama_bin() {
  if [ -n "${LLAMA_CPP_BIN:-}" ]; then
    if [ -x "${LLAMA_CPP_BIN}" ] || [ -f "${LLAMA_CPP_BIN}" ]; then
      echo "${LLAMA_CPP_BIN}"; return 0
    fi
    return 2
  fi
  local found
  # Prefer llama-completion: it supports -no-cnv (clean single-turn) and
  # --chat-template-file, avoiding the conversation-mode runaway seen in 002B.
  found="$(command -v llama-completion 2>/dev/null || true)"
  if [ -n "${found}" ]; then echo "${found}"; return 0; fi
  found="$(command -v llama-cli 2>/dev/null || true)"
  if [ -n "${found}" ]; then echo "${found}"; return 0; fi
  found="$(command -v llama 2>/dev/null || true)"
  if [ -n "${found}" ]; then echo "${found}"; return 0; fi
  return 2
}

# Detect binary name (for notes).
bin_kind() {
  case "$(basename "$1")" in
    llama-completion) echo "llama-completion" ;;
    llama-cli)        echo "llama-cli" ;;
    llama)            echo "llama" ;;
    *)                echo "unknown" ;;
  esac
}

# Detect whether the binary supports --chat-template-file + --jinja.
supports_template() {
  local bin="$1"
  "$bin" --help 2>&1 | grep -q -- "--chat-template-file" || return 1
  "$bin" --help 2>&1 | grep -q -- "--jinja" || return 1
  return 0
}

# Detect whether the binary supports -no-cnv (clean single-turn).
supports_no_cnv() {
  local bin="$1"
  "$bin" --help 2>&1 | grep -q -- "-no-cnv" || return 1
  return 0
}

# --- Read prompts ------------------------------------------------------------
read_prompt() {
  python3 - "$1" <<'PY'
import json, sys
from pathlib import Path
meta = json.loads(Path("metadata.json").read_text(encoding="utf-8"))
print(meta["test_prompts"][int(sys.argv[1])]["prompt"])
PY
}

SMOKE_PROMPT='A small shop has low sales, missing fast-moving stock, supplier delay, and more customers asking for credit. Give a short operating checklist.'

# --- Header ------------------------------------------------------------------
echo "AfrekaOS Offline - Task 002C Qwen3 direct-answer retest"
echo "========================================================"

if [ ! -f "${MODEL}" ]; then
  echo "ERROR: model file not found: ${MODEL}" >&2
  exit 2
fi

if ! LLAMA_BIN="$(resolve_llama_bin 2>/dev/null)"; then
  echo "ERROR: no llama.cpp binary available. Set LLAMA_CPP_BIN." >&2
  exit 2
fi

BKIND="$(bin_kind "${LLAMA_BIN}")"
NO_THINK_ON="${AFREKAOS_QWEN_NO_THINK:-0}"
if [ "${NO_THINK_ON}" = "1" ]; then NO_THINK_USED="yes"; else NO_THINK_USED="no"; fi

# Template (hard switch) usable only if binary supports it AND file exists.
TEMPLATE_USED="no"
TEMPLATE_REASON=""
TEMPLATE_ARGS=()
if [ -f "${TEMPLATE}" ]; then
  if supports_template "${LLAMA_BIN}"; then
    TEMPLATE_USED="yes"
    TEMPLATE_ARGS=(--jinja --chat-template-file "${TEMPLATE}")
  else
    TEMPLATE_REASON="binary does not support --chat-template-file/--jinja"
  fi
else
  TEMPLATE_REASON="template file missing"
fi

# -no-cnv only safe for llama-completion (llama-cli rejects it).
NO_CNV_ARGS=()
if [ "${BKIND}" = "llama-completion" ] && supports_no_cnv "${LLAMA_BIN}"; then
  NO_CNV_ARGS=(-no-cnv)
fi

echo "model         : ${MODEL}"
echo "binary        : ${LLAMA_BIN} (${BKIND})"
echo "/no_think     : ${NO_THINK_USED}"
echo "template      : ${TEMPLATE_USED}"
[ -n "${TEMPLATE_REASON}" ] && echo "template note: ${TEMPLATE_REASON}"
echo

# --- Build prompt with optional soft switch ----------------------------------
build_prompt() {
  local base="$1"
  if [ "${NO_THINK_USED}" = "yes" ]; then
    printf '%s /no_think' "${base}"
  else
    printf '%s' "${base}"
  fi
}

# --- Run one prompt ----------------------------------------------------------
# $1 = tag, $2 = prompt text, $3 = output file
run_one() {
  local tag="$1" base="$2" out="$3"
  local prompt
  prompt="$(build_prompt "${base}")"
  echo ">>> ${tag}"
  echo "    -> ${out}"
  set +e
  "${LLAMA_BIN}" -m "${MODEL}" "${TEMPLATE_ARGS[@]}" "${NO_CNV_ARGS[@]}" \
    -p "${prompt}" -n "${MAX_TOKENS:-256}" -t 4 --temp 0.7 < /dev/null > "${out}" 2>&1
  local rc=$?
  set -e
  if [ ${rc} -ne 0 ]; then
    echo "    -> run failed (rc=${rc}); see ${out}"
  fi
  echo
}

P1="$(read_prompt 0)"
P2="$(read_prompt 1)"

run_one "prompt-1" "${P1}" "${OUT_DIR}/qwen3-1.7b-direct-prompt-1.txt"
run_one "prompt-2" "${P2}" "${OUT_DIR}/qwen3-1.7b-direct-prompt-2.txt"
run_one "smoke"    "${SMOKE_PROMPT}" "${OUT_DIR}/qwen3-1.7b-direct-smoke.txt"

# --- Per-output analysis for the notes ---------------------------------------
analyze_for_notes() {
  local f="$1"
  python3 - "$f" <<'PY'
import re, sys
from pathlib import Path
f = Path(sys.argv[1])
text = f.read_text(encoding="utf-8", errors="replace") if f.is_file() else ""
has_open = "<think>" in text
has_close = "</think>" in text
# visible answer = everything outside <think>...</think> blocks
no_think = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
# also drop a leading think block that never closed
no_think = re.sub(r"<think>.*", "", no_think, flags=re.DOTALL)
visible = no_think.strip()
# drop llama.cpp log lines for the char count
visible_clean = "\n".join(
    ln for ln in visible.splitlines()
    if not ln.startswith("0.") and "common_perf_print" not in ln and "I " not in ln[:6]
).strip()
print(f"think_open={has_open} think_close={has_close} answer_chars={len(visible_clean)}")
print(f"answer_preview={visible_clean[:200]!r}")
PY
}

declare -a NOTES_LINES
P1_INFO="$(analyze_for_notes "${OUT_DIR}/qwen3-1.7b-direct-prompt-1.txt")"
P1_PREV="$(analyze_for_notes "${OUT_DIR}/qwen3-1.7b-direct-prompt-1.txt" | tail -1)"
P2_INFO="$(analyze_for_notes "${OUT_DIR}/qwen3-1.7b-direct-prompt-2.txt")"
SM_INFO="$(analyze_for_notes "${OUT_DIR}/qwen3-1.7b-direct-smoke.txt")"

# Scrape timing from each output file.
scrape() { grep -Eo "$1" "$2" 2>/dev/null | tail -n1 || true; }
TPS1="$(scrape '[0-9]+\.[0-9]+ tokens per second' "${OUT_DIR}/qwen3-1.7b-direct-prompt-1.txt")"
PE1="$(grep -E "prompt eval time" "${OUT_DIR}/qwen3-1.7b-direct-prompt-1.txt" | tail -1 | grep -Eo '[0-9]+\.[0-9]+ tokens per second' || true)"
MEM1="$(grep -E "host memory" "${OUT_DIR}/qwen3-1.7b-direct-prompt-1.txt" | tail -1 || true)"

# --- Write notes --------------------------------------------------------------
{
  echo "# Task 002C - Qwen3 Direct-Answer Runtime Notes"
  echo
  echo "- **Date/time:** ${NOW}"
  echo "- **Model path:** ${MODEL}"
  echo "- **llama binary:** ${LLAMA_BIN}"
  echo "- **Binary kind:** ${BKIND} (llama-completion / llama-cli / llama)"
  echo "- **/no_think used:** ${NO_THINK_USED}"
  echo "- **Custom template used:** ${TEMPLATE_USED}"
  [ -n "${TEMPLATE_REASON}" ] && echo "- **Template reason:** ${TEMPLATE_REASON}"
  [ "${#TEMPLATE_ARGS[@]}" -gt 0 ] && echo "- **Template args:** ${TEMPLATE_ARGS[*]}"
  [ "${#NO_CNV_ARGS[@]}" -gt 0 ] && echo "- **-no-cnv used:** yes (clean single-turn)"
  echo
  echo "## Per-prompt result"
  echo
  echo "- **prompt-1:** ${P1_INFO}"
  echo "- **prompt-2:** ${P2_INFO}"
  echo "- **smoke:** ${SM_INFO}"
  echo
  echo "## <think> presence"
  echo
  P1_THINK="$(echo "${P1_INFO}" | grep -oE 'think_open=\w+')"
  P2_THINK="$(echo "${P2_INFO}" | grep -oE 'think_open=\w+')"
  SM_THINK="$(echo "${SM_INFO}" | grep -oE 'think_open=\w+')"
  echo "- prompt-1: ${P1_THINK}"
  echo "- prompt-2: ${P2_THINK}"
  echo "- smoke: ${SM_THINK}"
  echo
  echo "## Usable answer text outside <think>"
  echo
  echo "- prompt-1 answer_chars: $(echo "${P1_INFO}" | grep -oE 'answer_chars=[0-9]+')"
  echo "- prompt-2 answer_chars: $(echo "${P2_INFO}" | grep -oE 'answer_chars=[0-9]+')"
  echo "- smoke answer_chars: $(echo "${SM_INFO}" | grep -oE 'answer_chars=[0-9]+')"
  echo
  echo "## Visible timing / TPS / memory (from actual llama.cpp output)"
  echo
  [ -n "${TPS1}" ] && echo "- prompt-1 generation tokens/sec: ${TPS1}" || echo "- prompt-1 generation tokens/sec: (not found)"
  [ -n "${PE1}" ] && echo "- prompt-1 prompt-eval tokens/sec: ${PE1}" || echo "- prompt-1 prompt-eval tokens/sec: (not found)"
  [ -n "${MEM1}" ] && echo "- memory: ${MEM1}" || echo "- memory: (not reported in this run)"
  echo "- Run scripts/analyze_qwen_outputs.py for the viability verdict."
  echo
  echo "## Artifacts"
  echo
  echo "- ${OUT_DIR}/qwen3-1.7b-direct-prompt-1.txt"
  echo "- ${OUT_DIR}/qwen3-1.7b-direct-prompt-2.txt"
  echo "- ${OUT_DIR}/qwen3-1.7b-direct-smoke.txt"
  echo
  echo "No fabricated numbers. All stats above are scraped from real llama.cpp output."
} > "${NOTES}"

echo "Retest complete. Notes: ${NOTES}"
echo "Run: python3 scripts/analyze_qwen_outputs.py"
