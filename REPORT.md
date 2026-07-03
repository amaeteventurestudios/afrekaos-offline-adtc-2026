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
