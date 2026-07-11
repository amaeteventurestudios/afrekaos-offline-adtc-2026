# Demo Video Shot List — AfrekaOS Offline (Task 005B)

> A 2–3 minute screen-recording plan. Offline only.
> Pair this with `demo-video-script.md` (the spoken narration).

## Setup

1. Ensure `model/afrekaos.gguf` is present (needed for the live advisor result).
2. Start the local UI:

   ```
   ./scripts/run_local_web.sh
   ```

3. Open http://127.0.0.1:8787 in a browser.
4. Recording tool (no dependencies added to the project):
   - macOS: `Cmd + Shift + 5` (built-in screen recording).
   - Ubuntu: GNOME screen recorder, `SimpleScreenRecorder`, or `OBS`.
5. Resolution: ~1280×800. Format: MP4 or WebM.

## Shot-by-shot flow (≈ 2–3 minutes total)

| # | Time | Action | URL | Narration cue |
|---|------|--------|-----|---------------|
| 1 | 0:00–0:15 | Open **Mission Control**. | `/` | Intro + offline/local thesis. |
| 2 | 0:15–0:30 | Point at the offline banner and cards. | `/` | Local model, SQLite retrieval, no cloud. |
| 3 | 0:30–0:45 | Open **Demo Scenarios**. | `/demo` | Ready-made SME scenarios (demo prompts only). |
| 4 | 0:45–1:10 | Select the **low sales / stockout / supplier delay** scenario → submit to the Daily Operations Advisor. | `/advisor/daily` | Explain the prompt and that it is a demo. |
| 5 | 1:10–1:35 | Show the **Daily Operations Advisor result**. | result page | Read the operating checklist; note it is retrieval-grounded. |
| 6 | 1:35–1:50 | Open **Inventory and Stock Check**. | `/advisor/inventory` | Fast-moving items, reorder points, supplier lead times. |
| 7 | 1:50–2:05 | Open **Cashflow Pressure Coach**. | `/advisor/cashflow` | Cash pressure, credit requests, record gaps. |
| 8 | 2:05–2:25 | Open **Offline System Status**. | `/status` | Locked model, SQLite retrieval, no cloud dependency. |
| 9 | 2:25–2:45 | Closing — point out the boundary language. | any page footer | Not accounting/banking/payroll/tax/lending/ERP. |
| 10 | 2:45–3:00 | State the open risk honestly. | `/status` | Ubuntu 22.04 / 8 GB run not yet complete; risk open. |

## Points to call out on screen

- **Local model:** qwen3-1.7b GGUF via llama.cpp, direct-answer mode.
- **SQLite retrieval:** FTS5 over local SME notes; context injected before answering.
- **No cloud dependency:** everything on 127.0.0.1; no external API calls.
- **Operational guidance boundary:** checklists for practical situations only.
- **Not accounting, banking, payroll, tax, lending, or ERP software.**

## Warnings

- **Demo prompts only.** No private business data, customer names, bank,
  payroll, or tax records.
- **Do not fabricate video.** If you cannot record, leave a placeholder and mark
  it "instructions only" in `evidence-manifest.md`.

## Status after this task

See `evidence-manifest.md` for whether a video was actually captured versus left
as instructions only.
