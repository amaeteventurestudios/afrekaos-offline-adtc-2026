# Task 004B — Screenshot Instructions (optional)

> Screenshots are **optional** evidence. The environment may not support GUI
> capture, so HTML/JSON snapshots (via `scripts/capture_ui_evidence.py`) are the
> primary evidence. **Do not include private business data** in screenshots or
> demo prompts.

## How to start the server

```bash
./scripts/run_local_web.sh
```

Then open a browser to http://127.0.0.1:8787.

## Pages to manually screenshot

| URL | Suggested filename |
|-----|--------------------|
| http://127.0.0.1:8787/ | `mission-control.png` |
| http://127.0.0.1:8787/demo | `demo-scenarios.png` |
| http://127.0.0.1:8787/status | `offline-status.png` |
| (one advisor result page after submitting a demo scenario) | `daily-advisor-result.png` |

## Where to save

Place screenshots under `artifacts/eval/task-004B-ui-evidence/` (or a
`screenshots/` subfolder).

## Notes

- Screenshots should not include any private/customer/bank/payroll data.
- Demo prompts are public, challenge-safe SME operations scenarios — safe to
  screenshot.
- If screenshots are not captured, the HTML/JSON snapshots from
  `capture_ui_evidence.py` serve as the evidence record.
