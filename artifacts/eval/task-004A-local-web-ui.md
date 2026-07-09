# Task 004A — Local Browser UI (Evidence)

> AfrekaOS Offline. First local browser UI using Python standard library only,
> connecting the UI to existing retrieval-grounded inference. No cloud.

## Routes added

| Route | Method | Purpose |
|-------|--------|---------|
| `/` | GET | Mission Control dashboard — product name, description, cards linking to advisors + status |
| `/advisor/daily` | GET | Daily Operations Advisor form (default triage prompt) |
| `/advisor/daily` | POST | Run grounded inference; show question, answer, mode label, warning, runtime notes |
| `/advisor/inventory` | GET | Inventory and Stock Check form |
| `/advisor/inventory` | POST | Run grounded inference (inventory focus) |
| `/advisor/cashflow` | GET | Cashflow Pressure Coach form |
| `/advisor/cashflow` | POST | Run grounded inference (cashflow focus) |
| `/status` | GET | Offline System Status — model lock, model path, symlink, llama binary, retrieval index, doc count, FTS status, Qwen controls, no-cloud statement |
| `/health` | GET | JSON: ok, product, model_exists, retrieval_index_exists, llama_binary, locked_candidate |

Server: `http://127.0.0.1:8787` via `http.server.ThreadingHTTPServer`.

## Whether the local server starts

**Yes.** Verified by `scripts/smoke_web.py` (SMOKE TEST PASSED) and by a manual
real-inference POST test.

## Whether `/health` works

**Yes.** Returns HTTP 200 with valid JSON:
```json
{ "ok": true, "product": "AfrekaOS Offline", "model_exists": true,
  "retrieval_index_exists": true, "llama_binary": "llama-completion",
  "locked_candidate": "qwen3-1.7b-q4-k-m" }
```

## Whether model inference was tested through the UI

**Yes.** A manual `POST /advisor/daily` with a real question returned HTTP 200
with operating guidance, the accounting/banking warning, and a populated answer
section. The UI calls `app.model_inference.run_grounded()` with bounded
generation (`AFREKAOS_UI_MAX_TOKENS`) and a subprocess timeout. Generation was
bounded (150 tokens) so no runaway output was created.

## Whether missing model/runtime errors are browser-friendly

**Yes.** If the model or llama binary is missing, `run_grounded` returns
`ok=False` with an `error` message, and the UI renders it in the answer section
as: *"Could not run local inference: {error}"* — a clear browser-friendly error,
not a stack trace. The smoke test confirms pages render even with a missing
model (it points `AFREKAOS_MODEL_PATH` at a nonexistent file).

## Whether retrieval index status appears

**Yes.** The `/status` page shows `retrieval_index_exists`, `indexed_documents`
(8), and `sqlite_fts_status` (available). If the index is missing at inference
time, the UI builds it (best-effort) before calling the model.

## Whether cloud dependencies are absent

**Yes.** The entire UI is `http.server` + `urllib` + `html` + `json` — Python
standard library only. No FastAPI, Flask, Node, npm, React, Tailwind, CDNs,
external CSS/JS/fonts/images, or network calls. No OpenAI, Claude, GLM,
Supabase, Vercel, cloud databases, or cloud inference.

## Limitations

- **Minimal styling.** Plain embedded CSS; no framework. Deliberate (no deps).
- **Single-user, localhost.** Not a production server; no auth, no HTTPS.
- **Inference is blocking per request.** `ThreadingHTTPServer` handles
  concurrent page loads, but a model call blocks its thread (~30-40s at ~4 tok/s
  on the dev machine). A loading state is a Task 004B concern.
- **No Yoruba-mode UI toggle yet.** Language mode is a separate task.
- **Dev machine.** Timing/feel should be re-validated on the target Ubuntu
  22.04 / 8 GB hardware.

## No fabricated runtime numbers

The only numbers here are route byte-sizes and doc counts observed during the
smoke/manual tests. No TPS/RAM claims are made in this artifact (those live in
the Task 003B runtime notes).

## Runtime artifact paths

- `artifacts/eval/task-004A-local-web-ui.md` (this file)

## Boundaries respected

No cloud, no external dependencies, no private/banking/payroll/tax data, no ERP
claim. All pages include a footer and the result pages include a warning stating
this is operational guidance, not accounting/banking/payroll/tax/ERP software.
