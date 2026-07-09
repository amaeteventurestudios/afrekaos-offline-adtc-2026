# Final Demo Script — AfrekaOS Offline

> 2–3 minute demo script. Plain and direct.

## Opening

"AfrekaOS Offline is a local-only operations copilot for African small
businesses. It runs on a low-cost laptop with no internet — no cloud model, no
cloud database."

## Problem

"Small shop owners and market operators deal with stockouts, supplier delays,
cash pressure, and credit decisions every day. Most reasoning tools assume
always-on internet. Their environment doesn't."

## Why offline matters

"Power and connectivity are intermittent. Records are often informal. Trust is
concentrated in a few staff and suppliers. So the copilot must run entirely on
the operator's machine during use."

## What AfrekaOS does

"It helps the operator reason through daily operations — inventory, cashflow,
credit, supplier delays, staffing, and expansion readiness — using a local Qwen
model grounded in local SME operations notes, served through a browser on
localhost."

## Walkthrough

1. **Mission Control** (`/`): the landing page. Shows offline mode, local model,
   SQLite retrieval, no cloud dependency. Cards link to each advisor.

2. **Demo Scenarios** (`/demo`): four ready-made SME scenarios. Click one to
   submit it to the matching advisor.

3. **Daily Operations Advisor** (`/advisor/daily`): enter a triage question —
   low sales, stockouts, supplier delay, credit pressure — and get a short
   operating checklist.

4. **Inventory and Stock Check** (`/advisor/inventory`): focus on fast-moving
   items, slow stock, reorder points, and supplier lead times.

5. **Cashflow Pressure Coach** (`/advisor/cashflow`): reason through cash
   pressure, credit requests, and record gaps.

6. **Offline System Status** (`/status`): shows the locked model, retrieval
   index, llama binary, and the "no cloud dependency" statement.

## Demo scenario to run live

**Low sales, stockout, supplier delay, customer credit pressure** — Scenario 1
on the Demo page. It submits to the Daily Operations Advisor and returns a
retrieval-grounded operating checklist.

## How it works under the hood

- **Local model:** qwen3-1.7b (GGUF, Q4_K_M) via llama.cpp, in direct-answer
  mode (no hidden thinking shown to the user).
- **SQLite retrieval:** the operator's question is matched against local SME
  operations notes via FTS5; the top results are injected as context before the
  model answers.
- **Direct-answer Qwen mode:** a non-thinking template + `/no_think` keeps
  answers short and practical.
- **No cloud dependency:** everything runs on 127.0.0.1. No external API calls.

## Boundary language

"AfrekaOS provides operational guidance only. It is not accounting, banking,
payroll, tax, lending, or ERP software. Operators should verify their own
records before acting."
