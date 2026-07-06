#!/usr/bin/env bash
#
# profile_model.sh
# AfrekaOS Offline - profiler.
#
# Runs BOTH canonical metadata test prompts through llama.cpp and records
# outputs + runtime notes under artifacts/eval/. Fully offline.
#
# Model resolution order:
#   1. CANDIDATE_MODEL_PATH (bake-off override, if set and non-empty)
#   2. AFREKAOS_MODEL_PATH  (runtime override, if set and non-empty)
#   3. model/afrekaos.gguf  (canonical default)
#
# Binary:
#   LLAMA_CPP_BIN if set; otherwise llama-cli / llama from PATH.
#
# If the model or binary is missing, this script still writes a runtime notes
# file recording that state (no fabricated numbers).
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

resolve_model_path() {
  if [ -n "${CANDIDATE_MODEL_PATH:-}" ]; then
    echo "${CANDIDATE_MODEL_PATH}"; return
  fi
  if [ -n "${AFREKAOS_MODEL_PATH:-}" ]; then
    echo "${AFREKAOS_MODEL_PATH}"; return
  fi
  echo "${REPO_ROOT}/model/afrekaos.gguf"
}

MODEL_PATH="$(resolve_model_path)"

candidate_id_for_path() {
  local p="$1"
  python3 - "${p}" "${REPO_ROOT}" <<'PY'
import json, sys
from pathlib import Path
chosen, repo_root = Path(sys.argv[1]), Path(sys.argv[2])
data_path = Path("model.candidates.json")
if not data_path.is_file():
    print(""); sys.exit(0)
try:
    data = json.loads(data_path.read_text(encoding="utf-8"))
except Exception:
    print(""); sys.exit(0)
try:
    chosen_abs = chosen.resolve() if chosen.is_absolute() else (repo_root / chosen).resolve()
except Exception:
    print(""); sys.exit(0)
for c in data.get("candidates", []):
    cand_abs = (repo_root / c["local_candidate_path"]).resolve()
    if cand_abs == chosen_abs:
        print(c["id"]); sys.exit(0)
print("")
PY
}

resolve_llama_bin() {
  if [ -n "${LLAMA_CPP_BIN:-}" ]; then
    if [ -x "${LLAMA_CPP_BIN}" ] || [ -f "${LLAMA_CPP_BIN}" ]; then
      echo "${LLAMA_CPP_BIN}"; return 0
    fi
    return 2
  fi
  local found
  # Prefer llama-completion for bounded single-turn completion (see task-002B).
  found="$(command -v llama-completion 2>/dev/null || true)"
  if [ -n "${found}" ]; then echo "${found}"; return 0; fi
  found="$(command -v llama-cli 2>/dev/null || true)"
  if [ -n "${found}" ]; then echo "${found}"; return 0; fi
  found="$(command -v llama 2>/dev/null || true)"
  if [ -n "${found}" ]; then echo "${found}"; return 0; fi
  return 2
}

EVAL_DIR="${REPO_ROOT}/artifacts/eval"
mkdir -p "${EVAL_DIR}"

OUT1="${EVAL_DIR}/task-002A-prompt-1-output.txt"
OUT2="${EVAL_DIR}/task-002A-prompt-2-output.txt"
NOTES="${EVAL_DIR}/task-002A-runtime-notes.md"

NOW="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"

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

CAND_ID="$(candidate_id_for_path "${MODEL_PATH}")"

echo "AfrekaOS Offline - profiler"
echo "----------------------------"
[ -n "${CAND_ID}" ] && echo "candidate id : ${CAND_ID}" || echo "candidate id : (unknown / canonical)"
echo "model path   : ${MODEL_PATH}"

MODEL_OK="no"; BIN_OK="no"
[ -f "${MODEL_PATH}" ] && MODEL_OK="yes"
if LLAMA_BIN="$(resolve_llama_bin 2>/dev/null)"; then BIN_OK="yes"; else LLAMA_BIN="<unavailable>"; fi

P1_DONE="no"; P2_DONE="no"

if [ "${MODEL_OK}" = "yes" ] && [ "${BIN_OK}" = "yes" ]; then
  echo "binary       : ${LLAMA_BIN}"
  echo "Running prompt 1..."
  set +e
  "${LLAMA_BIN}" -m "${MODEL_PATH}" -p "${PROMPT1}" -n 256 -t 4 --temp 0.7 2>&1 | tee "${OUT1}"
  RC1=${PIPESTATUS[0]}
  set -e
  [ "${RC1}" -eq 0 ] && P1_DONE="yes"

  echo "Running prompt 2..."
  set +e
  "${LLAMA_BIN}" -m "${MODEL_PATH}" -p "${PROMPT2}" -n 256 -t 4 --temp 0.7 2>&1 | tee "${OUT2}"
  RC2=${PIPESTATUS[0]}
  set -e
  [ "${RC2}" -eq 0 ] && P2_DONE="yes"
else
  {
    echo "[no model run] model_ok=${MODEL_OK} binary_ok=${BIN_OK}"
    echo "Model path: ${MODEL_PATH}"
    echo "Binary:     ${LLAMA_BIN}"
    echo "No benchmark was executed. Numbers are not fabricated."
  } > "${OUT1}"
  cp "${OUT1}" "${OUT2}"
fi

scrape_stat() { grep -Eo "$1" "$2" 2>/dev/null | tail -n1 || true; }

TPS1=""; TPS2=""
[ "${P1_DONE}" = "yes" ] && TPS1="$(scrape_stat '[0-9]+\.[0-9]+ tokens per second' "${OUT1}")"
[ "${P2_DONE}" = "yes" ] && TPS2="$(scrape_stat '[0-9]+\.[0-9]+ tokens per second' "${OUT2}")"

{
  echo "# Task 002A Runtime Notes"
  echo
  echo "- **Date/time:** ${NOW}"
  echo "- **Model path:** ${MODEL_PATH}"
  [ -n "${CAND_ID}" ] && echo "- **Candidate id:** ${CAND_ID}"
  echo "- **Model present:** ${MODEL_OK}"
  echo "- **llama.cpp binary:** ${LLAMA_BIN}"
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
    echo "> **Note:** No model exists at \`${MODEL_PATH}\`. State recorded only;"
    echo "> no benchmark numbers were fabricated."
  fi
} > "${NOTES}"

echo
echo "Profiler finished. Notes: ${NOTES}"
