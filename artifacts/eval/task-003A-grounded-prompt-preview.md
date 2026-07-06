# Task 003A — Grounded Prompt Previews

> These are **prompt previews, not model answers.** No model inference was
> called to produce this file. Each preview is the full prompt that
> `app/prompt_context.build_grounded_prompt()` would hand to a local runtime
> (e.g. `llama-completion`). Retrieved context is real (from the SQLite FTS5
> index), captured on 2026-07-06.

The structure of every grounded prompt is:
1. **AfrekaOS role** line.
2. **Local SME operations context** (up to 5 retrieved snippets, with sources).
3. **Operator question**.
4. **Answer rules** (practical steps, stay on SME ops, no accounting/banking/
   payroll/tax/ERP claims, no invented facts, no `<think>` block, short
   checklist, verify records where needed).
5. A trailing `Answer:` cue.

For the full answer-rule text see `app/prompt_context.py` (`ANSWER_RULES`).
Below, each preview shows the retrieved context and the question; the role and
rules are identical across previews and summarized once.

Common header (prepended to every preview):
```
You are AfrekaOS, an offline SME operations copilot for African small business operators.
```

Common answer rules (appended to every preview):
```
- Give practical, concrete operating steps.
- Stay strictly on SME operations (inventory, cashflow, credit, supplier, staffing, expansion).
- Do NOT make accounting, banking, payroll, tax-filing, or ERP claims.
- Do NOT invent facts. If records or numbers are needed, say so.
- Do NOT include hidden chain-of-thought or a <think> block. Answer directly.
- Answer as a short checklist.
- Where the operator should verify their own records before acting, say so explicitly.
```

---

## Preview 1 — Metadata prompt 1 (daily operations triage)

**Retrieved context (real):**

1. `[sme_operations] Supplier` — *"...delivery cascades into stockouts, lost
   sales, and credit pressure. Operator resilience depends on knowing lead
   times, having alternatives, and not being over-dependent on one supplier."*
2. `[sme_operations] Inventory` — *"...fast-moving item vs. typical daily/weekly
   run-rate. Reorder lead time per supplier. Which stockouts are driving the
   sales dip right now?"*
3. `[sme_operations] Cashflow` — *"...how much cash is tied up in customer
   credit. When the next supplier payment is due vs. when cash arrives..."*
4. `[language] Yoruba mode` — *(language-mode placeholder, lower relevance.)*
5. `[sme_operations] Staffing` — *"...coverage plan during peak hours..."*

**Operator question:**
> A small shop owner reports that sales are lower than usual, two fast-moving
> items are out of stock, customers are asking for credit, and the supplier
> delivery is delayed. What should they check first, and what should they avoid
> doing immediately?

This is the prompt that should counter the Task 002C prompt-1 derailment: the
retrieved context directly anchors the model on supplier lead times, stock-cover
checks, and cashflow/credit discipline, and the rules forbid off-topic and
chain-of-thought output.

---

## Preview 2 — Metadata prompt 2 (expansion readiness)

**Retrieved context (real):**

1. `[sme_operations] Expansion readiness` — *"...whether the operator's records,
   staff, cash discipline, and demand base can survive being split across two
   sites."*
2. `[sme_operations] Staffing` — *"...assuming one trusted staff member can
   cover two locations..."*
3. `[sme_operations] Inventory` — *"...stockouts of fast-moving items directly
   cost sales..."*
4. `[language] Yoruba mode` — *(lower relevance.)*
5. `[sme_operations] Cashflow` — *"...cashflow pressure is about timing..."*

**Operator question:**
> A market operator wants to expand from one location to two locations but has
> irregular cash records, one trusted staff member, seasonal customer demand,
> and limited working capital. What risks and readiness factors should they
> evaluate before expanding?

---

## Preview 3 — Smoke prompt

**Retrieved context (real):**

1. `[sme_operations] Supplier` — *"...delivery cascades into stockouts, lost
   sales, and credit pressure..."*
2. `[sme_operations] Inventory` — *"...which items are fast-moving vs.
   slow-moving..."*
3. `[sme_operations] Cashflow` — *"...cashflow pressure is about timing..."*
4. `[sources] Sources` — *"...only public SME operations concepts..."*
5. `[sme_operations] Credit` — *"...customer credit ties up cash..."*

**Operator question:**
> A small shop has low sales, missing fast-moving stock, supplier delay, and
> more customers asking for credit. Give a short operating checklist.

---

## How to regenerate

```bash
python3 scripts/preview_grounded_prompt.py "A small shop owner reports low sales..."
```

To see the full, exact prompt text (with all rules inline) for any question,
run that command — it prints the complete grounded prompt that would be sent to
the model.
