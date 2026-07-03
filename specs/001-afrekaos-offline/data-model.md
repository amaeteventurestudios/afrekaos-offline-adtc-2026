# Data Model — AfrekaOS Offline (001)

> Skeleton-stage design. Schema names are proposed, not yet implemented. All
> content is public SME operations concepts; no private records.

## 1. Storage layers

| Layer       | Tech        | Purpose                                              | Status        |
| ----------- | ----------- | ---------------------------------------------------- | ------------- |
| Corpus      | Markdown    | Public SME operations notes under `data/`            | Placeholder   |
| Retrieval   | SQLite FTS5 | Full-text index over the corpus for grounding        | Not built yet |
| Runtime     | GGUF        | Local model at `model/afrekaos.gguf`                 | Not locked    |
| Artifacts   | Files       | Eval + submission outputs under `artifacts/`         | Empty         |

## 2. Corpus taxonomy (`data/`)

Notes are organized by operational domain so retrieval can map a prompt to the
right context:

```
data/
  sme_operations/
    inventory.md         # stock, stockouts, fast-moving items, reorder points
    cashflow.md          # cash pressure, working capital, timing
    credit.md            # customer credit decisions, risk, limits
    supplier.md          # supplier delays, relationships, alternatives
    staffing.md          # trusted staff, coverage, delegation
    expansion.md         # multi-location readiness, risk factors
  language/
    yoruba_mode.md       # Yoruba language-mode design notes (placeholder)
  sources/
    README.md            # provenance for any public references used
```

Each corpus note is plain markdown with a clear heading, a short concept
summary, and (where relevant) checklists of what to check and what to avoid.

## 3. Retrieval schema (proposed, SQLite FTS5)

Conceptual only — to be implemented in Task 003:

```sql
-- One row per retrievable chunk of a corpus note.
CREATE VIRTUAL TABLE sme_ops_chunks USING fts5(
  doc_id,        -- e.g. 'inventory'
  heading,       -- section heading within the note
  body,          -- the chunk text
  tags,          -- operational tags, e.g. 'stockout reorder fast-moving'
  language       -- 'en' | 'yo'
);
```

Query path: prompt → extract operational signals → FTS5 query → top-k chunks →
grounded prompt to the local model.

## 4. Metadata (`metadata.json`)

Already created at repo root. Key fields used downstream:

- `runtime.model_format = "gguf"`, `runtime.engine = "llama.cpp"`.
- `model.path = "model/afrekaos.gguf"` (placeholder).
- `test_prompts[]` — exactly two prompts used for eval.

## 5. Artifacts layout

```
artifacts/
  eval/         # profiling + prompt outputs (RAM, TPS, responses)
  submission/   # final packaged submission
```

Machine-generated JSON under `artifacts/` is gitignored; markdown evidence is
kept.
