# Research — AfrekaOS Offline (001)

> Skeleton-stage notes. These are direction-setting, not final. All references
> are to public concepts; no private data is used.

## 1. Operational problem families

The two test prompts map to two recurring SME operational problem families:

1. **Daily operations triage** — when multiple pressures hit at once (sales dip,
   stockouts of fast-moving items, credit requests, supplier delay), what is the
   correct ordering of checks, and what actions should be avoided in the moment?
2. **Expansion readiness** — moving from one location to two with irregular cash
   records, thin staffing, seasonal demand, and limited working capital. What
   risks and readiness factors should be evaluated first?

These families drive the retrieval corpus taxonomy.

## 2. Offline runtime feasibility

- **GGUF + llama.cpp** is the standard local inference path for CPU/iGPU
  machines. The constraint is RAM, not raw compute.
- On an **8 GB RAM / integrated graphics** Ubuntu 22.04 laptop, a small
  quantized GGUF model is the realistic target. Exact size/quantization is to be
  locked in Task 002, with profiling evidence.
- **TPS** must be measured on the target hardware, not assumed.

## 3. Retrieval shape

- **SQLite FTS5** is appropriate: zero external services, ships with SQLite,
  works offline, and handles the small public corpus well.
- The corpus should be **operationally structured** (inventory, cashflow, credit,
  supplier, staffing, expansion) rather than free-form, so retrieval returns
  actionable context.
- **Grounding** matters more than corpus size. A small, well-structured public
  corpus will outperform a large noisy one for this use case.

## 4. Language mode

- **Yoruba** is named as the initial language-mode target, reflecting the
  operator context. This is a research/design target for later tasks, not a
  skeleton deliverable.
- The skeleton includes a `data/language/` area so language-mode notes have a
  home from day one.

## 5. What to avoid (research anti-goals)

- Do not assume cloud fallback "just for translation" or "just for the model" —
  the offline constraint is absolute during judged runtime.
- Do not pull in customer/bank/tax/payroll data — the product is a reasoning
  copilot, not a financial system of record.
- Do not optimize UI before the model path is locked (see `../../SCORING.md`).

## 6. Open questions (for later tasks)

- Which GGUF model + quantization hits the RAM/TPS budget on the target
  hardware?
- How should retrieval handle the two problem families differently (triage vs.
  expansion)?
- What is the minimum viable Yoruba-mode experience, and does it need a
  translation step or a multilingual model?
