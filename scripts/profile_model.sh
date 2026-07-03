#!/usr/bin/env bash
#
# profile_model.sh
# AfrekaOS Offline - Task 002A profiler.
#
# Runs BOTH canonical metadata test prompts through llama.cpp and records
# outputs + runtime notes under artifacts/eval/. Fully offline.
#
# Overrides:
#   LLAMA_CPP_BIN          path to the llama.cpp binary
#   AFREKAOS_MODEL_PATH    path to the GGUF model (default: model/afrekaos.gguf)
#
# If the model or binary is missing, this script still writes a runtime notes
# file recording that state (no fabricated numbers).
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MODEL_PATH="${AFREKAOS_MODEL_PATH:-${REPO_ROOT}/model/afrekaos.gguf}"
LLAMA_BIN="${LLAMA_CPP_BIN:-}"

EVAL_DIR="${REPO_ROOT}/artifacts/eval"
mkdir -p "${EVAL_DIR}"

OUT1="${EVAL_DIR}/task-002A-prompt-1-output.txt"
OUT2="${EVAL_DIR}/task-002A-prompt-2-output.txt"
NOTES="${EVAL_DIR}/task-002A-runtime-notes.md"

NOW="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"

# Pull the two prompts out of metadata.json with python (stdlib only).
read_prompt() {
  local idx="$1"
  python3 - "$idx" <<'PY'
import json, sys
from pathlib import Path
meta = json.loads(Path("metadata.json").read_text(encoding="utf-8"))
print(meta["test_prompts"][int(sys.argv[1])]["prompt"])
PY
}

PROMPT1="$(read_prompt 0)"
PROMPT2="$(read_prompt 1)"

echo "AfrekaOS Offline - profiler (Task 002A)"
echo "----------------------------------------"

# Decide whether we can actually run.
MODEL_OK="no"
BIN_OK="no"
if [ -f "${MODEL_PATH}" ]; then MODEL_OK="yes"; fi
if [ -n "${LLAMA_BIN}" ] && [ -f "${LLAMA_BIN}" ]; then BIN_OK="yes"; fi

P1_DONE="no"
P2_DONE="no"

if [ "${MODEL_OK}" = "yes" ] && [ "${BIN_OK}" = "yes" ]; then
  echo "Running prompt 1..."
  # tee preserves output for the artifact while showing it inline.
  set +e
  "${LLAMA_BIN}" -m "${MODEL_PATH}" -p "${PROMPT1}" -n 256 -t 4 --temp 0.7 2>&1 | tee "${OUT1}"
  RC1=${PIPESTATUS[0]}
  set -e
  if [ "${RC1}" -eq 0 ]; then P1_DONE="yes"; fi

  echo "Running prompt 2..."
  set +e
  "${LLAMA_BIN}" -m "${MODEL_PATH}" -p "${PROMPT2}" -n 256 -t 4 --temp 0.7 2>&1 | tee "${OUT2}"
  RC2=${PIPESTATUS[0]}
  set -e
  if [ "${RC2}" -eq 0 ]; then P2_DONE="yes"; fi
else
  # Write marker files so the absence is explicit, not silent.
  {
    echo "[no model run] model_ok=${MODEL_OK} binary_ok=${BIN_OK}"
    echo "Model path: ${MODEL_PATH}"
    echo "Binary:     ${LLAMA_BIN:-<unset>}"
    echo "No benchmark was executed. Numbers are not fabricated."
  } > "${OUT1}"
  cp "${OUT1}" "${OUT2}"
fi

# --- Runtime notes -----------------------------------------------------------

# Try to scrape timing/token stats from llama.cpp output if present.
scrape_stat() {
  # $1 = regex, $2 = file
  grep -Eo "$1" "$2" 2>/dev/null | tail -n1 || true
}

TPS1=""; TPS2=""; MEM=""
if [ "${P1_DONE}" = "yes" ]; then
  TPS1="$(scrape_stat '[0-9]+\.[0-9]+ tokens per second' "${OUT1}")"
fi
if [ "${P2_DONE}" = "yes" ]; then
  TPS2="$(scrape_stat '[0-9]+\.[0-9]+ tokens per second' "${OUT2}")"
fi

{
  echo "# Task 002A Runtime Notes"
  echo
  echo "- **Date/time:** ${NOW}"
  echo "- **Model path:** ${MODEL_PATH}"
  echo "- **Model present:** ${MODEL_OK}"
  echo "- **llama.cpp binary:** ${LLAMA_BIN:-<not set>}"
  echo "- **Binary present:** ${BIN_OK}"
  echo
  echo "## Prompts"
  echo
  echo "- **Prompt 1** (daily_operations_triage):"
  echo "  > ${PROMPT1}"
  echo "- **Prompt 2** (expansion_readiness):"
  echo "  > ${PROMPT2}"
  echo
  echo "## Completion"
  echo
  echo "- Prompt 1 completed: ${P1_DONE}"
  echo "- Prompt 2 completed: ${P2_DONE}"
  echo
  echo "## Timing / token stats (as printed by llama.cpp)"
  echo
  if [ "${P1_DONE}" = "yes" ] || [ "${P2_DONE}" = "yes" ]; then
    [ -n "${TPS1}" ] && echo "- Prompt 1 tokens/sec: ${TPS1}" || echo "- Prompt 1 tokens/sec: (not found in output)"
    [ -n "${TPS2}" ] && echo "- Prompt 2 tokens/sec: ${TPS2}" || echo "- Prompt 2 tokens/sec: (not found in output)"
  else
    echo "- No model run executed; no timing/token stats available."
  fi
  echo
  echo "## Memory / TPS"
  echo
  if [ "${P1_DONE}" = "yes" ] || [ "${P2_DONE}" = "yes" ]; then
    echo "- Memory: see raw output files for any llama.cpp memory reporting."
    echo "- TPS: captured above where available."
  else
    echo "- Not available: no model run executed."
  fi
  echo
  echo "## Artifacts"
  echo
  echo "- ${OUT1}"
  echo "- ${OUT2}"
  echo
  if [ "${MODEL_OK}" = "no" ]; then
    echo "> **Note:** No model exists at \`${MODEL_PATH}\`. The model URL is not"
    echo "> locked yet. This run recorded state only; no benchmark numbers were"
    echo "> fabricated."
  fi
} > "${NOTES}"

echo
echo "Profiler finished. Notes: ${NOTES}"
