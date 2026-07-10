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
