# Final Validation Log — AfrekaOS Offline (Task 005A)

- **Date/time:** 2026-07-15 03:30:47 UTC
- **Overall:** PASS
- **pytest available:** False
- **Model inference required:** no (all checks are non-inference)
- **Cloud dependencies used:** none

## Checks

| # | Check | Command | Exit code | Status |
|---|-------|---------|-----------|--------|
| 1 | check_metadata | `scripts/check_metadata.py` | 0 | PASS |
| 2 | check_model_candidates | `scripts/check_model_candidates.py` | 0 | PASS |
| 3 | build_retrieval_index | `scripts/build_retrieval_index.py` | 0 | PASS |
| 4 | query_retrieval | `scripts/query_retrieval.py` | 0 | PASS |
| 5 | preview_grounded_prompt | `scripts/preview_grounded_prompt.py` | 0 | PASS |
| 6 | analyze_grounded_outputs | `scripts/analyze_grounded_outputs.py` | 0 | PASS |
| 7 | smoke_web | `scripts/smoke_web.py` | 0 | PASS |
| 8 | capture_ui_evidence | `scripts/capture_ui_evidence.py` | 0 | PASS |
| 9 | unittest discover | `-m unittest discover -s tests -p test_*.py` | 0 | PASS |

## Per-check output (tail)

### check_metadata — PASS
```
METADATA CHECK PASSED
  product_name : AfrekaOS Offline
  domain       : SME operations / African small business operations
  model.path   : model/afrekaos.gguf
  prompts      : 2 (expected 2)
    [1] daily_operations_triage: A small shop owner reports that sales are lower than usual, two fast-m...
    [2] expansion_readiness: A market operator wants to expand from one location to two locations b...

```

### check_model_candidates — PASS
```
CANDIDATES CHECK PASSED
  product        : AfrekaOS Offline
  selection_mode : qwen_first_bakeoff
  winner path    : model/afrekaos.gguf
  candidates     : 3 (expected 3)
    - qwen3-1.7b-q4-k-m      [primary_speed_candidate] local=present
    - qwen3-4b-q4-k-m        [secondary_reasoning_candidate] local=missing
    - granite-4.1-3b-q4-k-m  [control_candidate] local=missing

```

### build_retrieval_index — PASS
```
AfrekaOS retrieval index built
----------------------------------------
database path    : /Users/amaeteumanah/Desktop/Projects/afrekaos-offline-adtc-2026/data/afrekaos_fts.sqlite
documents indexed : 15
FTS5 available    : True
source directories:
  - /Users/amaeteumanah/Desktop/Projects/afrekaos-offline-adtc-2026/data/sme_operations
  - /Users/amaeteumanah/Desktop/Projects/afrekaos-offline-adtc-2026/data/language
  - /Users/amaeteumanah/Desktop/Projects/afrekaos-offline-adtc-2026/data/sources
documents by category:
  - language: 8
  - sme_operations: 6
  - sources: 1

```

### query_retrieval — PASS
```
tions)
     path  : data/sme_operations/staffing.md
     snippet: ...stomer or private data. ## Concept Most small operators rely on a very small number of trusted staff. Coverage, delegation, and trust are the real constraints — not headcount. Expa...
  4. [sme_operations] Cashflow (SME operations)
     path  : data/sme_operations/cashflow.md
     snippet: # Cashflow (SME operations) > Public, challenge-safe placeholder notes. No customer or private data. ## Concept Cashflow pressure is about tim...
  5. [sme_operations] Supplier (SME operations)
     path  : data/sme_operations/supplier.md
     snippet: ...in stock). ## What to avoid - Promising customers restock dates based on the supplier's best case. - Burning the supplier relationship over a single delay. - Carrying no buffer for...

```

### preview_grounded_prompt — PASS
```
ght or a <think> block. Answer directly.
- Answer as a short checklist.
- Where the operator should verify their own records before acting, say so explicitly.

Response language: English
Answer in clear, simple English.
- Do not use cloud translation or any external translation service.
- If a term is difficult to translate, use simple wording or keep the business term in English.
- The retrieved context above may be in English; answer in the selected response language regardless.

BEGIN FINAL OPERATING GUIDANCE
- Answer only after this line.
- Do not repeat the local context.
- Do not repeat the source list.
- Do not repeat the answer rules.
- Do not reveal hidden chain-of-thought.
- Give only the final checklist.


========================================================================

```

### analyze_grounded_outputs — PASS
```
ier delay, and more customers asking for credit. Give a short operating checklist. - Give practical, concrete operating steps. - Stay strict'

[smoke-grounded]
  exists            : yes
  <think> present   : True
  think trap        : False
  visible chars     : 1826
  derailment terms  : False
  sme terms found   : cash, credit, expansion, inventory, records, staff, stockout, supplier
  answer preview    : '... delivery cascades into stockouts, lost sales, and credit pressure. Operator resilience depends on knowing lead times, having alternatives, and not being over-dependent on one supp...    ...isible '

====================================================
PROMPT-1 GROUNDING VERDICT: PASS
  -> grounded prompt-1 produced visible SME answer, no <think>, no derailment, includes SME terms.

```

### smoke_web — PASS
```
[ok] server is healthy
[ok] / -> 200 (7720 bytes)
[ok] /status -> 200 (7882 bytes)
[ok] /health -> 200 (204 bytes)
[ok] /health is valid JSON: ok=True

SMOKE TEST PASSED

```

### capture_ui_evidence — PASS
```
[ok] server healthy
[ok] /health -> 200 (valid JSON)
[ok] / -> 200 (7720 bytes) -> home.html
[ok] /demo -> 200 (11982 bytes) -> demo.html
[ok] /advisor/daily -> 200 (7957 bytes) -> advisor-daily.html
[ok] /advisor/inventory -> 200 (7977 bytes) -> advisor-inventory.html
[ok] /advisor/cashflow -> 200 (7924 bytes) -> advisor-cashflow.html
[ok] /status -> 200 (7882 bytes) -> status.html
[inference] skipped (set AFREKAOS_CAPTURE_INFERENCE=1 to enable)

EVIDENCE CAPTURE PASSED (7 files)

```

### unittest discover — PASS
```
..................................................................................................................................................................................................................................................................................
----------------------------------------------------------------------
Ran 274 tests in 1.442s

OK

EVIDENCE CAPTURE FAILED:
  - bad route

EVIDENCE CAPTURE PASSED (2 files)

```

## Notes

- The unittest suite uses `unittest discover` (standard library).
- pytest was **not available**; `unittest discover` was used instead.
- `smoke_web.py` and `capture_ui_evidence.py` start a local server on 127.0.0.1:8787 but do **not** call the model.
- No cloud inference, no external API, no internet required.
- No fabricated benchmark numbers.