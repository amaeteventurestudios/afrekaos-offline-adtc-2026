# Tasks — AfrekaOS Offline (001)

Status legend: `[ ]` pending · `[~]` in progress · `[x]` done

## Task 001 — Repository skeleton (this file's task)

- [x] Create directory structure (`model/`, `app/`, `data/*`, `scripts/`,
      `tests/`, `artifacts/*`, `specs/001-afrekaos-offline/`).
- [x] `metadata.json` with product, domain, runtime, model path placeholder, and
      exactly two test prompts.
- [x] `download_model.sh` safe placeholder (creates `model/`, executable, no
      fetch).
- [x] `REPORT.md` draft (Problem, African SME context, Offline design, Model and
      runtime, Retrieval layer, Limitations, How to run).
- [x] `README.md` (public ADTC-style edition, local-first thesis, no overclaim).
- [x] `SCORING.md` scoring discipline note.
- [x] `.gitignore` (model, gguf, venv, pycache, DS_Store; ignore generated JSON
      in artifacts but not markdown evidence).
- [x] `LICENSE`.
- [x] Spec kit: `spec.md`, `plan.md`, `tasks.md`, `research.md`,
      `data-model.md`, `quickstart.md`.
- [x] Placeholder corpus notes under `data/` (public, challenge-safe).
- [x] Initialize git, set remote, branch `main`, commit, push.

## Task 002A — Runtime baseline (complete)

- [x] `app/runtime_config.py` — `DEFAULT_MODEL_PATH`, `AFREKAOS_MODEL_PATH`,
      `LLAMA_CPP_BIN` overrides, helpers `get_model_path()`,
      `get_llama_binary()`, `model_exists()`, `runtime_summary()`.
      Dependency-free.
- [x] `scripts/check_metadata.py` — validates product name, domain, model path,
      exactly two non-empty prompts; exits non-zero on violations.
- [x] `scripts/run_smoke_prompt.sh` — executable; one AfrekaOS prompt through
      llama.cpp; checks model + binary; offline only.
- [x] `scripts/profile_model.sh` — executable; both canonical prompts; writes
      outputs + notes under `artifacts/eval/`; no fabricated numbers.
- [x] `tests/test_metadata_contract.py`, `tests/test_runtime_config.py` —
      standard-library-only tests.
- [x] README "Runtime Baseline" section; REPORT "Task 002A" section.
- [x] Validation run (metadata check + direct Python test run).

## Task 002B — Model bake-off (complete)

- [x] `model.candidates.json` — Qwen-first bake-off: qwen3-1.7b (primary),
      qwen3-4b (secondary), granite-4.1-3b (control); canonical winner path
      `model/afrekaos.gguf`; prohibited-use boundaries.
- [x] `scripts/check_model_candidates.py` — validates 3 candidates, roles,
      local paths under `model/candidates/`, winner path, prohibited-use.
- [x] `download_model.sh` rewritten — candidate acquisition via `CANDIDATE=`,
      `FORCE=1`, llama.cpp `-hf` preferred, manual fallback; no cloud inference.
- [x] `scripts/run_smoke_prompt.sh`, `scripts/profile_model.sh` updated for
      candidate mode (`CANDIDATE_MODEL_PATH` override, candidate id printed).
- [x] `scripts/profile_candidates.sh` — bake-off profiler writing under
      `artifacts/eval/model-bakeoff/`; missing-model notes; no fabricated numbers.
- [x] `artifacts/eval/model-bakeoff/rubric.md` — 0-3 scorecard.
- [x] `tests/test_model_candidates.py` — standard-library-only tests.
- [x] README / REPORT / SCORING updated with bake-off rationale.
- [x] Winner: **unresolved** (no candidate present locally; no `model.lock.json`).

## Task 002C — Qwen direct-answer mode retest (complete)

- [x] `templates/qwen3_nonthinking.jinja` + `templates/README.md` — force
      Qwen3 non-thinking / direct-answer mode (template equivalent of
      `enable_thinking=False`); offline-only; no CoT shown to user.
- [x] `scripts/retest_qwen_direct.sh` — executable; retests qwen3-1.7b on the
      three bake-off prompts with template + `/no_think`; stdin from `/dev/null`;
      writes outputs + runtime notes under `artifacts/eval/model-bakeoff/task-002C/`.
- [x] `scripts/analyze_qwen_outputs.py` — dependency-free analyzer; reports
      `<think>` presence, visible answer char count, PASS/FAIL/INCONCLUSIVE.
- [x] `scripts/profile_candidates.sh` updated — Qwen-aware: applies
      `AFREKAOS_QWEN_NO_THINK=1` + non-thinking template only to Qwen
      candidates; records `/no_think`, template, `<think>` presence, usable text.
- [x] `tests/test_qwen_direct_mode.py` — validates artifacts exist; analyzer
      handles missing files and think/answer logic.
- [x] `artifacts/eval/task-002C-qwen-direct-mode.md` evidence doc.
- [x] Real retest run: direct mode eliminated `<think>` (analyzer PASS, 3/3);
      prompt-2 + smoke usable; prompt-1 derailed (recorded as unresolved).
- [x] **Winner: qwen3-1.7b-q4-k-m** locked as first canonical model.
      `model.lock.json` created; `model/afrekaos.gguf` → relative symlink.

## Future tasks (sketched)

### 002D — Fallback / comparison model testing (open)

- [ ] If the prompt-1 derailment cannot be tamed, acquire and test
      `qwen2.5-3b-instruct-q4-k-m` (no thinking-mode trap) or `qwen3-4b-q4-k-m`.
- [ ] Acquire `granite-4.1-3b-q4-k-m` control for comparison.
- [ ] Re-profile on the target Ubuntu 22.04 / 8 GB hardware.
- [ ] Harden system prompt / stop tokens for reliable direct SME answers.

### 003 — Retrieval layer (open)

- [ ] Define the SQLite FTS5 schema (see `data-model.md`).
- [ ] Index the public SME operations corpus in `data/`.
- [ ] Wire retrieval into the reasoning path.

### 004 — Local browser app

- [ ] Localhost server scaffolding (no external deps).
- [ ] Operator flows: inventory, cashflow, credit, supplier, staffing,
      expansion.
- [ ] Yoruba mode (language target).

### 005 — Evaluation and submission

- [ ] Run the two test prompts and capture outputs.
- [ ] Package submission artifacts under `artifacts/submission/`.
