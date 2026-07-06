#!/usr/bin/env bash
#
# profile_candidates.sh
# AfrekaOS Offline - Task 002B bake-off profiler.
#
# Reads model.candidates.json and, for each candidate, runs both metadata test
# prompts plus one AfrekaOS smoke prompt through llama.cpp. Outputs land under
# artifacts/eval/model-bakeoff/. Fully offline.
#
# For candidates whose local file is missing, a missing-model note is written
# instead. No numbers are fabricated.
#
# Binary:
#   LLAMA_CPP_BIN if set; otherwise llama-cli / llama from PATH.
#

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
BAKEOFF_DIR="${REPO_ROOT}/artifacts/eval/model-bakeoff"
mkdir -p "${BAKEOFF_DIR}"

SMOKE_PROMPT='A small shop has low sales, missing fast-moving stock, supplier delay, and more customers asking for credit. Give a short operating checklist.'

resolve_llama_bin() {
  if [ -n "${LLAMA_CPP_BIN:-}" ]; then
    if [ -x "${LLAMA_CPP_BIN}" ] || [ -f "${LLAMA_CPP_BIN}" ]; then
      echo "${LLAMA_CPP_BIN}"; return 0
    fi
    return 2
  fi
  local found
  # Prefer llama-completion for bounded single-turn completion: llama-cli runs
  # in conversation mode and (with Qwen3) can loop without an EOS-triggering
  # chat template, producing runaway output. See task-002B-model-bakeoff.md.
  found="$(command -v llama-completion 2>/dev/null || true)"
  if [ -n "${found}" ]; then echo "${found}"; return 0; fi
  found="$(command -v llama-cli 2>/dev/null || true)"
  if [ -n "${found}" ]; then echo "${found}"; return 0; fi
  found="$(command -v llama 2>/dev/null || true)"
  if [ -n "${found}" ]; then echo "${found}"; return 0; fi
  return 2
}

read_prompt() {
  python3 - "$1" <<'PY'
import json, sys
from pathlib import Path
meta = json.loads(Path("metadata.json").read_text(encoding="utf-8"))
print(meta["test_prompts"][int(sys.argv[1])]["prompt"])
PY
}

# Iterate candidates from JSON. Print: "<id>\t<local_path>\t<family>"
# family is "qwen" for any id containing "qwen", else "other". Used to decide
# whether to apply /no_think and the qwen3 non-thinking template.
candidate_rows() {
  python3 - "${REPO_ROOT}" <<'PY'
import json, sys
from pathlib import Path
repo_root = Path(sys.argv[1])
data = json.loads((repo_root / "model.candidates.json").read_text(encoding="utf-8"))
for c in data["candidates"]:
    fam = "qwen" if "qwen" in c["id"].lower() else "other"
    print(f"{c['id']}\t{repo_root / c['local_candidate_path']}\t{fam}")
PY
}

NOW="$(date -u '+%Y-%m-%d %H:%M:%S UTC')"

if LLAMA_BIN="$(resolve_llama_bin 2>/dev/null)"; then
  BIN_OK="yes"
else
  BIN_OK="no"; LLAMA_BIN="<unavailable>"
fi

PROMPT1="$(read_prompt 0)"
PROMPT2="$(read_prompt 1)"

# Qwen direct-mode controls (Task 002C). Applied only to Qwen candidates.
QWEN_TEMPLATE="${REPO_ROOT}/templates/qwen3_nonthinking.jinja"
QWEN_NO_THINK_ON="${AFREKAOS_QWEN_NO_THINK:-0}"

# Detect whether the resolved binary supports --chat-template-file + --jinja.
qwen_template_supported() {
  [ "${BIN_OK}" = "yes" ] || return 1
  [ -f "${QWEN_TEMPLATE}" ] || return 1
  "${LLAMA_BIN}" --help 2>&1 | grep -q -- "--chat-template-file" || return 1
  "${LLAMA_BIN}" --help 2>&1 | grep -q -- "--jinja" || return 1
  return 0
}

# Build Qwen-specific extra args. Returns 0 if any controls were applied.
QWEN_TMPL_USED_GLOBAL="no"
build_qwen_args() {
  local family="$1"
  QWEN_EXTRA=()
  QWEN_USED_NOTHINK="no"
  QWEN_USED_TMPL="no"
  [ "${family}" = "qwen" ] || return 0
  # Template (hard switch) first.
  if qwen_template_supported; then
    QWEN_EXTRA+=(--jinja --chat-template-file "${QWEN_TEMPLATE}")
    QWEN_USED_TMPL="yes"
    QWEN_TMPL_USED_GLOBAL="yes"
  fi
  # -no-cnv only for llama-completion (llama-cli rejects it).
  if [ "$(basename "${LLAMA_BIN}")" = "llama-completion" ]; then
    "${LLAMA_BIN}" --help 2>&1 | grep -q -- "-no-cnv" && QWEN_EXTRA+=(-no-cnv)
  fi
  return 0
}

