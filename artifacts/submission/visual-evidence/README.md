# Visual Evidence — AfrekaOS Offline

> Task 005B. Final screenshot and demo-video evidence package.
> **Visual evidence task only — no new product features or dependencies were
> added.**

## Purpose

This directory holds the plan, scripts, and manifest for the final visual
evidence of AfrekaOS Offline: which screenshots and demo video to capture, how
to capture them, and what was actually captured (versus left as instructions).

## Contents

| File | What it is |
|------|------------|
| `screenshot-checklist.md` | Exact pages + filenames to screenshot, with capture steps and safety warnings. |
| `demo-video-shot-list.md` | A 2–3 minute shot-by-shot video plan. |
| `demo-video-script.md` | Plain narration for the 2–3 minute demo video. |
| `evidence-manifest.md` | What visual evidence is expected and what was actually captured. |
| `visual-evidence-prep-log.md` | Output of `scripts/prepare_visual_evidence.py` (verifies the UI is live and summarizes HTML/JSON evidence). Generated when the prep script runs. |

## How to capture

1. Start the local UI (offline only):

   ```
   ./scripts/run_local_web.sh
   ```

2. Open http://127.0.0.1:8787 in a browser.
3. Follow `screenshot-checklist.md` for screenshots.
4. Follow `demo-video-shot-list.md` + `demo-video-script.md` for video.

## Rules (non-negotiable)

- **Demo prompts only.** Use only the prompts in `screenshot-checklist.md` and
  the Demo Scenarios page.
- **No private business data.** Do not enter customer names, bank records,
  payroll records, tax records, or private company data.
- **Do not fabricate screenshots or video.** If a capture cannot be made
  automatically, leave a placeholder and document it as "instructions only."
- **No new dependencies.** No Playwright, Selenium, pyppeteer, npm, or external
  services are used or required.

## Related evidence (already captured)

- HTML/JSON route snapshots: `artifacts/eval/task-004B-ui-evidence/`
- Final evaluation package: `artifacts/submission/final-evaluation-package.md`
- Ubuntu / 8 GB retest note: `artifacts/submission/task-005D-ubuntu-8gb-retest.md`
