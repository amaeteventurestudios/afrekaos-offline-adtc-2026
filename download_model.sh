#!/usr/bin/env bash
#
# download_model.sh
# AfrekaOS Offline - Task 002B candidate acquisition (Qwen-first bake-off).
#
# Source of truth: model.candidates.json
#
# This script acquires GGUF bake-off candidates into model/candidates/.
# It does NOT call OpenAI, Claude, GLM, or any cloud inference API.
# Acquisition uses llama.cpp's Hugging Face download ('-hf') when a usable
# llama binary is available; otherwise it prints exact manual commands.
#
# Env:
#   CANDIDATE   one of: qwen3-1.7b-q4-k-m | qwen3-4b-q4-k-m |
#               granite-4.1-3b-q4-k-m | all
#               (default: qwen3-1.7b-q4-k-m)
#   FORCE=1     overwrite an existing candidate file
#   LLAMA_CPP_BIN   path to a llama.cpp binary (e.g. llama-cli). If unset, the
#               script looks for llama-cli then llama in PATH.
#   SELECT_WINNER=1  (reserved) allow overwriting model/afrekaos.gguf after a
#               winner is explicitly chosen. This script does NOT auto-select.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="${SCRIPT_DIR}"
MODEL_DIR="${REPO_ROOT}/model"
CANDIDATES_DIR="${MODEL_DIR}/candidates"
CANDIDATES_JSON="${REPO_ROOT}/model.candidates.json"

CANDIDATE="${CANDIDATE:-qwen3-1.7b-q4-k-m}"

mkdir -p "${MODEL_DIR}" "${CANDIDATES_DIR}"

echo "AfrekaOS Offline - candidate acquisition (Qwen-first bake-off)"
echo "--------------------------------------------------------------"
echo "candidate : ${CANDIDATE}"
echo "force     : ${FORCE:-0}"
echo "source    : ${CANDIDATES_JSON}"
echo

if [ ! -f "${CANDIDATES_JSON}" ]; then
  echo "ERROR: ${CANDIDATES_JSON} not found." >&2
  exit 2
fi

# Resolve a usable llama binary: explicit override, then PATH search.
resolve_llama_bin() {
  if [ -n "${LLAMA_CPP_BIN:-}" ]; then
    if [ -x "${LLAMA_CPP_BIN}" ] || [ -f "${LLAMA_CPP_BIN}" ]; then
      echo "${LLAMA_CPP_BIN}"
      return 0
    fi
    echo "ERROR: LLAMA_CPP_BIN set but not found: ${LLAMA_CPP_BIN}" >&2
    return 2
  fi
  local found
  found="$(command -v llama-cli 2>/dev/null || true)"
  if [ -n "${found}" ]; then echo "${found}"; return 0; fi
  found="$(command -v llama 2>/dev/null || true)"
  if [ -n "${found}" ]; then echo "${found}"; return 0; fi
  return 1
}

# Pull a field for a candidate id from model.candidates.json (python stdlib).
cand_field() {
  local cid="$1" field="$2"
  python3 - "${cid}" "${field}" <<'PY'
import json, sys
from pathlib import Path
cid, field = sys.argv[1], sys.argv[2]
data = json.loads(Path("model.candidates.json").read_text(encoding="utf-8"))
for c in data["candidates"]:
    if c["id"] == cid:
        print(c[field])
        sys.exit(0)
print(f"ERROR: candidate {cid!r} not found in model.candidates.json", file=sys.stderr)
sys.exit(2)
PY
}

# Acquire one candidate by id.
acquire_candidate() {
  local cid="$1"
  local repo quant local_path
  repo="$(cand_field "${cid}" "repo")"
  quant="$(cand_field "${cid}" "quantization")"
  # local_candidate_path is repo-relative in the JSON.
  local rel
  rel="$(cand_field "${cid}" "local_candidate_path")"
  local_path="${REPO_ROOT}/${rel}"

  echo ">>> ${cid}"
  echo "    repo        : ${repo}"
  echo "    quant       : ${quant}"
  echo "    local path  : ${local_path}"

  if [ -f "${local_path}" ] && [ "${FORCE:-0}" != "1" ]; then
    echo "    -> already present (use FORCE=1 to re-acquire). Skipped."
    return 0
  fi

  local bin
  if bin="$(resolve_llama_bin 2>/dev/null)"; then
    echo "    binary      : ${bin}"
    echo "    mode        : llama.cpp Hugging Face acquisition (-hf)"
    # llama-cli -hf <repo>:<quant> is a download/convert helper in recent
    # llama.cpp builds. We pass -m to direct the resulting file to the
    # candidate path. Older builds may not support -hf acquisition; if so,
    # the command fails and we fall through to manual instructions below.
    set +e
    "${bin}" -hf "${repo}:${quant}" -m "${local_path}" 2>&1
    rc=$?
    set -e
    if [ ${rc} -ne 0 ]; then
      echo "    -> llama.cpp -hf acquisition failed (rc=${rc})." >&2
      echo "    -> Falling back to manual instructions." >&2
      print_manual "${repo}" "${quant}"
      return 3
    fi
    if [ -f "${local_path}" ]; then
      echo "    -> acquired: ${local_path}"
      return 0
    fi
    echo "    -> acquisition reported success but file is missing at ${local_path}" >&2
    print_manual "${repo}" "${quant}"
    return 3
  else
    echo "    mode        : no llama binary available"
    print_manual "${repo}" "${quant}"
    return 4
  fi
}

print_manual() {
  local repo="$1" quant="$2"
  cat <<EOF

    MANUAL ACQUISITION (no usable llama binary / -hf unavailable):

      # Option A: use llama.cpp Hugging Face pull directly
      llama-cli -hf ${repo}:${quant}

      # Option B: download the GGUF from Hugging Face, then place it here:
      #   <repo-relative> -> ${local_path:-model/candidates/<file>.gguf}

      Repo: https://huggingface.co/${repo}
      File suffix: *${quant}*.gguf

EOF
}

# --- Run --------------------------------------------------------------------

case "${CANDIDATE}" in
  all)
    for cid in qwen3-1.7b-q4-k-m qwen3-4b-q4-k-m granite-4.1-3b-q4-k-m; do
      acquire_candidate "${cid}" || true
      echo
    done
    ;;
  qwen3-1.7b-q4-k-m|qwen3-4b-q4-k-m|granite-4.1-3b-q4-k-m)
    acquire_candidate "${CANDIDATE}"
    ;;
  *)
    echo "ERROR: unknown CANDIDATE '${CANDIDATE}'." >&2
    echo "       Use one of: qwen3-1.7b-q4-k-m | qwen3-4b-q4-k-m | granite-4.1-3b-q4-k-m | all" >&2
    exit 2
    ;;
esac

echo
echo "Done."
echo "NOTE: model/afrekaos.gguf was NOT overwritten. To promote a winner, run"
echo "      the bake-off (./scripts/profile_candidates.sh) and explicitly lock"
echo "      the winner (SELECT_WINNER=1) in a later step."
