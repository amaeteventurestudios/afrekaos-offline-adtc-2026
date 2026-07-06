# Task 002B — Model Bake-Off (Evidence)

> AfrekaOS Offline. Qwen-first bake-off. This document records what was
> actually done and observed locally. No fabricated numbers.

## Candidate list

| id | repo | quant | role | local path |
|----|------|-------|------|------------|
| `qwen3-1.7b-q4-k-m` | `bartowski/Qwen_Qwen3-1.7B-GGUF` | Q4_K_M | primary speed candidate | `model/candidates/qwen3-1.7b-q4-k-m.gguf` |
| `qwen3-4b-q4-k-m` | `bartowski/Qwen_Qwen3-4B-GGUF` | Q4_K_M | secondary reasoning candidate | `model/candidates/qwen3-4b-q4-k-m.gguf` |
| `granite-4.1-3b-q4-k-m` | `ibm-granite/granite-4.1-3b-GGUF` | Q4_K_M | control baseline | `model/candidates/granite-4.1-3b-q4-k-m.gguf` |

Source of truth: `model.candidates.json`. Contract checker: `scripts/check_model_candidates.py` (passes).

## Why Qwen is first

AfrekaOS needs **fast, practical, checklist-style** responses for everyday SME
operators. The small/fast Qwen candidate is the default to beat on speed and
responsiveness. Granite is kept **only as a conservative control baseline**, not
as a default. This reverses any earlier intent to lock Granite as the default.

## Canonical winner path

`model/afrekaos.gguf` — to be filled **only** after a winner is explicitly
locked via `model.lock.json`. It is **not** filled by this task.

## What was actually validated locally

- `model.candidates.json` and the candidate contract checker pass.
- `download_model.sh` was rewritten into a candidate acquisition script
  (`CANDIDATE=…`, `FORCE=1`, prefers llama.cpp `-hf`, prints manual fallback).
- `check_model_candidates.py`, `profile_candidates.sh`, the rubric/scorecard,
  and `tests/test_model_candidates.py` all added and passing.
- The bake-off profiler (`profile_candidates.sh`) ran successfully end-to-end.

## Whether each candidate file exists locally

| Candidate | Present locally |
|-----------|-----------------|
| qwen3-1.7b-q4-k-m | **yes** (1.2 GB, acquired via direct HuggingFace download) |
| qwen3-4b-q4-k-m | no |
| granite-4.1-3b-q4-k-m | no |

`model/afrekaos.gguf`: **absent** (no winner promoted).

> Note on acquisition: `llama-cli -hf` resolved the candidate by its id-based
> filename, which does not match Bartowski's actual repo filenames
> (`Qwen_Qwen3-1.7B-Q4_K_M.gguf`). The primary candidate was instead acquired
> via a direct download from the HuggingFace resolve URL and placed at the
> canonical candidate path. `download_model.sh` retains the `-hf` path and a
> manual-command fallback for the remaining candidates.

## Whether `LLAMA_CPP_BIN` was available

- `LLAMA_CPP_BIN` env var: **unset**.
- The runtime scripts resolve a binary from PATH, preferring
  `llama-completion` (see below), then `llama-cli`, then `llama`.
- Binary used: `/usr/local/bin/llama-completion` (llama.cpp build 9700).

## Whether `llama-cli` / `llama` were found in PATH

- `/usr/local/bin/llama-cli`: **yes**
- `/usr/local/bin/llama`: **yes**
- `/usr/local/bin/llama-completion`: **yes** (preferred for single-turn runs)

## Whether smoke/profile ran real inference

**Yes — for qwen3-1.7b only.** The other two candidates had no local file, so
the profiler wrote missing-model notes for them (no fabricated numbers).

Real numbers observed for qwen3-1.7b (from actual `common_perf_print` output;
run on the **development** Darwin x86_64 machine, NOT the target Ubuntu
hardware, so these are not final target-hardware numbers):

| Run | prompt eval (tok/s) | generation (tok/s) | tokens generated |
|-----|---------------------|--------------------|------------------|
| prompt-1 | 27.70 | 5.11 | 95 |
| prompt-2 | 24.09 | 5.29 | ~95 |
| smoke    | 23.91 | 5.74 | ~95 |

