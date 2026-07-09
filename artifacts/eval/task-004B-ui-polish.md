# Task 004B — UI Polish and Evidence

> AfrekaOS Offline. Polishes the standard-library local browser UI, adds a
> `/demo` route with four SME scenarios, and captures evidence snapshots.

## What was added / changed

- **`app/web_templates.py`** — polished: offline status banner (Offline mode ·
  Local model · SQLite retrieval · No cloud dependency), top navigation bar,
  stronger card layout with tags, improved form/answer/runtime/error layouts,
  unified boundary warning on every advisor result, and a new
  `render_demo()` page with four demo-scenario cards.
- **`app/web_app.py`** — added `GET /demo` route; advisor forms/results now
  pass `active` nav keys; all result pages link to Mission Control, Demo
  Scenarios, and Offline Status.
- **`scripts/capture_ui_evidence.py`** — starts the server, fetches all key
  routes, saves HTML/JSON snapshots, verifies HTTP 200 + labels, writes
  evidence-notes.md. Optional bounded inference via
  `AFREKAOS_CAPTURE_INFERENCE=1`.
- **Tests** — `test_web_templates.py` (banner, demo, warning, nav),
  `test_web_app.py` (demo route, no-cloud language), `test_ui_evidence.py`
  (capture script import + helpers).

## Routes polished

| Route | Status |
|-------|--------|
| `/` | polished — banner, nav, 5 cards |
| `/demo` | **new** — 4 demo scenario cards |
| `/advisor/daily` | polished — nav, form |
| `/advisor/inventory` | polished — nav, form |
| `/advisor/cashflow` | polished — nav, form |
| `/status` | polished — nav, status grid |
| `/health` | unchanged (JSON) |

## New `/demo` route

Four demo scenarios with one-click submission to the matching advisor:
1. **Low sales, stockout, supplier delay** → Daily Operations Advisor
2. **Expansion readiness** → Daily Operations Advisor
3. **Inventory pressure** → Inventory and Stock Check
4. **Cash pressure and customer credit** → Cashflow Pressure Coach

## Evidence files created

Under `artifacts/eval/task-004B-ui-evidence/`:
- `home.html`, `demo.html`, `advisor-daily.html`, `advisor-inventory.html`,
  `advisor-cashflow.html`, `status.html`, `health.json`, `evidence-notes.md`

## Whether local server starts

**Yes.** Verified by `capture_ui_evidence.py` (EVIDENCE CAPTURE PASSED, 7 files)
and `smoke_web.py` (SMOKE TEST PASSED).

## Whether `/health` works

**Yes.** Returns valid JSON (`ok: true`).

## Whether screenshots were captured

**No** — only HTML/JSON snapshots were captured. Screenshots are optional
(this environment may not support GUI capture); instructions are in
`artifacts/eval/task-004B-screenshot-instructions.md`.

## Whether inference was tested through evidence capture

**No** — the default capture does not run inference (points model path at a
nonexistent file so pages render without a model). Inference through the UI was
verified in Task 004A. Set `AFREKAOS_CAPTURE_INFERENCE=1` to optionally
capture a bounded inference result.

## Whether cloud dependencies are absent

**Yes.** The entire UI and evidence capture use Python standard library only.
No external CSS/JS/fonts/CDNs/images, no network calls, no cloud services.

## Limitations

- Screenshots are optional (instructions only); not captured in CI.
- Evidence capture does not run inference by default.
- Minimal styling (plain embedded CSS, no framework) — deliberate.

## No fabricated runtime numbers

This artifact reports only HTTP status codes, byte sizes, and file counts
observed during capture. No TPS/RAM claims.
