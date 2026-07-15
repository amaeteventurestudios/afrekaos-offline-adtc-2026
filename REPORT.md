# AfrekaOS Offline — DRAFT REPORT (ADTC 2026)

> Status: Draft. This is a skeleton report. Claims are kept deliberately narrow
> until the model path, quantization, and retrieval corpus are locked.

## Problem

Small business owners and field operators across African markets routinely have
to reason through operational pressure without cloud access: stockouts, delayed
supplier deliveries, requests for credit, cashflow squeezes, staffing gaps, and
questions about whether they are ready to expand. Most reasoning tools assume
always-on internet and external API calls, which does not match the conditions
in which these operators actually work.

AfrekaOS Offline is an **offline SME operations copilot**. It helps an operator
reason through daily operations — inventory, cashflow pressure, supplier delays,
customer follow-up, staffing, and expansion readiness — without requiring cloud
access.

## African SME context

The product is shaped around the realities of African small business operations:

- Power and connectivity are intermittent; the judged runtime must not depend on
  the internet.
- Record-keeping is often irregular (paper, SMS, memory) rather than structured.
- Trust is concentrated in a small number of staff and suppliers.
- Working capital is limited, so credit decisions and stock decisions compound
  quickly.
- Seasonal demand shifts matter more than long-horizon forecasting for most
  operators.

The retrieval corpus (see `data/`) is built only from **public SME operations
concepts and challenge-safe placeholder notes**. No private datasets, customer
records, bank data, or proprietary materials are included.

## Offline design

AfrekaOS Offline is local-first by constraint, not by preference:

- **Local-only runtime.** No OpenAI, Claude, GLM, Supabase, Vercel, cloud
  database, external API, or internet dependency during judged runtime.
- **Local browser app on localhost.** The operator interacts through a browser
  pointed at a local server; nothing leaves the machine.
- **GGUF model + llama.cpp runtime**, sized for low-cost hardware.
- **SQLite FTS5 retrieval layer** over public SME operations notes, so the model
  can ground its reasoning in concrete operational concepts rather than
  guessing.

## Model and runtime

- **Format:** GGUF.
- **Engine:** llama.cpp.
- **Target hardware:** low-cost Ubuntu 22.04 laptop, 8 GB RAM, integrated
  graphics.
- **Model path placeholder:** `model/afrekaos.gguf`.

The exact model and quantization are **not locked yet**. `download_model.sh` is
a safe placeholder that creates `model/` if missing and explicitly states the
URL is not locked. Do not assume a specific model is present.

## Retrieval layer

Retrieval is SQLite FTS5 over a small, public SME operations corpus:

- `data/sme_operations/` — public operational concepts (inventory, cashflow,
  credit, supplier, staffing, expansion).
- `data/language/` — language-mode notes, including Yoruba-mode placeholders.
- `data/sources/` — provenance for any public references used.

The retrieval layer is the part that lets the copilot give grounded, specific
operational advice instead of generic platitudes. It is also where the African
use-case story lives.

## Limitations

This is a skeleton. Be explicit about what is not true yet:

- No model is bundled or downloaded. The model URL is not locked.
- No llama.cpp integration is implemented yet.
- No UI is implemented yet.
- No SQLite FTS5 index is built yet; the corpus is placeholder notes.
- No live customer, bank, tax, payroll, or accounting data is used, and none
  will be. AfrekaOS Offline is **not** accounting software, banking software,
  tax software, payroll software, or an ERP. It is an operations reasoning
  copilot.

## How to run

There is no runnable app yet. For the skeleton stage:

```bash
# 1. (Optional) create the model directory.
./download_model.sh

# 2. Nothing else runs yet.
```

A real quickstart will be added in a later task once the model path and the
local server are in place. See `specs/001-afrekaos-offline/quickstart.md`.

## Task 002A — Runtime Baseline

This task added the **first executable model/runtime baseline** without building
retrieval or UI. It establishes runtime discipline, metadata validation, and
profiler readiness.

**What was added:**

- `app/runtime_config.py` — dependency-free runtime config. Defines
  `DEFAULT_MODEL_PATH = "model/afrekaos.gguf"` and honors the
  `AFREKAOS_MODEL_PATH` and `LLAMA_CPP_BIN` environment overrides. Helpers:
  `get_model_path()`, `get_llama_binary()`, `model_exists()`,
  `runtime_summary()`.
- `scripts/check_metadata.py` — metadata contract checker (product name,
  domain, model path, exactly two non-empty prompts). Exits non-zero on
  violations.
- `scripts/run_smoke_prompt.sh` — executable; runs one short SME operations
  prompt through llama.cpp. Checks model + binary exist first. No internet, no
  external API.
- `scripts/profile_model.sh` — executable; runs both canonical metadata prompts
  and writes outputs + runtime notes under `artifacts/eval/`.
