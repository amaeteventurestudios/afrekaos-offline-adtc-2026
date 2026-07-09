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

### 003A — SQLite FTS5 retrieval layer (complete)

- [x] `app/retrieval.py` — SQLite FTS5 module: `build_index`, `search`,
      `get_document`, `retrieval_summary`; BM25 ranking; clear failures if FTS5
      unavailable or index missing. Standard library only.
- [x] `app/prompt_context.py` — `build_context_block`, `build_grounded_prompt`
      (role + retrieved context + question + answer rules; forbids
      accounting/banking/payroll/tax/ERP claims and `<think>` blocks).
- [x] `scripts/build_retrieval_index.py`, `scripts/query_retrieval.py`,
      `scripts/preview_grounded_prompt.py`.
- [x] `tests/test_retrieval.py`, `tests/test_prompt_context.py` — temp-index
      tests; validate search relevance, missing-index behavior, prompt shape.
- [x] Index built: 8 documents (6 sme_operations + 1 language + 1 sources);
      FTS5 available.
- [x] Evidence: `artifacts/eval/task-003A-retrieval.md`,
      `artifacts/eval/task-003A-grounded-prompt-preview.md`.
- [x] README / REPORT / SCORING updated.

### 003B — Connect grounded prompts to model inference (complete)

- [x] `app/model_inference.py` — inference helper: `build_ungrounded_prompt`,
      `run_model`, `run_ungrounded`, `run_grounded`, `inference_summary`;
      prefers `llama-completion`; Qwen direct mode (`/no_think` + template +
      `-no-cnv`); stdin DEVNULL; bounded generation + subprocess timeout;
      structured result dicts. Standard library only.
- [x] `scripts/run_grounded_inference.py` — 6-run comparison (3 prompts ×
      grounded/ungrounded); bounded; writes outputs + runtime notes + comparison.
- [x] `scripts/analyze_grounded_outputs.py` — `<think>` trap detection (refined:
      empty template block ≠ trap), derailment terms, SME-term presence,
      PASS/FAIL/INCONCLUSIVE verdict.
- [x] `tests/test_model_inference.py`, `tests/test_grounded_output_analyzer.py`.
- [x] Real inference ran (all 6 runs); prompt-1 derailment resolved; analyzer
      verdict PASS. Grounded adds specificity + "stockout" term.
- [x] Evidence: `artifacts/eval/task-003B-grounded-inference.md` + outputs;
      scorecard updated (Task 003B note appended, 002C notes preserved).

### 003C — Corpus expansion and answer-quality tightening (open)

- [ ] Expand the public SME corpus for richer retrieval grounding.
- [ ] Tighten system prompt / stop tokens for more actionable checklists.
- [ ] Re-profile on target Ubuntu 22.04 / 8 GB hardware.

### 004A — Local browser UI (complete)

- [x] `app/web_app.py` — `http.server.ThreadingHTTPServer` at 127.0.0.1:8787;
      routes: `/`, `/advisor/{daily,inventory,cashflow}` (GET+POST),
      `/status`, `/health`; standard library only; bounded inference.
- [x] `app/web_templates.py` — HTML render helpers, embedded CSS, all user
      content escaped; no external CSS/JS/fonts/CDNs/images.
- [x] `scripts/run_local_web.sh` — executable; sets
      `AFREKAOS_QWEN_NO_THINK=1`; runs `python3 -m app.web_app`.
- [x] `scripts/smoke_web.py` — non-inference smoke test (no model required).
- [x] `tests/test_web_templates.py`, `tests/test_web_app.py`.
- [x] Smoke test passed; manual real-inference POST verified.
- [x] Evidence: `artifacts/eval/task-004A-local-web-ui.md`.

### 004B — UI polish and demo evidence (complete)

- [x] `app/web_templates.py` polished — offline status banner, top nav,
      stronger cards, improved layouts, unified boundary warning,
      `render_demo()` with 4 demo scenarios.
- [x] `app/web_app.py` updated — `GET /demo` route; advisor nav links.
- [x] `scripts/capture_ui_evidence.py` — captures all routes as HTML/JSON
      snapshots; verifies labels; optional bounded inference.
- [x] `tests/test_web_templates.py` (banner, demo, warning, nav),
      `tests/test_web_app.py` (demo route, no-cloud), `tests/test_ui_evidence.py`.
- [x] Evidence captured (7 files); smoke test passed.
- [x] Artifacts: `task-004B-ui-polish.md`, `task-004B-screenshot-instructions.md`,
      `task-004B-ui-evidence/` snapshots.

### 004C — Visual screenshots / target-hardware UI validation (open)

- [ ] Capture screenshots if GUI is available (instructions in
      `task-004B-screenshot-instructions.md`).
- [ ] Loading state for blocking inference.
- [ ] Yoruba-mode UI toggle.
- [ ] Re-validate on target Ubuntu 22.04 / 8 GB hardware.

### 005A — Final evaluation package (complete)

- [x] `scripts/final_validation.py` — runs all checks + unittest; writes
      `artifacts/submission/final-validation-log.md`.
- [x] `artifacts/submission/final-evaluation-package.md` — product/runtime/
      retrieval/UI/evidence/limitations/boundaries.
- [x] `artifacts/submission/final-demo-script.md` — 2–3 min demo script.
- [x] `artifacts/submission/final-runbook.md` — clone → validate → run.
- [x] `artifacts/submission/final-risk-register.md` — 8-row risk table.
- [x] `artifacts/submission/final-artifact-index.md` — evidence index.
- [x] README / REPORT / SCORING updated.

### 005B — Optional screenshots / demo video (open)

- [ ] Capture screenshots if GUI available.
- [ ] Optional demo video.

### 005C — Target Ubuntu 22.04 / 8 GB hardware retest (open)

- [ ] Re-profile model on target hardware.
- [ ] Re-validate UI + inference on target.
