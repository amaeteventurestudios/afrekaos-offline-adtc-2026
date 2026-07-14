# Task 006A — Language Mode (Evidence)

> AfrekaOS Offline. Controlled multilingual response support for English,
> Yorùbá, Hausa, Swahili, Nigerian Pidgin, and French. No cloud translation.

## Whether HyveGrid language files were found

**Yes.** A HyveGrid Offline repo exists at
`/Users/amaeteumanah/Desktop/Projects/hyvegrid-offline-adtc-2026`. Its language
discipline was inspected: a language registry (code → name/native), controlled
UI-text dictionaries, glossary phrases with review-needed flags, a
`?lang=` selector, and English-only retrieval with localized *answers*.

## What was ported conceptually

The **architecture pattern only** — not any bee/hive/apiculture content, product
names, or UI wording:

- A central language registry (`app/language_mode.py`) with code → label/native.
- A normalization + fallback function (unknown → English).
- Per-language response instructions injected into the prompt.
- Glossary files under `data/language/` for each language.
- A language `<select>` in the advisor and demo forms (works without JS).
- The job page displays the selected response language.
- English-only retrieval corpus; only the *answer* language is controlled.
- No cloud translation, no external API.

## Supported languages

| Code | Label | Native |
|------|-------|--------|
| en | English | English |
| yo | Yorùbá | Yorùbá |
| ha | Hausa | Hausa |
| sw | Swahili | Swahili |
| pcm | Nigerian Pidgin | Naija |
| fr | French | Français |

## Why French was added

Francophone West and Central Africa. Clear, simple business French suitable for
the region extends the operator base beyond Anglophone and major Nigerian/East
African trade languages.

## Why retrieval remains English for now

The SQLite FTS5 corpus (`data/sme_operations/`, `data/language/`,
`data/sources/`) is English. Building a parallel non-English corpus or
query-time cross-language matching is a larger task deferred to later work. In
this version, the retrieved context is injected as English, and the model is
instructed to answer in the selected language regardless.

## How selected-language answers work

1. Operator picks a language in the advisor form (`<select name="language">`).
2. POST carries the code to the job; the job stores `language_code`/`language_label`.
3. The worker passes it to `model_inference.run_grounded(language=...)`.
4. `build_grounded_prompt(language=...)` injects the per-language instruction:
   "Answer in X", with a fallback rule to keep difficult terms in English, and an
   explicit "do not use cloud translation" instruction.
5. The job page shows "Response language: <label>".
6. If a term has no clean translation, the model may keep it in English — this is
   intentional (clarity over a wrong word).

## Known limitations

- **Retrieval is English-only.** A future task may add parallel corpus notes.
- **Quality depends on the local model** (qwen3-1.7b-q4-k-m). Smaller models may
  produce mixed-language output or leave terms in English.
- **We do not claim perfect translation.** This is a controlled response mode,
  not a certified translation system.
- The boundary language (not accounting/banking/payroll/tax/lending/ERP) is
  enforced in every language via the answer rules.

## No cloud translation

No Google Translate, no external translation API, no network calls. Everything
runs locally, Python standard library only.

## Whether live inference was manually tested

`scripts/run_language_inference_sample.py` is provided for optional manual
testing when the model and llama runtime are available. It was not run as part
of this artifact (the validation is model-free). The smoke test
(`scripts/smoke_language_mode.py`) validates the configuration and prompt
construction for all six languages without calling the model.

## Validation results

- `scripts/smoke_language_mode.py` — PASS (6 prompt previews written under
  `artifacts/eval/task-006A-language-mode/`).
- `scripts/final_validation.py` — Overall: PASS.
- `scripts/smoke_web.py` — PASS.
- `scripts/smoke_submit_flow.py` — PASS.
- `python3 -m unittest discover` — OK, 251 tests.

## No fabricated numbers

No real inference timing/quality numbers are claimed here. Multilingual answer
quality is a user-facing property that depends on the local model.