- `tests/test_metadata_contract.py`, `tests/test_runtime_config.py` —
  standard-library-only tests.
- README and this report updated.

**What remains unresolved:**

- No model is downloaded or locked. The model URL is still not locked.
- If `model/afrekaos.gguf` is absent, the smoke/profiler scripts record that
  state and do not fabricate benchmark numbers.
- Actual model selection/download lock is deferred to Task 002B.

**Explicitly not added in this task:** no UI, no retrieval (no SQLite FTS5
index), no cloud service, no private data, no banking data, no payroll data, no
tax workflow, and no ERP behavior. No model was downloaded in this task unless a
local model already existed and was only referenced by the scripts.

## Task 002B — Model Bake-Off

### Why the project shifted from a Granite lock to a Qwen-first bake-off

An earlier direction was to lock Granite as the default model. That is reversed.
AfrekaOS needs **fast, practical, checklist-style** responses for everyday SME
operators; Granite is useful as a *conservative control baseline* but should not
be the default if a Qwen candidate is faster and good enough on SME operations
prompts. So the selection mode is now `qwen_first_bakeoff`: the small/fast Qwen
candidate is the default to beat, and Granite only serves as a sanity-check
control.

### Candidates

| id | role | repo | quant |
|----|------|------|-------|
| `qwen3-1.7b-q4-k-m` | primary speed candidate | `bartowski/Qwen_Qwen3-1.7B-GGUF` | Q4_K_M |
| `qwen3-4b-q4-k-m` | secondary reasoning candidate | `bartowski/Qwen_Qwen3-4B-GGUF` | Q4_K_M |
| `granite-4.1-3b-q4-k-m` | control baseline | `ibm-granite/granite-4.1-3b-GGUF` | Q4_K_M |

Canonical winning model path (only filled after a real winner is locked):
`model/afrekaos.gguf`.

### What was actually validated locally

`download_model.sh` was rewritten into a candidate acquisition script that reads
`model.candidates.json` as the source of truth, supports `CANDIDATE=` selection,
prefers llama.cpp `-hf` acquisition, and falls back to printed manual commands.
`check_model_candidates.py`, `profile_candidates.sh`, a rubric, and tests were
added. All contract checks and the unittest suite pass.

### Whether any model exists locally

