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

### 004C — Advisor submit & runtime feedback fix (complete); screenshots still open

- [x] Reproduced the broken submit path and documented root cause in
      `artifacts/eval/task-004C-ui-submit-fix.md` (synchronous blocking inference
      in the request handler; vague 500 page; CSS `content:"\2713 "` banner
      marker rendering as "13").
- [x] Advisor + demo forms verified: `method="POST"`, correct `action`,
      `textarea name="question"`, `button type="submit"`, escaped HTML, no
      external dependencies, work without JavaScript.
- [x] Client-side loading feedback (inline `<script>`, no external files):
      disables the submit button, changes text to "Running local model…", shows
      the 30–90s message; normal POST still works with JS off.
- [x] In-memory job flow: `POST /advisor/<name>` creates a job, starts a
      background thread, and immediately redirects (303) to `/job/<id>`.
      `GET /job/<id>` auto-refreshes every 3s while queued/running, shows
      ordered progress steps, the runtime status panel, and the final answer or
      a browser-friendly error. Jobs in memory only; never persisted; full
      question never logged.
- [x] Vague "500 — Server error" replaced with a friendly error page (summary,
      current route, suggested checks: model path / llama binary / timeout /
      terminal logs, nav links). Full traceback to terminal only.
- [x] Status banner fixed: explicit `✓` text in the HTML (CSS pseudo-element
      removed); tests assert `13 Offline mode` is absent on every page.
- [x] Status detail panel on job pages (model path exists, llama binary,
      retrieval index, locked candidate, local-only mode).
- [x] Tests added/updated: `tests/test_ui_submit_flow.py` (POST→303→job page,
      demo forms, banner, status panel, no real inference),
      `tests/test_web_templates.py` (loading feedback, job page, error page,
      banner checkmark, no "13"), `tests/test_web_app.py` (job store,
      status detail).
- [x] `scripts/smoke_submit_flow.py` — automated POST→redirect→job-page check;
      PASSES.
- [x] Final validation PASS; `smoke_web` PASS; full unittest (182 tests) PASS.
- [ ] Capture screenshots if GUI is available (instructions in
      `task-004B-screenshot-instructions.md` and
      `artifacts/submission/visual-evidence/screenshot-checklist.md`).
- [ ] Yoruba-mode UI toggle.
- [ ] Re-validate on target Ubuntu 22.04 / 8 GB hardware.

### 004D — Answer rendering fix (complete)

- [x] Root cause documented in `artifacts/eval/task-004D-answer-rendering-fix.md`:
      two divergent "visible answer" implementations disagreed (UI
      `_extract_answer` over-filtered `I/W/L` lines, wiping the answer; while
      `model_inference._visible_answer` counted log lines → `visible_chars>0`).
      Plus `contains_think` flagged the empty Qwen template as a trap.
- [x] Added single source of truth `app.model_inference.extract_visible_answer()`
      returning `clean_answer`, `clean_answer_chars`, `contains_think`,
      `think_trap`, `extraction_warning`.
- [x] `run_model()` now returns `clean_answer`, `clean_answer_chars`,
      `think_trap`, `extraction_warning`, `raw_stdout_chars`, `raw_stderr_chars`
      (backwards-compatible `visible_answer_chars == clean_answer_chars`,
      `stdout_chars`, `stderr_chars`, `contains_think` retained).
- [x] Job result page renders `clean_answer` when `clean_answer_chars > 0`;
      shows extraction warning if present; runtime summary uses
      `clean_answer_chars` + `think_trap`; only shows the empty-answer fallback
      when the answer is genuinely empty.
- [x] Empty Qwen `<think></think>` template handled as `contains_think=True,
      think_trap=False` (not a failure).
- [x] Optional bounded debug: `AFREKAOS_DEBUG_OUTPUT=1` writes a small snapshot
      (no user question) to `artifacts/eval/task-004D-debug/`.
- [x] Analyzers (`analyze_qwen_outputs`, `analyze_grounded_outputs`,
      `analyze_target_benchmark`) expose distinct `contains_think`/`think_trap`;
      none classify an empty template as a trap; dead code removed.
- [x] Tests added/updated: `tests/test_model_output_extraction.py` (extraction
      cases), `tests/test_web_templates.py` (clean_answer rendering, extraction
      warning, clean_answer_chars in summary), `tests/test_grounded_output_analyzer.py`
      + `tests/test_target_hardware_scripts.py` (contains_think vs think_trap).
- [x] Final validation PASS; `smoke_web` PASS; `smoke_submit_flow` PASS; full
      unittest (199 tests) PASS.

### 004E — Prompt echo & final answer display fix (complete)

- [x] Root cause documented in `artifacts/eval/task-004E-prompt-echo-fix.md`:
      runtime echoed the grounded prompt into stdout; extractor had no
      prompt-echo awareness; latent bug where `<think>` mention in answer rules
      triggered false think-strip.
