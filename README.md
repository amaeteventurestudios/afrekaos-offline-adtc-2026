# AfrekaOS Offline (ADTC 2026)

> Public, offline-first edition. Skeleton stage.

AfrekaOS Offline is an **offline SME operations copilot** for African business
operators. It helps small business owners and field operators reason through
daily operations — inventory, cashflow pressure, supplier delays, customer
follow-up, staffing, and expansion readiness — **without requiring cloud
access**.

This repository is a public, **ADTC-style offline challenge edition**.

## What this is

- A **local-only** reasoning copilot for SME operations.
- Runs as a **local browser app on localhost** on a low-cost Ubuntu 22.04 laptop
  (8 GB RAM, integrated graphics).
- Uses a **GGUF model** with the **llama.cpp** runtime.
- Uses a **SQLite FTS5** retrieval layer over **public SME operations notes**.
- Yoruba mode is planned as a language-mode target.

## What this is not

AfrekaOS Offline is **not** accounting software, banking software, tax software,
payroll software, or an ERP. It does not store or process customer, bank, tax,
or payroll data. It is an operations **reasoning** copilot.

## Local-first thesis

The thesis is simple: the operator's environment is the constraint, not a
preference. Power and connectivity are intermittent, records are often informal,
and trust is concentrated in a few people and suppliers. So the copilot must:

- run entirely on the operator's machine during judged runtime,
- make **zero** external API calls (no OpenAI, Claude, GLM, Supabase, Vercel,
  cloud database, or any internet dependency),
- ground its reasoning in a local, public operations corpus via SQLite FTS5.

## Current status

This is the **skeleton**. Concretely, right now:

- ✅ Repository structure and planning/spec files exist.
- ✅ `metadata.json` declares the product, runtime constraints, and the two test
  prompts.
- ✅ `download_model.sh` is a safe placeholder (creates `model/`, does not fetch).
- ❌ No model is bundled or downloaded. The model URL is **not locked yet**.
- ❌ No llama.cpp integration yet.
- ❌ No UI yet.
- ❌ No SQLite FTS5 index yet; the corpus is placeholder notes.

Do not overclaim based on this repo. See `REPORT.md` and
`specs/001-afrekaos-offline/`.

## Runtime Baseline (Task 002A)

The runtime baseline wires up the **model/runtime path** only — no UI, no
retrieval, no cloud.

- **Canonical model path:** `model/afrekaos.gguf`
- **Optional overrides:**
  - `AFREKAOS_MODEL_PATH` — point at a different GGUF model file.
  - `LLAMA_CPP_BIN` — path to the llama.cpp binary (e.g. `llama-cli` / `main`).

> The **model URL is not locked yet.** No model is downloaded by this task. If
> `model/afrekaos.gguf` does not exist, the smoke/profiler scripts report that
> state clearly and refuse to fabricate results.

Commands:

```bash
# Validate metadata.json against the product contract.
python3 scripts/check_metadata.py

# Run one short SME operations prompt through llama.cpp (requires model + binary).
./scripts/run_smoke_prompt.sh

# Run both canonical prompts and record outputs under artifacts/eval/.
./scripts/profile_model.sh
```

Configuration helpers live in `app/runtime_config.py` (`get_model_path()`,
`get_llama_binary()`, `model_exists()`, `runtime_summary()`).

## Model Bake-Off (Task 002B)

AfrekaOS uses a **Qwen-first** model bake-off. Speed and responsiveness matter
for daily SME operations, so the small/fast Qwen candidate is the default to
beat; Granite is kept only as a conservative control baseline, not the default.

**Canonical winning model path:** `model/afrekaos.gguf`

> `model/` and `*.gguf` files are **gitignored**. No GGUF is committed. The
> model URL is **not locked yet** — a winner is only recorded after local
> evidence is captured and `model.lock.json` is explicitly created.

Candidates (see `model.candidates.json`):

| id | repo | role |
|----|------|------|
| `qwen3-1.7b-q4-k-m` | `bartowski/Qwen_Qwen3-1.7B-GGUF` | primary speed candidate |
| `qwen3-4b-q4-k-m`   | `bartowski/Qwen_Qwen3-4B-GGUF`   | secondary reasoning candidate |
| `granite-4.1-3b-q4-k-m` | `ibm-granite/granite-4.1-3b-GGUF` | control baseline |

Acquire candidates (uses llama.cpp `-hf` when a binary is available, else prints
manual commands; no cloud inference):

```bash
CANDIDATE=qwen3-1.7b-q4-k-m    ./download_model.sh
CANDIDATE=qwen3-4b-q4-k-m      ./download_model.sh
CANDIDATE=granite-4.1-3b-q4-k-m ./download_model.sh
CANDIDATE=all                  ./download_model.sh
```

Run the bake-off profiler against whatever candidates are present locally:

```bash
./scripts/profile_candidates.sh     # outputs under artifacts/eval/model-bakeoff/
```

Validate the candidate contract:

```bash
python3 scripts/check_model_candidates.py
```

Smoke/profiler scripts also accept a `CANDIDATE_MODEL_PATH` override for
ad-hoc bake-off runs:

```bash
CANDIDATE_MODEL_PATH=model/candidates/qwen3-1.7b-q4-k-m.gguf ./scripts/run_smoke_prompt.sh
```

