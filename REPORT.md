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