- [x] Explicit `BEGIN FINAL OPERATING GUIDANCE` delimiter added to both
      `build_grounded_prompt` and `build_ungrounded_prompt`, with instructions
      not to repeat context/sources/rules/CoT.
- [x] `strip_prompt_echo()` added; `extract_visible_answer()` now accepts the
      original `prompt`, prefers text after the delimiter, strips exact prefix
      and known echo markers/source paths; returns `prompt_echo_detected` and
      `prompt_echo_stripped`. Extraction reordered: echo-strip before
      think-strip (so the `<think>` mention in rules cannot trigger false strip).
- [x] Best-effort `--no-display-prompt` added to `run_model` (checked via
      `--help`, silent fallback to post-processing). `run_model` passes the
      prompt into extraction and returns `prompt_echo_*` fields.
- [x] UI: answer panel titled "Operating Guidance"; mode shown in status panel
      (Retrieval-grounded / Direct-answer mode / Local-only); "Prompt echo
      removed from display" note when echo stripped; runtime summary includes
      `prompt_echo_stripped`.
- [x] Analyzers (`analyze_grounded_outputs`, `analyze_target_benchmark`,
      `analyze_qwen_outputs`) report `prompt_echo_detected`/`prompt_echo_status`
      over cleaned answer; older artifacts not auto-failed.
- [x] Tests added: `tests/test_prompt_echo_extraction.py` (delimiter, echo
      strip, markers, SME-term preservation, prompt builder),
      `tests/test_web_templates.py` (title, echo note, no prompt markers).
- [x] Final validation PASS; `smoke_web` PASS; `smoke_submit_flow` PASS; full
      unittest (214 tests) PASS.

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

### 005B — Visual evidence package (complete — instructions only)

- [x] Visual evidence directory created:
      `artifacts/submission/visual-evidence/`.
- [x] `screenshot-checklist.md` — exact pages, filenames, and the one demo
      prompt to capture (Mission Control, Demo, 3 advisors, Status, 1 live
      advisor result).
- [x] `demo-video-shot-list.md` — 2–3 minute shot-by-shot plan.
- [x] `demo-video-script.md` — plain, honest narration.
- [x] `evidence-manifest.md` — expected vs. actually-captured visual evidence.
- [x] `scripts/prepare_visual_evidence.py` — stdlib-only helper; verifies UI is
      live (`/`, `/demo`, `/status`, `/health` → 200) and copies existing
      HTML/JSON snapshots into the visual-evidence directory.
- [x] Final artifact index, README, and REPORT updated.
- [x] Validation passes (final_validation, smoke_web, capture_ui_evidence,
      unittest).
- [x] **Screenshots/video are instructions only** — no fabricated images, no
      browser-automation dependency added. Real HTML/JSON route snapshots are
      referenced/copied instead.

### 005C — Target hardware retest (complete on closest available machine)

- [x] `scripts/target_hardware_profile.py` — collects OS/CPU/memory/disk/model/
      retrieval/FTS5; writes `target-hardware-profile.md`.
- [x] `scripts/target_inference_benchmark.py` — 3 bounded grounded prompts with
      wall-clock timing + TPS scraping; writes outputs + notes + summary.
- [x] `scripts/analyze_target_benchmark.py` — think-trap/derailment/forbidden-
      claim/SME-term analyzer; writes `target-hardware-benchmark-analysis.md`.
- [x] `tests/test_target_hardware_scripts.py` (14 tests).
- [x] Benchmark ran (3/3 PASS, no traps, real TPS captured).
- [x] **Gap documented:** current machine is macOS 12.7.6 / 32 GB, NOT Ubuntu
      22.04 / 8 GB. True target run still needed on actual hardware.
- [x] Evidence: `artifacts/submission/task-005C-target-hardware-retest.md`.

### 005D — Ubuntu 22.04 / 8 GB target retest (attempt complete; Ubuntu target NOT met)

- [x] Re-ran the full validation + benchmark + UI pipeline end-to-end on the only
      machine reachable from this environment (macOS 12.7.6 / 32 GB — same as
      005C).
- [x] Hardware profile confirmed, retrieval index rebuilt (8 docs), final
      validation PASS (9/9), target inference benchmark PASS (3/3, no think
      traps, real TPS captured), analyzer PASS, web smoke test PASS, UI evidence
      capture PASS (7 files).
- [x] Artifact created: `artifacts/submission/task-005D-ubuntu-8gb-retest.md`
      (honest record — no fabricated numbers; all timing/TPS/memory scraped from
      real llama.cpp output / Python wall-clock).
- [x] Risk register updated: Risk 2 remains **"Partially mitigated — open"**
      because the run was **not** on Ubuntu 22.04 (per the task's contingency
      rule for non-Ubuntu runs).
- [ ] **True Ubuntu 22.04 / 8 GB run still open.** This task did not execute on
      Ubuntu 22.04, so the target-hardware risk is not closed. A genuine Ubuntu
      22.04 run (ideally ≤ 8 GB) is required to move Risk 2 to "Mitigated with
      Ubuntu 22.04 / 8 GB retest evidence."
