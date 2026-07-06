#!/usr/bin/env bash
#
# run_smoke_prompt.sh
# AfrekaOS Offline - runtime smoke test.
#
# Runs ONE short SME operations prompt through llama.cpp to confirm the local
# runtime path works end-to-end. Fully offline: no internet, no external API.
#
# Model resolution order:
#   1. CANDIDATE_MODEL_PATH (bake-off override, if set and non-empty)
#   2. AFREKAOS_MODEL_PATH  (runtime override, if set and non-empty)
#   3. model/afrekaos.gguf  (canonical default)
#
# Binary:
#   LLAMA_CPP_BIN if set; otherwise llama-cli / llama from PATH.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

# --- Resolve model path ------------------------------------------------------
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

# Resolve a candidate id if the chosen path matches a known candidate.
candidate_id_for_path() {
  local p="$1"
  python3 - "${p}" "${REPO_ROOT}" <<'PY'
import json, os, sys
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

# --- Resolve llama binary ----------------------------------------------------
resolve_llama_bin() {
  if [ -n "${LLAMA_CPP_BIN:-}" ]; then
    if [ -x "${LLAMA_CPP_BIN}" ] || [ -f "${LLAMA_CPP_BIN}" ]; then
      echo "${LLAMA_CPP_BIN}"; return 0
    fi
    echo "ERROR: LLAMA_CPP_BIN set but not found: ${LLAMA_CPP_BIN}" >&2
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
  echo "ERROR: no llama.cpp binary found. Set LLAMA_CPP_BIN or put llama-cli on PATH." >&2
  return 2
}

PROMPT='A small shop has low sales, missing fast-moving stock, supplier delay, and more customers asking for credit. Give a short operating checklist.'

echo "AfrekaOS Offline - runtime smoke test"
echo "--------------------------------------"

CAND_ID="$(candidate_id_for_path "${MODEL_PATH}")"
if [ -n "${CAND_ID}" ]; then
  echo "candidate id : ${CAND_ID}"
else
  echo "candidate id : (unknown / canonical)"
fi
echo "model path   : ${MODEL_PATH}"
echo "override     : ${CANDIDATE_MODEL_PATH:+CANDIDATE_MODEL_PATH}${AFREKAOS_MODEL_PATH:+AFREKAOS_MODEL_PATH}${CANDIDATE_MODEL_PATH:+${AFREKAOS_MODEL_PATH:-}}${CANDIDATE_MODEL_PATH:-${AFREKAOS_MODEL_PATH:-default}}"

# --- Preconditions -----------------------------------------------------------

if [ ! -f "${MODEL_PATH}" ]; then
  echo "ERROR: model file not found at: ${MODEL_PATH}" >&2
  if [ "${MODEL_PATH}" = "${REPO_ROOT}/model/afrekaos.gguf" ]; then
    echo "       The model URL is not locked yet. Run the bake-off or" >&2
    echo "       CANDIDATE=qwen3-1.7b-q4-k-m ./download_model.sh" >&2
  fi
  exit 2
fi

if ! LLAMA_BIN="$(resolve_llama_bin)"; then
  exit 2
fi

echo "binary       : ${LLAMA_BIN}"
echo "prompt       : ${PROMPT}"
echo

# --- Run --------------------------------------------------------------------
"${LLAMA_BIN}" \
  -m "${MODEL_PATH}" \
  -p "${PROMPT}" \
  -n 128 \
  -t 4 \
  --temp 0.7

echo
echo "Smoke test completed."