echo "AfrekaOS Offline - model bake-off (Task 002B + 002C direct mode)"
echo "=================================================================="
echo "binary        : ${LLAMA_BIN} (ok=${BIN_OK})"
echo "bakeoff dir   : ${BAKEOFF_DIR}"
echo "no_think env  : ${QWEN_NO_THINK_ON}"
echo

run_prompt_to_file() {
  # $1 = model path, $2 = prompt, $3 = output file, $4 = candidate family
  #
  # IMPORTANT: stdin is redirected from /dev/null for the inference call.
  # llama-completion / llama-cli default to interactive mode and read stdin;
  # if they inherit the loop's stdin they consume the candidate list and only
  # the first candidate gets processed. See task-002B-model-bakeoff.md.
  local model="$1" prompt="$2" out="$3" family="${4:-other}"
  local qargs=()
  if [ "${BIN_OK}" != "yes" ]; then
    echo "[no run] no llama.cpp binary available." > "${out}"
    return 1
  fi
  # Apply Qwen direct-mode controls (soft + hard switch).
  build_qwen_args "${family}"
  qargs=("${QWEN_EXTRA[@]}")
  # Soft switch: append /no_think to the prompt for Qwen if enabled.
  if [ "${family}" = "qwen" ] && [ "${QWEN_NO_THINK_ON}" = "1" ]; then
    prompt="${prompt} /no_think"
  fi
  set +e
  "${LLAMA_BIN}" -m "${model}" "${qargs[@]}" -p "${prompt}" -n "${MAX_TOKENS:-256}" -t 4 --temp 0.7 < /dev/null > "${out}" 2>&1
  local rc=$?
  set -e
  return ${rc}
}

# Track per-candidate state for the summary.
declare -a S_IDS S_PRESENT S_P1 S_P2 S_SMOKE

while IFS=$'\t' read -r cid local_path family; do
  family="${family:-other}"
  echo ">>> ${cid} (family=${family})"
  echo "    local path: ${local_path}"
  present="no"; p1="no"; p2="no"; sm="no"
  if [ -f "${local_path}" ]; then
    present="yes"
    echo "    -> candidate file present; running prompts."
    run_prompt_to_file "${local_path}" "${PROMPT1}" "${BAKEOFF_DIR}/${cid}-prompt-1.txt" "${family}" && p1="yes"
    run_prompt_to_file "${local_path}" "${PROMPT2}" "${BAKEOFF_DIR}/${cid}-prompt-2.txt" "${family}" && p2="yes"
    run_prompt_to_file "${local_path}" "${SMOKE_PROMPT}" "${BAKEOFF_DIR}/${cid}-smoke.txt" "${family}" && sm="yes"
  else
    echo "    -> candidate file MISSING; writing missing-model note."
    for tag in prompt-1 prompt-2 smoke; do
      cat > "${BAKEOFF_DIR}/${cid}-${tag}.txt" <<EOF
[missing model] candidate=${cid}
file=${local_path}
No inference was run because the candidate GGUF is absent.
No benchmark numbers were fabricated.
EOF
    done
  fi
  S_IDS+=("${cid}"); S_PRESENT+=("${present}"); S_P1+=("${p1}"); S_P2+=("${p2}"); S_SMOKE+=("${sm}")
  echo
done < <(candidate_rows)

# --- Summary -----------------------------------------------------------------

scrape() { grep -Eo "$1" "$2" 2>/dev/null | tail -n1 || true; }