<!-- BEGIN-LOCAL-STATE -->
_This section reflects the actual machine state at task time (see
`artifacts/eval/task-002B-model-bakeoff.md`)._
- `qwen3-1.7b-q4-k-m`: **present** (1.2 GB, acquired via direct HuggingFace
  download; `llama-cli -hf` did not resolve Bartowski's real filename).
- `qwen3-4b-q4-k-m`: **absent**.
- `granite-4.1-3b-q4-k-m`: **absent**.
- `model/afrekaos.gguf`: **absent** (no winner promoted).
<!-- END-LOCAL-STATE -->

### Whether real inference ran

**Yes — for qwen3-1.7b only**, via `llama-completion` (build 9700). Real timing
was captured (generation ~5 tok/s, prompt eval ~24-28 tok/s on the development
machine; projected ~5.4 GB host memory). The other two candidates had no local
file and were recorded as missing-model.

However, **qwen3-1.7b produced no usable user-visible SME answer**: its Qwen3
thinking mode consumed the entire token budget inside `<think>` and never
emitted the actual checklist/advice. So the practical-answer floor was not met
at this configuration. Two runtime bugs were found and fixed during the bake-off
(`llama-cli` conversation-mode runaway → prefer `llama-completion`; interactive
stdin stealing the loop's input → redirect from `/dev/null`). **No final
performance is claimed** — target-hardware numbers and a thinking-disabled
re-run are still required.

### Winner status

**Unresolved.** No winner is selected and no `model.lock.json` exists, because
no local evidence supports a selection yet. This is deliberate: do not fabricate
a winner.

### Not claimed

This task claims no accounting, banking, payroll, tax, or ERP capability, and
adds no UI, retrieval, cloud service, private data, or external API.

## Task 002C — Qwen Direct-Answer Mode Retest

### The Task 002B failure

Task 002B found that `qwen3-1.7b-q4-k-m` ran real inference but produced **no
user-visible SME answer**: Qwen3's thinking mode consumed the entire token
budget inside `<think>` across all three prompts. The winner was left
unresolved.

### Direct-answer retest

Task 002C added a non-thinking chat template
(`templates/qwen3_nonthinking.jinja`, the template equivalent of
`enable_thinking=False`) plus a `/no_think` soft switch
(`AFREKAOS_QWEN_NO_THINK=1`), and retested qwen3-1.7b via `llama-completion`
with `-no-cnv`. See `artifacts/eval/task-002C-qwen-direct-mode.md`.

### Actual local result

The thinking-mode trap is **fixed**: no `<think>` block appears in any of the
three retest outputs (analyzer verdict: **PASS**, 3/3 outputs with useful
visible answer text). Real timing captured on the development machine:
generation ~4 tok/s, prompt-eval ~28 tok/s, projected ~5.4 GB host memory.

Answer quality is **mixed**: prompt-2 (expansion) produced a strong, usable SME
risk analysis; smoke produced a usable checklist; prompt-1 (triage) **derailed**
into off-topic multiple-choice + chemistry hallucination despite having visible
text. So direct mode is necessary but the model still needs prompt hardening or
a larger non-thinking alternative for reliability across all prompts.

### Whether qwen3-1.7b remains viable

**Conditionally yes.** It is locked as the **first canonical model**
(`model.lock.json`; `model/afrekaos.gguf` is a relative symlink to the
candidate) so the project can proceed to retrieval (Task 003). This is a working
baseline, not a final endorsement. Unresolved items: prompt-1 derailment,
target-hardware profiling, and no comparison candidate (granite/qwen3-4b still
absent). A fallback candidate (`qwen2.5-3b-instruct-q4-k-m`) is recommended for
Task 002D if the derailment cannot be tamed.

### Not claimed

No final target-hardware performance is claimed. No accounting, banking,
payroll, tax, or ERP capability is claimed.

## Task 003A — SQLite Retrieval Layer

This task added the **first local SQLite FTS5 retrieval layer** so AfrekaOS can
ground prompts before model inference.

**What was added:**

- `app/retrieval.py` — FTS5 module: `build_index`, `search`, `get_document`,
  `retrieval_summary`. Standard library only.
- `app/prompt_context.py` — grounded prompt builder: `build_context_block`,
  `build_grounded_prompt` (role + retrieved context + question + answer rules).
- `scripts/build_retrieval_index.py`, `scripts/query_retrieval.py`,
  `scripts/preview_grounded_prompt.py`.
- `tests/test_retrieval.py`, `tests/test_prompt_context.py` (65 tests total,
  all passing).
- Evidence: `artifacts/eval/task-003A-retrieval.md`,
  `artifacts/eval/task-003A-grounded-prompt-preview.md`.

**Source directories:** `data/sme_operations/`, `data/language/`, `data/sources/`
— public SME operations notes only. Model files, artifacts, and `.git` are never
indexed.

**Index path:** `data/afrekaos_fts.sqlite` (generated locally; gitignored as a
build artifact). 8 documents indexed; SQLite FTS5 confirmed available.

**Why retrieval matters after the Qwen prompt-1 derailment.** In Task 002C,
`qwen3-1.7b` derailed on prompt-1 into off-topic content even in direct-answer
mode. The grounded prompt builder now injects the relevant SME notes (supplier
lead times, stock-cover checks, cashflow/credit discipline) and answer rules
that forbid off-topic, chain-of-thought, and financial-software claims. This
narrows the relevant context and should raise the answer floor — though
confirming the reduction requires actually running grounded prompts through the
model (Task 003B), which is deliberately out of scope here.

**This is still not UI.** No cloud database, private data, banking workflow,
payroll workflow, tax workflow, or ERP behavior was added.

## Task 003B — Grounded Inference

This task connected the SQLite FTS5 retrieval layer (Task 003A) to the locked
Qwen model and compared grounded vs ungrounded outputs.

**What was added:** `app/model_inference.py` (inference helper with grounded/
ungrounded runners, bounded generation, subprocess timeout, stdin from
DEVNULL), `scripts/run_grounded_inference.py` (6-run comparison),
`scripts/analyze_grounded_outputs.py` (derailment/SME-term analyzer), and tests.

**Grounded vs ungrounded comparison.** All 3 prompts (metadata prompt-1,
prompt-2, smoke) were run twice: once ungrounded (role + rules only) and once
grounded (role + retrieved SME context + rules), both in Qwen direct-answer
mode. Real inference ran on all 6 via `llama-completion`.

**Did real inference run?** Yes — all 6 runs completed with no timeouts.
Generation ~3.4–4.1 tok/s, projected 5410 MiB host memory (development machine).

**Did prompt-1 improve?** Yes — the Task 002C derailment (chemistry/
multiple-choice) is **fully resolved**. Neither grounded nor ungrounded
prompt-1 derailed; the answer rules + AfrekaOS role kept the model on SME
operations. Grounding further improved specificity (concrete stock counts,
expiration dates, supplier delivery status from retrieved notes). Analyzer
verdict: **PASS**.

**Limitations:** small sample (6 runs), dev-machine timing (not target
hardware), BM25 keyword retrieval (not semantic), and the role+rules alone
fixed the derailment so retrieval's marginal contribution is specificity rather
than derailment prevention per se.

**This is still not UI.** No cloud database, private data, banking workflow,
payroll workflow, tax workflow, or ERP behavior was added.

## Task 004A — Local Browser UI

This task added the **first local browser UI** using Python standard library
only.

**What was added:** `app/web_app.py` (`http.server.ThreadingHTTPServer` at
`127.0.0.1:8787`), `app/web_templates.py` (HTML render helpers with embedded
CSS, all user content escaped), `scripts/run_local_web.sh` (sets
`AFREKAOS_QWEN_NO_THINK=1`, runs `python3 -m app.web_app`),
`scripts/smoke_web.py` (non-inference smoke test), and tests.

**Routes:** `/` (Mission Control), `/advisor/daily`|`/inventory`|`/cashflow`
(GET forms + POST grounded inference), `/status` (offline system status),
`/health` (JSON). The UI calls `app.model_inference.run_grounded()` with bounded
generation and a subprocess timeout; missing model/runtime renders a
browser-friendly error.

**Standard library only.** No FastAPI, Flask, Node, npm, React, Tailwind, CDNs,
or any external CSS/JS/fonts/images. No network calls.

**Was UI inference tested?** Yes — `scripts/smoke_web.py` passed (all routes
200, `/health` valid JSON), and a manual `POST /advisor/daily` returned
operating guidance with the accounting/banking warning. Generation was bounded.

**Limitations:** minimal styling, single-user localhost (no auth/HTTPS), blocking
inference per request, no Yoruba-mode UI toggle yet, dev-machine timing.

**This is not cloud software.** No private data, banking workflow, payroll
workflow, tax workflow, or ERP behavior was added.

## Task 004B — UI Polish and Evidence

This task polished the standard-library local browser UI and added demo +
evidence tooling.

**What was added:** offline status banner, top navigation bar, stronger card
layout, improved form/answer/error layouts, unified boundary warning on every
advisor result, a new `GET /demo` route with four demo-scenario cards (low
sales/stockout, expansion readiness, inventory pressure, cash/credit), and
`scripts/capture_ui_evidence.py` (fetches all routes, saves HTML/JSON snapshots,
verifies labels; optional bounded inference via
`AFREKAOS_CAPTURE_INFERENCE=1`).

**`/demo`:** four ready-made SME scenarios, each with a one-click form that
submits to the matching advisor endpoint.

**Evidence capture:** `capture_ui_evidence.py` captured 7 files (home, demo, 3
advisors, status, health.json) — all routes returned 200, all labels verified.
Inference was not run during capture (by design); it can be enabled optionally.

**Was inference captured?** Not during evidence capture (default off). Inference
through the UI was verified in Task 004A.

**Limitations:** screenshots are optional (instructions only, no GUI capture in
this environment); minimal styling; standard library only.

**This is standard-library local UI.** No cloud database, private data, banking
workflow, payroll workflow, tax workflow, lending workflow, or ERP behavior was
added.

## Task 004C — Advisor Submit & Runtime Feedback Fix

This task fixed the broken advisor submit experience so the local model never
leaves the user staring at a frozen form or a vague "500" page.

**What was broken.** (1) `do_POST` ran grounded inference **synchronously inside
the request handler** — ~43–69s per prompt (see Task 005D timings) with **no
progress feedback**, so the button looked like it did nothing. (2) The global
error handler rendered only `<h2>500 — Server error</h2>` with no diagnostics.
(3) The status banner relied on a CSS `content:"\2713 "` pseudo-element that
rendered as a stray marker, observed externally as "13 Offline mode".

**Was the 500 reproduced?** **Partially.** With a deliberately broken model path
the failure path returns HTTP 200 with a folded "Could not run local inference"
message (not a 500); the bare 500 only appears when an unexpected exception
escapes the handler. The **primary confirmed defect** was the silent blocking
POST with no loading state — reproduced by code inspection and the real 43–69s
timings. See `artifacts/eval/task-004C-ui-submit-fix.md` for the root-cause
analysis (no guessing).

**What was fixed.**
- **In-memory job system.** `POST /advisor/<name>` now creates a job, starts a
  background thread, and **immediately returns 303 → `/job/<id>`**. Jobs live in
  memory only, are never persisted, and the full question is never logged.
- **Progress page.** `GET /job/<id>` auto-refreshes every 3s while queued/
  running, shows the ordered steps (Request received → … → Running local Qwen
  model → Complete), the runtime status panel, and the final answer or a
  browser-friendly error.
- **Client-side loading feedback.** Advisor + demo forms include a tiny inline
  `<script>` (no external files) that disables the button and shows "Running
  local model…" on submit. Plain POST still works with JavaScript off.
- **Friendly error page.** The global handlers render diagnostics: error summary,
  current route, suggested checks (model path, llama binary, timeout, terminal
  logs), and nav links — never a bare "500".
- **Banner fix.** Explicit `✓` text in the HTML (the CSS pseudo-element was
  removed). Tests assert the page no longer contains `13 Offline mode`.
- **Status detail panel** on job pages (model path exists, llama binary,
  retrieval index, locked candidate, local-only mode).
- **Server logging** of the POST + job lifecycle (no full question).
- The web port is now configurable via `AFREKAOS_WEB_PORT` (default 8787).

**Does the advisor button now redirect to the job progress page?** **Yes.**
Verified live: `POST /advisor/daily → 303 /job/<id>`, and the job page renders
progress steps, the runtime status panel, and the final result/error.
`scripts/smoke_submit_flow.py` automates this check.

**Does the loading/progress state appear?** **Yes** — client-side button-disable
+ "Running local model…" message, and the server-side progress page with
auto-refresh and step indicators.

**Does the banner still show "13"?** **No.** Banner now renders literal
`✓ Offline mode · ✓ Local model · ✓ SQLite retrieval · ✓ No cloud dependency`;
tests assert `13 Offline mode` is absent on every page.

**Was real inference manually tested?** **Yes** (with the real model present):
the job completes and the answer renders on the job page. The automated
tests/smoke use a deliberately nonexistent model so they fail fast without real
inference.

**Limitations.** Jobs are in-memory only (lost on restart, by design — no
private questions persisted); the soft job cap is 50 (oldest evicted first); the
job page polls via meta-refresh (no WebSockets, keeping the stdlib-only
constraint); TPS variance and the open Ubuntu/8 GB risk are unchanged by this UI
fix.

**No new product features or dependencies were added.** Everything is Python
standard library only. **No cloud database, no cloud inference, no private data,
no banking workflow, no payroll workflow, no tax workflow, no lending workflow,
and no ERP behavior was added.**

## Task 004D — Answer Rendering Fix

This task fixed the job result page so it displays the model's actual answer
instead of "model produced no visible answer text" when the run succeeded.

**What was observed.** On `/job/<id>`, a job completed but the answer panel
showed "(model produced no visible answer text)" while the runtime summary
reported `return_code=0, visible_chars=2361, think_trap=True`.

**Why return_code=0 + visible_chars > 0 means the model produced text.**
`return_code=0` means llama.cpp exited cleanly, and `visible_chars > 0` means
the extraction function counted non-trivial content in the output stream. An
empty answer panel alongside those two facts is therefore a rendering/extraction
bug, not a model failure.

**Root cause (confirmed by reconstruction).** There were **two divergent
"visible answer" implementations**. `model_inference._visible_answer` (computes
`visible_answer_chars`) had a narrow line filter and counted log lines as
"answer"; `web_app._extract_answer` (renders the UI answer) had an over-broad
`^[IWL]\s+` line filter that stripped *any* line starting with `I `/`W `/`L `.
Because every llama.cpp log line starts with those letters, the UI filter wiped
the answer whenever logs dominated the stream — so the two functions disagreed
(186 vs 0 chars on the same input). A second defect: `contains_think` used a
bare `<think>` substring test, so the intended empty Qwen non-thinking template
`<think>\n\n</think>` was falsely reported as `think_trap=True`.

**What was fixed in extraction/rendering.**
- Added a single source of truth: `model_inference.extract_visible_answer()`,
  returning `clean_answer`, `clean_answer_chars`, `contains_think`,
  `think_trap`, `extraction_warning`. The UI and `run_model` both use it, so
  `visible_answer_chars == clean_answer_chars` always.
- Log-line filtering now matches the llama.cpp log *shape* (dotted timestamp, or
  `I/W/L` + a known log prefix), not bare `I/W/L + space` — so a genuine answer
  like "I should restock..." survives.
- `contains_think` (marker present, incl. empty template) is now distinct from
  `think_trap` (unclosed `<think>` with substantial trailing content). An empty
  template is `contains_think=True, think_trap=False`.
- The worker renders `result["clean_answer"]` directly; the job page shows the
  extraction warning if present and only shows the empty-answer fallback when
  `clean_answer_chars` is truly 0. Runtime summary now reports
  `clean_answer_chars` and `think_trap`.
- The three analyzers (`analyze_qwen_outputs`, `analyze_grounded_outputs`,
  `analyze_target_benchmark`) now all expose distinct `contains_think` /
  `think_trap` and never classify an empty template as a trap.
- Optional bounded debug: `AFREKAOS_DEBUG_OUTPUT=1` writes a small snapshot
  (no user question) to `artifacts/eval/task-004D-debug/`.

**Was the issue manually retested?** The failure was reproduced deterministically
with synthetic output mirroring real llama.cpp shape (no private data); see
`artifacts/eval/task-004D-answer-rendering-fix.md`. Extraction/rendering is
covered by 17 new unit tests. A full live re-run was not repeated for this
artifact, but the unified extractor guarantees the UI char count and the
displayed answer can no longer disagree.

**Limitations.** Log-line filtering is heuristic (matches known llama.cpp log
prefixes); an unknown future log prefix could occasionally slip through, but it
would appear as extra text rather than a missing answer. The debug option writes
bounded files only and never persists user questions.

**No new product features or dependencies were added.** Standard library only.

## Task 004E — Prompt Echo & Final Answer Display Fix

The app was showing the entire grounded prompt as the answer — the role line,
retrieved context, `source:` file paths, "Operator question:", and "Answer
rules:" — followed by the actual checklist. The user-facing answer should show
only the final operating guidance.

**Was prompt echo reproduced?** **Yes**, deterministically: feeding the real
grounded prompt (plus a trailing answer) through the extractor produced a
`clean_answer` starting with "You are AfrekaOS..." and containing `source:`
paths and "Answer rules" (1919 chars, mostly prompt).

**Root cause.** (1) The runtime echoes the prompt into stdout when invoked with
`-p`, and no `--no-display-prompt` flag was passed. (2) The extractor had no
prompt-echo awareness. (3) A latent bug: the answer rules mention `<think>` as
literal text, so the think-strip regex (`<think>.*` DOTALL) treated that mention
as a real tag and deleted the delimiter + everything after it — which is why the
fix had to reorder echo-stripping before think-stripping.

**What was fixed.** Delimiter-based prompt construction
(`BEGIN FINAL OPERATING GUIDANCE`) on both grounded and ungrounded prompts;
`strip_prompt_echo()` + delimiter-preference in `extract_visible_answer()`
(returning `prompt_echo_detected`/`prompt_echo_stripped`); extraction reordered
so echo-stripping runs before think-stripping; best-effort
`--no-display-prompt` added to `run_model` (checked via `--help`, silent
fallback); the answer panel is titled "Operating Guidance" with mode shown
separately in the status panel; a "Prompt echo removed from display" note
appears when echo was stripped; analyzers now report `prompt_echo_detected`/
`prompt_echo_status`.

**Does the final answer now display only operating guidance?** **Yes.** The
same echoed input now yields just the checklist; no role line, context, source
paths, or rules. SME terms in the real answer are preserved.

**Limitations.** Marker matching is heuristic; `--no-display-prompt` is
binary-dependent (post-processing fallback covers older binaries); a separate
"Local context used" panel was not added (to avoid new feature complexity).

**No new product features or dependencies were added.** Standard library only.

## Task 004F — Qwen Marker Cleanup

After Task 004E the answer panel showed the correct operating guidance, but the
text still began with a leftover `</think>` and ended with `[end of text]` —
Qwen/llama.cpp runtime control markers that leaked into the visible answer.

**Was the marker leakage reproduced?** **Yes**, deterministically: the pre-fix
extractor left `</think>`, `[end of text]`, `[end of turn]`, `<|endoftext|>`,
and `<|im_end|>` in the output. Only the complete `<think>\n\n</think>` block
was already removed.

**What was fixed.** Added `app.model_inference._clean_runtime_markers()`,
integrated into `extract_visible_answer()`, which strips lone `</think>`,
lone `<think>`, empty block remnants, `[end of text]`, `[end of turn]`,
`<|endoftext|>`, `<|im_end|>`, and `<|im_start|>`, then collapses excessive
blank lines and trims. A lone closing `</think>` is **not** treated as a think
trap; valid answer text after it is preserved, as is text before `[end of text]`.
Bullets and numbered lists are preserved; no markdown conversion is forced.

**Are `</think>` and `[end of text]` no longer visible?** **Yes** — verified by
13 new unit tests (`TestRuntimeMarkerCleanup`) plus the full 227-test suite.
`final_validation.py` PASS; `smoke_web` PASS; `smoke_submit_flow` PASS.

**Was real inference manually retested?** Verified deterministically with
synthetic output mirroring the real model stream (no private data). The cleanup
runs on every extraction path.

**Limitations.** Marker matching is regex-based; an unknown future EOS token
could slip through (as extra trailing text, not a missing answer). The cleanup
is conservative — only known control markers are removed, never SME terms.

**No new product features or dependencies were added.** Standard library only.

## Task 006A — Language Mode

AfrekaOS now supports controlled multilingual responses in six languages:
English, Yorùbá, Hausa, Swahili, Nigerian Pidgin, and French.

**HyveGrid discipline reused conceptually.** A HyveGrid Offline repo exists
locally; its language architecture (registry, controlled labels, glossary,
fallback, prompt instructions) was ported as a *pattern only* — no bee/hive/
apiculture content, product names, or UI wording was copied.

**What was added.** `app/language_mode.py` (6-language registry, normalization
with English fallback, per-language response instructions); glossary files under
`data/language/` for each language; language support in
`build_grounded_prompt`/`build_ungrounded_prompt`/`run_grounded`/`run_ungrounded`
(injecting the response-language instruction + "no cloud translation" rule); a
`<select name="language">` on advisor and demo forms (works without JS); the job
page shows "Response language: <label>"; `scripts/smoke_language_mode.py`
(model-free validation + prompt previews) and `scripts/run_language_inference_sample.py`
(optional live sample).

**Why French.** Francophone West and Central Africa — extends the operator base
with clear, simple business French.

**Retrieval remains English** for now. The FTS5 corpus is English; retrieved
context is injected as English and only the *answer* language is controlled.
Parallel non-English corpus notes are deferred to later work.

**No cloud translation** was added. No Google Translate, no external API, no
network calls. The local model produces the localized answer directly.

**Limitations.** Quality depends on the local model (qwen3-1.7b); smaller
models may mix languages or leave difficult terms in English. We do not claim
perfect translation. The operational boundary is enforced in every language.

**No external dependencies were added.** Standard library only.

## Task 006B — Full UI Localization

Task 006A only localized the answer language; the page chrome stayed English.
Task 006B localizes the **entire UI**: navigation, labels, warnings, form text,
job progress steps, runtime labels, footer, demo page, and status page.

**HyveGrid localization pattern reused conceptually.** The HyveGrid Offline repo
uses the same discipline (language registry, controlled labels, `?lang=`
selector, localized page chrome). The pattern was ported — no bee/hive content
or product wording was copied.

**What was added.** A UI translation registry (`UI_TEXT_BUNDLES`) with ~60 keys
× 6 languages in `app/language_mode.py`; all page renderers in
`app/web_templates.py` now accept a `language` parameter and render chrome from
the bundle; a global language selector (`<form class="langswitch">`) in the
header on every page; `?lang=<code>` query parameter support with language
persistence across nav links; localized default advisor prompts; job pages
render in the job's stored language. `scripts/smoke_ui_localization.py`
validates the localization without requiring the model.

**French page chrome now renders in French.** So do Yorùbá, Hausa, Swahili, and
Nigerian Pidgin. Technical values (model paths, job ids, return codes) remain
unchanged.

**No cloud translation or external APIs were added.** All UI strings are baked
into the standard-library Python module. Retrieval remains English for now.

**Limitations.** Yorùbá/Hausa/Swahili translations are best-effort; we do not
claim perfect translation. Retrieval corpus is English.

**No external dependencies were added.** Standard library only.

## Task 005A — Final Evaluation Package

This task created the final evaluation package, validation runner, and
submission evidence.

**What was added:**
- `scripts/final_validation.py` — runs every repo check (metadata, candidates,
  retrieval build/query, prompt preview, grounded analyzer, web smoke test, UI
  evidence capture, unittest discover), captures pass/fail, writes a markdown
  log to `artifacts/submission/final-validation-log.md`.
- `artifacts/submission/final-evaluation-package.md` — product, runtime,
  retrieval, UI, evidence, limitations, boundaries.
- `artifacts/submission/final-demo-script.md` — 2–3 minute demo script.
- `artifacts/submission/final-runbook.md` — clone → validate → run instructions.
- `artifacts/submission/final-risk-register.md` — 8-row risk table.
- `artifacts/submission/final-artifact-index.md` — evidence file index.

**Validation script:** runs all checks non-interactively; no model inference
required (smoke/evidence captures point the model path at a nonexistent file so
pages render without a model). Writes overall PASS/FAIL + per-check exit codes.

**Was real inference required?** No — `final_validation.py` does not call the
model. Inference evidence already exists from Tasks 002C/003B/004A.

**Limitations:** dev-machine timing (not target hardware); qwen3-1.7b is a first
baseline; small corpus; standard-library UI.

**No cloud database, no cloud inference, no private data, no banking workflow,
no payroll workflow, no tax workflow, no lending workflow, and no ERP behavior
was added.**

## Task 005C — Target Hardware Retest

This task ran the target hardware retest package: a profiler, a bounded
inference benchmark, and an output analyzer.

**What was added:** `scripts/target_hardware_profile.py` (collects OS/CPU/memory/
disk/model/retrieval/FTS5 info), `scripts/target_inference_benchmark.py` (runs
3 grounded prompts with wall-clock timing + TPS scraping),
`scripts/analyze_target_benchmark.py` (think-trap/derailment/forbidden-claim/
SME-term analyzer), and `tests/test_target_hardware_scripts.py`.

**Does the current machine match target constraints?** **No.** It is macOS 12.7.6
(Darwin x86_64, Intel i7-6700K, 32 GB RAM) — not Ubuntu 22.04, and 4× the target
RAM. The artifact documents this gap explicitly.

**Did inference run?** **Yes** — all 3 grounded prompts completed (no timeouts,
no think traps). Real timing: wall-clock 45–64s per prompt, generation
2.6–2.9 tok/s. Analyzer verdict: **PASS** (visible answers, no derailment, no
forbidden claims, all 8 SME terms present).

**Limitations:** not Ubuntu 22.04; 32 GB not 8 GB; single run per prompt (TPS
variance is real); true target-hardware run still needed.

**No cloud database, no cloud inference, no private data, no banking workflow,
no payroll workflow, no tax workflow, no lending workflow, and no ERP behavior
was added.**

## Task 005D — Ubuntu 22.04 / 8 GB Retest

This task's goal was to run and document the **true** Ubuntu 22.04 / 8 GB target
retest for AfrekaOS Offline.

**What machine was used.** The only machine reachable from this environment is
the same macOS workstation used in Task 005C: macOS 12.7.6 (Darwin x86_64),
Intel Core i7-6700K, 32 GB RAM.

**Does it match the target?** **No.** It is not Ubuntu 22.04, and it has 4× the
target RAM (32 GB vs. 8 GB). The Ubuntu target was attempted but not reachable
from this environment; an Ubuntu result is not claimed.

**What ran (all on macOS).** The full pipeline was re-run end-to-end and all of
it passed with fresh, real numbers: hardware profile → retrieval index (8 docs)
→ final validation (PASS, 9/9 checks) → target inference benchmark
(`AFREKAOS_QWEN_NO_THINK=1`, 3 grounded prompts, PASS) → analyzer (PASS, no
think traps, no derailment, no forbidden claims, 8/8 SME terms) → web smoke
test (PASS) → UI evidence capture (PASS, 7 files).

**Results (actually captured, not fabricated):**

| Prompt | wall-clock (s) | generation tps | prompt-eval tps | think trap |
|--------|----------------|----------------|-----------------|------------|
| prompt-1 grounded | 69.43 | 2.37 | 25.18 | no |
| prompt-2 grounded | 52.48 | 3.83 | 40.69 | no |
| smoke grounded | 43.02 | 3.33 | 40.80 | no |

llama.cpp projected **~5.3 GB host memory** usage (within the 8 GB target), but
projection is not a substitute for measured free RAM on a real 8 GB host.

**Remaining limitations.** (1) Not Ubuntu 22.04 — the highest-priority
target-hardware risk (Risk 2) is **not closed** and remains
"Partially mitigated — open." A true Ubuntu 22.04 run on an actual host (ideally
≤ 8 GB) is still required. (2) 32 GB RAM, not 8 GB — memory-pressure behavior
untested. (3) Same physical machine as 005C — this refreshes evidence and
records the Ubuntu attempt, but does not advance the platform question. (4)
Single run per prompt — TPS variance is real (2.37–3.83 tok/s).

**No cloud database, no cloud inference, no private data, no banking workflow,
no payroll workflow, no tax workflow, no lending workflow, and no ERP behavior
was added.**

## Task 005B — Visual Evidence Package

This task produced the final screenshot and demo-video evidence package. It is a
visual evidence task only.

**What was added.** A new visual-evidence directory
(`artifacts/submission/visual-evidence/`) with: a `README.md`,
`screenshot-checklist.md` (exact pages, filenames, and the one demo prompt to
use), `demo-video-shot-list.md` (a 2–3 minute shot plan),
`demo-video-script.md` (plain, honest narration), and `evidence-manifest.md`.
A standard-library-only helper `scripts/prepare_visual_evidence.py` was added:
it starts the local UI, verifies `/`, `/demo`, `/status`, and `/health` return
200, and copies the existing HTML/JSON route snapshots into the visual-evidence
directory with an index and a prep log.

**Were screenshots captured?** **Instructions only.** No browser-automation
dependency was added (no Playwright/Selenium/pyppeteer/npm), and no PNGs were
fabricated. Real, non-visual evidence already exists as HTML/JSON route
snapshots under `artifacts/eval/task-004B-ui-evidence/` (and is copied by the
prep script), but actual PNG screenshots are a manual capture step per the
checklist.

**Was a demo video captured?** **Instructions only.** A full shot list and
narration are provided; recording the video is a manual step.

**Limitations.** (1) No real PNG screenshots or video were committed — both are
manual capture steps to avoid fabricating images. (2) The one live advisor
screenshot requires the model present at `model/afrekaos.gguf`. (3) The
remaining open risk — a true Ubuntu 22.04 / 8 GB run — is unchanged by this
visual task and stays open.

**No new product features or dependencies were added.** The helper script is
Python standard library only. **No cloud database, no cloud inference, no
private data, no banking workflow, no payroll workflow, no tax workflow, no
lending workflow, and no ERP behavior was added.**