## Qwen Direct-Answer Mode (Task 002C)

Task 002B found that `qwen3-1.7b` generated **only thinking output** — its
`<think>` block consumed the whole token budget and it never produced a
user-visible SME answer. Task 002C fixes this with a non-thinking template
(`templates/qwen3_nonthinking.jinja`) and a `/no_think` soft switch, then
retests qwen3-1.7b in direct-answer mode.

Result: direct mode **eliminated the `<think>` trap** and the candidate produced
visible SME answers (analyzer verdict: PASS). `qwen3-1.7b-q4-k-m` is locked as
the **first canonical model** (`model/afrekaos.gguf` → symlink; see
`model.lock.json`), with quality caveats tracked as unresolved items (prompt-1
derailed on one of three prompts). It is a working baseline, not a final
endorsement.

Commands:

```bash
# Retest qwen3-1.7b in direct-answer mode (template + /no_think).
AFREKAOS_QWEN_NO_THINK=1 ./scripts/retest_qwen_direct.sh

# Analyze whether outputs produced usable visible answers.
python3 scripts/analyze_qwen_outputs.py
```

`model.lock.json` is created only if a candidate passes direct-answer
viability. `model/` and `*.gguf` remain gitignored; only the lock JSON and the
symlink target path are recorded in metadata.

## Local Retrieval Layer (Task 003A)

AfrekaOS grounds prompts in **local** SME operations notes before model
inference. Retrieval uses **SQLite FTS5** over the public corpus in `data/`.
The index is **local** and **no cloud database** is used. The SQLite database is
generated locally and should not be treated as private data.

```bash
# Build the SQLite FTS5 index from local markdown notes.
python3 scripts/build_retrieval_index.py

# Query the index (three default AfrekaOS queries if none given).
python3 scripts/query_retrieval.py
python3 scripts/query_retrieval.py "low sales stockout supplier delay customer credit"

# Preview the full grounded prompt (retrieved context + question + rules).
# Does NOT call the model.
python3 scripts/preview_grounded_prompt.py "A small shop owner reports low sales, missing stock, supplier delay, and more customers asking for credit. What should they check first?"
```

Retrieval grounds prompts before model inference: it anchors the model on
concrete SME operations concepts (reorder points, lead times, credit limits,
cash-on-hand checks) and adds answer rules that forbid off-topic, chain-of-thought,
and financial-software claims. This is intended to reduce the prompt-1 derailment
seen in Task 002C.

## Grounded Inference (Task 003B)

Grounded inference injects local SQLite FTS5 context (retrieved SME notes)
before calling the locked Qwen model, then compares grounded vs ungrounded
outputs. This is **still local-only** — no cloud model or cloud database is
used. Task 003B tests whether retrieval reduces off-topic answers before UI
work begins.

```bash
python3 scripts/build_retrieval_index.py
AFREKAOS_QWEN_NO_THINK=1 python3 scripts/run_grounded_inference.py
python3 scripts/analyze_grounded_outputs.py
```

Result: the Task 002C prompt-1 derailment (chemistry/multiple-choice) is
**resolved**. Both grounded and ungrounded prompt-1 now stay on SME operations
(answer rules + role), and grounding further improves specificity (concrete
stock/supplier/credit checks from retrieved notes). Analyzer verdict: **PASS**.
See `artifacts/eval/task-003B-grounded-inference.md`.

## Local Browser UI (Task 004A)

AfrekaOS Offline has a **local-only browser UI** built with the Python standard
library (`http.server`). No internet is required during runtime. No cloud model
or cloud database is used. The UI calls retrieval-grounded inference when the
model and llama runtime are available; if they are missing, it shows a clear
local error.

```bash
python3 scripts/build_retrieval_index.py
./scripts/run_local_web.sh
```

Then visit **http://127.0.0.1:8787** — Mission Control links to the Daily
Operations Advisor, Inventory and Stock Check, Cashflow Pressure Coach, and
Offline System Status.

```bash
python3 scripts/smoke_web.py   # non-inference smoke test (no model required)
```

## Repository layout

```
afrekaos-offline-adtc-2026/
  metadata.json          # product metadata, runtime, two test prompts
  download_model.sh      # safe placeholder model fetch
  REPORT.md              # draft report
  README.md              # this file
  SCORING.md             # scoring discipline note
  .gitignore
  LICENSE
  model/                 # GGUF model lands here (gitignored)
  app/                   # local browser app (not implemented yet)
  data/                  # public SME operations corpus
    sme_operations/
    language/
    sources/
  scripts/
  tests/
  artifacts/
    eval/
    submission/
  specs/
    001-afrekaos-offline/
      spec.md
      plan.md
      tasks.md
      research.md
      data-model.md
      quickstart.md
```

## Basic setup (placeholders)

There is no runnable app yet. For repo hygiene only:

```bash
# Safe placeholder: creates model/ if missing. Does NOT download anything.
./download_model.sh
```

A real quickstart (local server, model load, retrieval index) will arrive in a
later task. See `specs/001-afrekaos-offline/quickstart.md`.

## Data and IP boundaries

This repository uses **only public SME operations concepts and challenge-safe
placeholder notes**. It deliberately does **not** include:

- private datasets,
- customer records,
- bank data,
- investor materials,
- a commercial roadmap,
- proprietary strategy.

## License

See `LICENSE`.
