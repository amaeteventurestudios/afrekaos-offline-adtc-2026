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
