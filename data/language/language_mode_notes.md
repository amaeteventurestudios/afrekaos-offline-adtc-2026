# Language Mode Notes — AfrekaOS Offline

> Task 006A. How the controlled multilingual response mode works.
> Public, challenge-safe. No private data.

## Supported languages

| Code | Label | Native |
|------|-------|--------|
| en | English | English |
| yo | Yorùbá | Yorùbá |
| ha | Hausa | Hausa |
| sw | Swahili | Swahili |
| pcm | Nigerian Pidgin | Naija |
| fr | French | Français |

## How it works

- The operator selects a response language in the advisor UI (English default).
- The selected language code is passed through the job → grounded prompt →
  local model.
- A per-language instruction tells the model which language to answer in.
- **Retrieval remains English** in this version: the SQLite FTS5 corpus is
  English, and the retrieved context is injected as-is. Only the *answer*
  language is controlled.
- There is **no cloud translation** and **no external API**. The local model
  produces the localized answer directly.

## Fallback behavior

- Unknown / unsupported language codes fall back to English.
- If a term has no clean translation in the selected language, the model is
  instructed to keep that business term in English for clarity (e.g. "stockout"
  or "supplier" may remain in English inside a Yorùbá answer).
- This is intentional: clarity is preferred over a wrong or invented word.

## Why these languages

- **English** — default; the retrieval corpus is English.
- **Yorùbá, Hausa, Swahili** — major African trade/operator languages.
- **Nigerian Pidgin** — widely spoken in Nigerian markets; kept simple and
  respectful (not comic exaggeration).
- **French** — Francophone West and Central Africa; clear, simple business
  French suitable for the region.

## Limitations

- **Retrieval is English-only** for now. A future task may add parallel
  non-English corpus notes or query-time matching.
- **Quality depends on the local model** (qwen3-1.7b-q4-k-m). Smaller models
  may produce mixed-language answers or leave difficult terms in English.
- **We do not claim perfect translation.** This is a controlled response mode,
  not a certified translation system.
- The boundary language (not accounting/banking/payroll/tax/lending/ERP) is
  enforced in every language.

## No cloud translation

No Google Translate, no external translation API, no network calls. Everything
runs locally, standard-library only.
