# Task 003A — SQLite Retrieval Layer (Evidence)

> AfrekaOS Offline. Builds the first local SQLite FTS5 retrieval layer over the
> public SME operations notes so prompts can be grounded before model inference.
> No fabricated numbers.

## What was indexed

Public SME operations markdown notes only:

- `data/sme_operations/` — inventory, cashflow, credit, supplier, staffing, expansion
- `data/language/` — Yoruba mode design placeholder
- `data/sources/` — sources/provenance README

Model files, artifacts, `.git`, and private/hidden files are explicitly **never**
indexed (see the `_SKIP_DIRS` guard in `app/retrieval.py`).

## Number of documents indexed

**8 documents** total:
- sme_operations: 6
- language: 1
- sources: 1

Index path: `data/afrekaos_fts.sqlite` (generated locally; not private data).

## Whether SQLite FTS5 was available

**Yes.** Verified at build time: `FTS5 available: True`. If FTS5 were unavailable
the builder would fail clearly with a `RuntimeError`.

## Example retrieval results for the three default queries

These were produced by `python3 scripts/query_retrieval.py` against the real
index. Top result shown per query:

**Query 1:** `low sales stockout supplier delay customer credit`
- Top: `[sme_operations] Supplier` — "delivery cascades into stockouts, lost
  sales, and credit pressure. Operator resilience depends on knowing lead
  times, having alternatives, and not being over-dependent on one supplier."
- Also surfaced: Credit, Cashflow, Inventory, Expansion readiness.

**Query 2:** `expand to second location irregular cash records trusted staff seasonal demand`
- Top: `[sme_operations] Expansion readiness` — "whether the operator's records,
  staff, cash discipline, and demand base can survive being split across two
  sites."
- Also surfaced: Staffing, Cashflow, Supplier, Credit.

**Query 3:** `daily operating checklist small shop inventory cashflow customers supplier`
- Top: `[sme_operations] Inventory` — "fast-moving item vs. typical daily/weekly
  run-rate. Reorder lead time per supplier. Which stockouts are driving the sales
  dip right now?"
- Also surfaced: Cashflow, Staffing, Yoruba mode, Supplier.

Ranking is sensible: each query's top results are the most topically relevant
SME notes, ranked by BM25.

## How retrieval should reduce prompt-1 derailment

In Task 002C, `qwen3-1.7b` derailed on prompt-1 (triage) into off-topic
multiple-choice + chemistry content, even in direct-answer mode. The grounded
prompt builder (`app/prompt_context.py`) now:

1. Retrieves the relevant SME notes (supplier, inventory, cashflow, credit) for
   the operator's question.
2. Injects them as explicit **local context** into the prompt.
3. Adds **answer rules** that constrain the model: stay on SME operations, do
   not invent facts, answer as a short checklist, and explicitly do not produce
   a `<think>` block or financial-software claims.
4. Instructs the model to tell the operator to **verify records** where needed.

This gives the model concrete, on-topic anchors (reorder points, lead times,
credit limits, cash-on-hand checks) that should keep generation inside the SME
operations domain instead of drifting to unrelated topics. Retrieval does not
*guarantee* no derailment, but it materially raises the floor by narrowing the
relevant context. (Confirming the reduction requires actually running the
grounded prompts through the model — that is Task 003B, deliberately out of
scope here.)

## Limitations

- **Retrieval is keyword/BM25 FTS5**, not semantic/embedding search. It matches
  on terms, so paraphrased concepts may rank lower than exact-term matches.
- The corpus is **small** (8 public placeholder notes). Retrieval is only as
  good as the notes; richer notes → better grounding.
- **No model inference is wired in here.** This task builds the retrieval and
  prompt-preview layer only. Connecting grounded prompts to actual model
  inference is Task 003B.
- Prompt previews in the companion artifact are **not model answers** — they are
  the prompts that would be sent.

## Boundaries respected

No UI, no FastAPI, no cloud database, no external API, no private/customer/
banking/payroll/tax data, no ERP claim. Standard library only. No model files,
artifacts, or `.git` content are indexed.

## Runtime artifact paths created

- `artifacts/eval/task-003A-retrieval.md` (this file)
- `artifacts/eval/task-003A-grounded-prompt-preview.md`
- `data/afrekaos_fts.sqlite` (the generated index; gitignored as a build artifact — see below)