{
  echo "# AfrekaOS Offline - Model Bake-Off Summary (Task 002B + 002C)"
  echo
  echo "- **Date/time:** ${NOW}"
  echo "- **llama.cpp binary:** ${LLAMA_BIN}"
  echo "- **Binary available:** ${BIN_OK}"
  echo "- **AFREKAOS_QWEN_NO_THINK:** ${QWEN_NO_THINK_ON}"
  echo "- **Qwen non-thinking template used:** ${QWEN_TMPL_USED_GLOBAL}"
  echo
  echo "## Smoke prompt"
  echo
  echo "> ${SMOKE_PROMPT}"
  echo
  echo "## Candidate matrix"
  echo
  echo "| Candidate | File present | Prompt 1 | Prompt 2 | Smoke |"
  echo "|-----------|--------------|----------|----------|-------|"
  n=${#S_IDS[@]}
  for ((i=0;i<n;i++)); do
    printf '| %s | %s | %s | %s | %s |\n' \
      "${S_IDS[$i]}" "${S_PRESENT[$i]}" "${S_P1[$i]}" "${S_P2[$i]}" "${S_SMOKE[$i]}"
  done
  echo
  echo "## Direct-mode checks (Qwen, Task 002C)"
  echo
  echo "- /no_think appended to Qwen prompts: ${QWEN_NO_THINK_ON}"
  echo "- custom template applied to Qwen runs: ${QWEN_TMPL_USED_GLOBAL}"
  # Did any Qwen output still contain <think>?
  any_think="no"
  for ((i=0;i<n;i++)); do
    cid="${S_IDS[$i]}"
    for tag in prompt-1 prompt-2 smoke; do
      f="${BAKEOFF_DIR}/${cid}-${tag}.txt"
      if [ -f "${f}" ] && grep -q "<think>" "${f}"; then any_think="yes"; fi
    done
  done
  echo "- any output still containing <think>: ${any_think}"
  # Did any Qwen output produce visible answer text outside <think>?
  usable="no"
  for ((i=0;i<n;i++)); do
    cid="${S_IDS[$i]}"
    [ "${S_PRESENT[$i]}" = "yes" ] || continue
    cnt=0
    for tag in prompt-1 prompt-2 smoke; do
      f="${BAKEOFF_DIR}/${cid}-${tag}.txt"
      if [ -f "${f}" ]; then
        ac="$(python3 - "${f}" <<'PY'
import re, sys
from pathlib import Path
t = Path(sys.argv[1]).read_text(encoding="utf-8", errors="replace") if Path(sys.argv[1]).is_file() else ""
o = re.sub(r"<think>.*?</think>", "", t, flags=re.DOTALL)
o = re.sub(r"<think>.*", "", o, flags=re.DOTALL)
o = "\n".join(l for l in o.splitlines() if not l.startswith("0.") and "common_perf" not in l and "I " not in l[:6]).strip()
print(len(o))
PY
)"
        [ "${ac:-0}" -ge 60 ] && cnt=$((cnt+1))
      fi
    done
    [ "${cnt}" -ge 2 ] && usable="yes"
  done
  echo "- any candidate with usable answer text in >=2/3 outputs: ${usable}"
  echo
  echo "## Timing / token stats (from actual llama.cpp output)"
  echo
  any_tps=0
  for ((i=0;i<n;i++)); do
    cid="${S_IDS[$i]}"
    if [ "${S_P1[$i]}" = "yes" ] || [ "${S_P2[$i]}" = "yes" ] || [ "${S_SMOKE[$i]}" = "yes" ]; then
      any_tps=1
      tps1="$(scrape '[0-9]+\.[0-9]+ tokens per second' "${BAKEOFF_DIR}/${cid}-prompt-1.txt")"
      tps2="$(scrape '[0-9]+\.[0-9]+ tokens per second' "${BAKEOFF_DIR}/${cid}-prompt-2.txt")"
      tpss="$(scrape '[0-9]+\.[0-9]+ tokens per second' "${BAKEOFF_DIR}/${cid}-smoke.txt")"
      echo "- ${cid}:"
      echo "    - prompt-1 tokens/sec: ${tps1:-(not found)}"
      echo "    - prompt-2 tokens/sec: ${tps2:-(not found)}"
      echo "    - smoke   tokens/sec: ${tpss:-(not found)}"
    fi
  done
  [ "${any_tps}" = "0" ] && echo "- No candidate produced runtime output; no timing/token stats available."
  echo
  echo "## Winner"
  echo
  echo "- **Status:** unresolved (see artifacts/eval/task-002B-model-bakeoff.md)"
  echo "- No winner is auto-selected. A winner is locked only after local evidence"
  echo "  is reviewed and model.lock.json is explicitly created."
  echo
  echo "## Notes"
  echo
  echo "- No cloud inference, no external API. Fully offline."
  echo "- Numbers above are scraped from actual llama.cpp output; nothing fabricated."
} > "${BAKEOFF_DIR}/summary.md"

echo "Bake-off complete. Summary: ${BAKEOFF_DIR}/summary.md"
