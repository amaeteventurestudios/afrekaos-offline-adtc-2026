# Screenshot Checklist — AfrekaOS Offline (Task 005B)

> Exact pages to capture for the final visual evidence set.
> Local UI runs at **http://127.0.0.1:8787** (offline only).

## Prerequisites

1. The model must be present at `model/afrekaos.gguf` for the one inference
   screenshot (shot 07). If it is absent, capture shots 01–06 only and mark
   shot 07 as "not captured — model not present."
2. Start the local UI:

   ```
   ./scripts/run_local_web.sh
   ```

3. Confirm it is live: open http://127.0.0.1:8787/health in a browser; you
   should see JSON with `"ok": true`.

## Capture settings (recommended)

- Browser window: ~1280×800 (or your native width). Full-page or viewport
  capture both acceptable.
- Format: PNG.
- Save into this directory (`artifacts/submission/visual-evidence/`).

## Shots to capture

| # | Filename | URL | What it shows |
|---|----------|-----|---------------|
| 01 | `01-mission-control.png` | http://127.0.0.1:8787/ | Landing page (Mission Control): offline banner, local-model + SQLite-retrieval + no-cloud cards, advisor links. |
| 02 | `02-demo-scenarios.png` | http://127.0.0.1:8787/demo | Demo Scenarios page: four ready-made SME scenarios (demo prompts only). |
| 03 | `03-daily-operations-advisor.png` | http://127.0.0.1:8787/advisor/daily | Daily Operations Advisor input form. |
| 04 | `04-inventory-stock-check.png` | http://127.0.0.1:8787/advisor/inventory | Inventory and Stock Check input form. |
| 05 | `05-cashflow-pressure-coach.png` | http://127.0.0.1:8787/advisor/cashflow | Cashflow Pressure Coach input form. |
| 06 | `06-offline-system-status.png` | http://127.0.0.1:8787/status | Offline System Status: locked model, retrieval index, llama binary, no-cloud statement. |
| 07 | `07-daily-advisor-result.png` | http://127.0.0.1:8787/advisor/daily (after submit) | A real Daily Operations Advisor result page using the prompt below. |

## Shot 07 — exact prompt (demo only)

Paste this **exact** prompt into the Daily Operations Advisor and capture the
result page:

> A small shop has lower sales than usual, two fast-moving items are out of
> stock, the supplier delivery is delayed, and more customers are asking for
> credit. Give a short operating checklist.

This is a demo prompt. It contains no private business data.

## Warnings

- **Do not use private business data.** Use demo prompts only.
- **Do not show customer names, bank records, payroll records, tax records, or
  private company data.**
- **Do not fabricate screenshots.** If you cannot capture a shot, leave the file
  absent and record it in `evidence-manifest.md` as "not captured."

## How to capture manually (no automation)

1. Open each URL in a browser.
2. Use the OS screenshot tool:
   - macOS: `Cmd + Shift + 4` (region) or `Cmd + Shift + 5` (screenshot app).
   - Ubuntu: `Print Screen` / `Shift + Print Screen` (region) or the
     "Screenshot" / "GNOME Screenshot" tool.
3. Rename the file to the suggested filename and move it into this directory.

No browser automation dependency is required or used.

## Status after this task

See `evidence-manifest.md` for which shots were actually captured (if any)
versus left as instructions only.
