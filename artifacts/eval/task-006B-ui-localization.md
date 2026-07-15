# Task 006B — Full UI Localization (Evidence)

> AfrekaOS Offline. Upgraded from "selected-language answer only" (006A) to
> full HyveGrid-style UI localization: the selected language changes the entire
> page chrome — navigation, labels, warnings, form text, job page, progress
> steps, runtime labels, footer, demo page, and status page.

## What was broken

After Task 006A, the model answer could be French, but the page chrome stayed
English: "Mission Control", "Demo Scenarios", "Daily Advisor", "Your Question",
"Operating Guidance", "Runtime Summary", "Runtime Status", boundary warning,
footer — all English regardless of selected language.

## What was changed

- **UI translation registry** in `app/language_mode.py`: `UI_TEXT_BUNDLES` with
  ~60 keys × 6 languages (en/fr/yo/ha/sw/pcm). Functions: `get_ui_text`,
  `get_ui_bundle`, `get_default_prompt`, `get_demo_scenarios`,
  `get_boundary_warning`, `get_footer_text`, `get_progress_steps`.
- **All page templates** in `app/web_templates.py` now accept a `language`
  parameter and render chrome from the bundle: header, banner, nav links,
  page titles, card titles, form labels, buttons, job progress steps, result
  labels, warnings, runtime status labels, status page, footer, error pages,
  demo page.
- **Global language selector** in the header on every page (a compact
  `<form class="langswitch">` with `?lang=` GET; auto-submits via inline
  `onchange` if JS is on, works as plain GET without JS).
- **Language persistence across navigation**: nav links carry `?lang=<code>`;
  job pages render in the job's stored language; advisor POST carries the
  language in a form field and stores it on the job.
- **Localized default prompts**: the advisor textarea default changes with the
  selected language (e.g. French daily prompt about "une petite boutique").
- **`?lang=` query parameter** support in all GET routes.

## Whether HyveGrid localization pattern was found and reused

**Yes.** The HyveGrid Offline repo at
`/Users/amaeteumanah/Desktop/Projects/hyvegrid-offline-adtc-2026` uses the same
discipline (language registry, controlled labels, `?lang=` selector, localized
page chrome). The pattern was reused conceptually — no bee/hive/apiculture
content, product names, or UI wording was copied.

## Supported languages

English (default), Yorùbá, Hausa, Swahili, Nigerian Pidgin, French.

## How selected language is preserved

- **GET pages**: `?lang=<code>` in the URL; the header `<form class="langswitch">`
  switches language by navigating to `/?lang=<code>`.
- **Nav links**: carry `?lang=<code>` (except English, which is the bare URL).
- **Advisor POST**: the `<select name="language">` form field carries the code;
  the job stores `language_code`/`language_label`.
- **Job page**: renders in the job's stored `language_code` regardless of the
  current `?lang=` (so a French job stays French even if the operator navigated
  away and back).

## What remains English by design

- **Retrieval corpus**: the FTS5 notes are English; retrieved context is
  injected as English. Only the answer language is controlled.
- **Technical values**: model paths, job ids, return codes, `clean_answer_chars`,
  `think_trap`, `qwen3-1.7b-q4-k-m` — these are never translated.
- **Route paths**: `/advisor/daily`, `/job/<id>`, `/status` — unchanged.

## Known limitations

- **Yorùbá/Hausa/Swahili** UI translations are best-effort; some strings may be
  imperfect. We do not claim perfect translation.
- **Quality depends on the human-curated bundle**, not the model. The bundle is
  fixed text, not generated.
- **Retrieval remains English** for now.

## No cloud translation

No Google Translate, no external API, no network calls. All UI strings are
baked into the standard-library Python module. Everything runs locally.

## Validation results

- `smoke_language_mode.py` — PASS
- `smoke_ui_localization.py` — PASS (6 localized snapshots saved)
- `smoke_web.py` — PASS
- `smoke_submit_flow.py` — PASS
- `final_validation.py` — Overall: PASS
- `python3 -m unittest discover` — OK, 274 tests

## Snapshots

Generated under `artifacts/eval/task-006B-ui-localization/`:
`fr-home.html`, `fr-daily-advisor.html`, `fr-demo.html`, `fr-status.html`,
`pcm-daily-advisor.html`, `yo-daily-advisor.html`, `localization-smoke-notes.md`.
