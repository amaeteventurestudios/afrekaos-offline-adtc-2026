# Spec — AfrekaOS Offline (001)

> Product: AfrekaOS Offline — an offline SME operations copilot for African
> business operators. Edition: ADTC 2026. Skeleton stage.

## 1. Problem

African small business owners and field operators must reason through daily
operational pressure — stockouts, delayed supplier deliveries, credit requests,
cashflow squeezes, staffing gaps, and expansion readiness — usually without
reliable internet. Existing reasoning tools assume always-on cloud access and
external API calls, which does not match these operators' real conditions.

## 2. Product thesis

An **offline SME operations copilot** that helps an operator reason through
daily operations (inventory, cashflow pressure, supplier delays, customer
follow-up, staffing, expansion readiness) **without cloud access**. It runs as a
local browser app on localhost and grounds its reasoning in a local, public SME
operations corpus.

## 3. Runtime constraints (hard)

- **Local-only runtime.**
- **GGUF model format.**
- **llama.cpp runtime.**
- **No** OpenAI, Claude, GLM, Supabase, Vercel, cloud database, external API,
  or internet dependency **during judged runtime**.
- **Target hardware:** low-cost Ubuntu 22.04 laptop, 8 GB RAM, integrated
  graphics.
- **App type:** local browser app on localhost.
- **Retrieval layer:** SQLite FTS5 with public SME operations notes.

## 4. What it is not

Not accounting software, banking software, tax software, payroll software, or an
ERP. It does not store customer, bank, tax, or payroll data. It is an operations
**reasoning** copilot.

## 5. Scope of this task (001 — skeleton)

This task creates the repository skeleton and planning files only. It
deliberately does **not**:

- implement the UI,
- implement llama.cpp integration,
- add runtime dependencies,
- download or lock a real model.

See `tasks.md` for the task breakdown and `plan.md` for sequencing.

## 6. Success criteria for the skeleton

- The full directory structure exists.
- `metadata.json` declares the product, runtime constraints, model path
  placeholder, and exactly the two test prompts.
- `download_model.sh` is a safe, executable placeholder that does not fetch.
- Root docs (`README.md`, `REPORT.md`, `SCORING.md`) are present and do not
  overclaim.
- Spec kit files exist and are focused on AfrekaOS Offline.
- Repo is on `main`, committed, and pushed to the configured remote.

## 7. Out of scope for 001

Model selection, quantization choice, llama.cpp wiring, SQLite FTS5 index build,
UI, Yoruba mode implementation. These are later tasks.