Projected host memory for the model: ~5410 MiB (fits the 8 GB target).

## Answer-quality notes (from actual outputs)

- Across **all three** runs, qwen3-1.7b's output stayed **entirely inside the
  `<think>` block**. The model never emitted the actual SME checklist or
  advice — its thinking mode consumed the full token budget (`-n 96`), then hit
  EOF ("`> EOF by user`").
- Practical consequence: **no usable user-visible SME answer** was produced at
  this configuration. This is a hard floor failure for AfrekaOS, which needs
  practical checklist-style output.
- The model's hidden reasoning was cautious and relevant (it correctly
  identified stock/credit/supplier linkages), but that never reached the user.
- No output made any accounting/banking/tax/payroll/ERP claim. No cloud call
  was observed.

### Two runtime bugs found and fixed during the bake-off

1. **Conversation-mode runaway.** `llama-cli` defaults to conversation mode and
   (with Qwen3, no clean EOS trigger) generated a runaway ~315 MB–458 MB output
   stream in early attempts. `llama-cli` itself reports: *"-no-conversation is
   not supported by llama-cli, please use llama-completion instead."* Fix: the
   runtime scripts now **prefer `llama-completion`** for bounded single-turn
   completion.
2. **Interactive stdin stealing the loop's input.** `llama-completion` defaults
   to interactive mode and reads stdin; when invoked inside the profiler's
   `while read` loop it consumed the candidate list, so only the first candidate
   was processed. Fix: inference calls now redirect stdin from `/dev/null`.

Both fixes are in `scripts/run_smoke_prompt.sh`, `scripts/profile_model.sh`, and
`scripts/profile_candidates.sh`.

## Winner

**Unresolved.** Only one candidate ran, and it failed the practical-answer
floor (thinking mode ate the token budget; 0 on practical SME reasoning and
checklist clarity — see `artifacts/eval/model-bakeoff/scorecard.md`). The other
two candidates have no local evidence. **No `model.lock.json` was created.**

### What would resolve it (Task 002C)

- Disable Qwen3 thinking (`/no_think`) or use a non-thinking variant, and/or
  raise the token budget, then re-score qwen3-1.7b.
- Acquire and run qwen3-4b and/or granite on the **target Ubuntu 22.04 / 8 GB**
  hardware for a real comparison.
- Only then, if evidence clearly supports a winner, promote it to
  `model/afrekaos.gguf` and create `model.lock.json`.

## Boundaries respected

No UI, no SQLite retrieval, no FastAPI, no cloud inference, no external API,
no private/customer/banking/payroll/tax data, no ERP claim. No model was
auto-promoted. Product name and the two metadata prompts were unchanged.

## Runtime artifact paths created

- `artifacts/eval/model-bakeoff/summary.md`
- `artifacts/eval/model-bakeoff/rubric.md`
- `artifacts/eval/model-bakeoff/scorecard.md`
- `artifacts/eval/model-bakeoff/qwen3-1.7b-q4-k-m-prompt-1.txt`
- `artifacts/eval/model-bakeoff/qwen3-1.7b-q4-k-m-prompt-2.txt`
- `artifacts/eval/model-bakeoff/qwen3-1.7b-q4-k-m-smoke.txt`
- `artifacts/eval/model-bakeoff/qwen3-4b-q4-k-m-prompt-1.txt` (missing-model note)
- `artifacts/eval/model-bakeoff/qwen3-4b-q4-k-m-prompt-2.txt` (missing-model note)
- `artifacts/eval/model-bakeoff/qwen3-4b-q4-k-m-smoke.txt` (missing-model note)
- `artifacts/eval/model-bakeoff/granite-4.1-3b-q4-k-m-prompt-1.txt` (missing-model note)
- `artifacts/eval/model-bakeoff/granite-4.1-3b-q4-k-m-prompt-2.txt` (missing-model note)
- `artifacts/eval/model-bakeoff/granite-4.1-3b-q4-k-m-smoke.txt` (missing-model note)
