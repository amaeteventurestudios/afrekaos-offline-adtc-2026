#!/usr/bin/env bash
#
# run_smoke_prompt.sh
# AfrekaOS Offline - Task 002A runtime smoke test.
#
# Runs ONE short SME operations prompt through llama.cpp to confirm the local
# runtime path works end-to-end. Fully offline: no internet, no external API.
#
# Overrides:
#   LLAMA_CPP_BIN          path to the llama.cpp binary (e.g. llama-cli / main)
#   AFREKAOS_MODEL_PATH    path to the GGUF model (default: model/afrekaos.gguf)
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
MODEL_PATH="${AFREKAOS_MODEL_PATH:-${REPO_ROOT}/model/afrekaos.gguf}"
LLAMA_BIN="${LLAMA_CPP_BIN:-}"

PROMPT='A small shop has low sales, missing fast-moving stock, supplier delay, and more customers asking for credit. Give a short operating checklist.'

echo "AfrekaOS Offline - runtime smoke test"
echo "--------------------------------------"

# --- Preconditions -----------------------------------------------------------

if [ -z "${LLAMA_BIN}" ]; then
  echo "ERROR: LLAMA_CPP_BIN is not set. Configure it to a llama.cpp binary" >&2
  echo "       (e.g. 'export LLAMA_CPP_BIN=/usr/local/bin/llama-cli')." >&2
  exit 2
fi

if [ ! -x "${LLAMA_BIN}" ] && [ ! -f "${LLAMA_BIN}" ]; then
  echo "ERROR: llama.cpp binary not found at: ${LLAMA_BIN}" >&2
  exit 2
fi

if [ ! -f "${MODEL_PATH}" ]; then
  echo "ERROR: model file not found at: ${MODEL_PATH}" >&2
  echo "       The model URL is not locked yet. See download_model.sh." >&2
  exit 2
fi

echo "model   : ${MODEL_PATH}"
echo "binary  : ${LLAMA_BIN}"
echo "prompt  : ${PROMPT}"
echo

# --- Run --------------------------------------------------------------------
# Tokens kept small; this is a connectivity smoke test, not a benchmark.
"${LLAMA_BIN}" \
  -m "${MODEL_PATH}" \
  -p "${PROMPT}" \
  -n 128 \
  -t 4 \
  --temp 0.7

echo
echo "Smoke test completed."
