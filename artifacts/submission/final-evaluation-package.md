# Final Evaluation Package — AfrekaOS Offline

> Task 005A. This is the submission summary for AfrekaOS Offline (ADTC 2026).

## Product

- **Name:** AfrekaOS Offline
- **Thesis:** An offline SME operations copilot for African business operators.
  It helps small business owners and field operators reason through daily
  operations — inventory, cashflow pressure, supplier delays, customer
  follow-up, staffing, and expansion readiness — without requiring cloud access.

## Runtime

- **Model:** `qwen3-1.7b-q4-k-m` (first locked baseline; see `model.lock.json`)
- **Canonical model path:** `model/afrekaos.gguf` (relative symlink to
  `model/candidates/qwen3-1.7b-q4-k-m.gguf`)
- **Model format:** GGUF, Q4_K_M
- **Engine:** llama.cpp (`llama-completion` for direct-answer single-turn)
- **Direct-answer mode:** `AFREKAOS_QWEN_NO_THINK=1` +
  `templates/qwen3_nonthinking.jinja` + `-no-cnv`
- **Target hardware:** low-cost Ubuntu 22.04 laptop, 8 GB RAM, integrated graphics

## Retrieval

- **SQLite FTS5** over local, public SME operations notes
- **Index:** `data/afrekaos_fts.sqlite` (generated locally; 8 documents)
- **Corpus:** `data/sme_operations/` (inventory, cashflow, credit, supplier,
  staffing, expansion), `data/language/`, `data/sources/`

## UI

- **Type:** Python standard-library local browser UI (`http.server`)
- **Server URL:** http://127.0.0.1:8787
- **Main routes:**
  - `/` — Mission Control
  - `/demo` — Demo Scenarios (4 ready-made SME scenarios)
  - `/advisor/daily` — Daily Operations Advisor
  - `/advisor/inventory` — Inventory and Stock Check
  - `/advisor/cashflow` — Cashflow Pressure Coach
  - `/status` — Offline System Status
  - `/health` — JSON health endpoint

## Evidence artifacts

| Artifact | What it proves |
|----------|---------------|
| `model.candidates.json` | Qwen-first bake-off candidate set (qwen3-1.7b primary, qwen3-4b secondary, granite control) |
| `model.lock.json` | qwen3-1.7b-q4-k-m locked as first canonical baseline |
| `artifacts/eval/task-002B-model-bakeoff.md` | Model bake-off evidence; 1.7B acquired and profiled |
| `artifacts/eval/task-002C-qwen-direct-mode.md` | Direct-answer mode fixes the thinking trap; model locked |
| `artifacts/eval/task-003A-retrieval.md` | SQLite FTS5 retrieval layer over public SME notes |
| `artifacts/eval/task-003B-grounded-inference.md` | Grounded vs ungrounded comparison; prompt-1 derailment resolved |
| `artifacts/eval/task-004A-local-web-ui.md` | Standard-library local browser UI; routes + inference verified |
| `artifacts/eval/task-004B-ui-polish.md` | UI polish, `/demo` route, evidence snapshots |
| `artifacts/eval/task-004B-ui-evidence/` | HTML/JSON snapshots of all UI routes |
| `artifacts/submission/final-validation-log.md` | Full validation run log |

## Known limitations

- **Dev-machine timing** (Darwin x86_64) is **not** target-hardware timing
  (Ubuntu 22.04 / 8 GB). TPS/RAM numbers must be re-validated on target.
- **qwen3-1.7b is a first locked baseline**, not a final universal endorsement.
  It can be shallow on complex business questions; prompt-1 derailed before the
  answer-rules + grounding fix.
- **Not accounting, banking, payroll, tax, lending, or ERP software.**
- **Uses public SME notes only** — no private/customer/bank data.
- **Retrieval corpus is small** (8 documents); richer notes → better grounding.

## Boundaries (enforced)

- No cloud inference.
- No cloud database.
- No external APIs during runtime.
- No private data, customer records, bank records, payroll workflows, tax filing
  workflows, or ERP claims.
- No FastAPI, Flask, Node, npm, React, Tailwind, or external CSS/JS/fonts/CDNs.
