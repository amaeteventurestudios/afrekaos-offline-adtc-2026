# Task 004C — Advisor Submit & Runtime Feedback Fix (Evidence)

> AfrekaOS Offline. Fix the broken advisor submit experience, remove the vague
> 500 page, add visible progress feedback while the local model runs, and fix
> the broken status banner marker.

## What was observed

Reported symptoms (from the task brief):

1. Clicking "Get operating guidance" on `/advisor/daily` gives no indication
   the local model is running.
2. The request eventually shows a blank "500 — Server error" page.
3. The status banner shows "13 Offline mode" instead of a clean status label.

## Reproduction

The server was started with a deliberately broken model path
(`AFREKAOS_MODEL_PATH=/nonexistent/repro.gguf`) and a demo question was POSTed
to `/advisor/daily`.

### What the actual failure path is

**The most reliable failure is not a 500 — it is a blocking, silent POST.**
With the real model present, `do_POST` calls `_run_advisor()` **synchronously
inside the request handler**. Grounded inference takes roughly **43–69 seconds**
per prompt (see Task 005D numbers). During that entire window the browser shows
**nothing**: no progress, no spinner, no "building context" message. To the user
it looks like the button did nothing.

When inference fails (model missing, binary missing, or timeout), the current
code returns HTTP 200 with a folded-in "Could not run local inference: …"
string rather than a real 500 — **except** when an unexpected exception escapes
`_run_advisor` (template parse error, retrieval crash, unexpected OSError).
That path lands in the bare `except` and renders only:

```
<h2>500 — Server error</h2>
```

with no diagnostics and no route back to a working page. That is the "blank 500
page" symptom.

Captured server log during reproduction (nonexistent model path):

```
127.0.0.1 - - "GET /health HTTP/1.1" 200 -
127.0.0.1 - - "POST /advisor/daily HTTP/1.1" 200 -
```

The body contained the folded error (good), but there was **no progress
feedback during the request** and the global error handler offered **no
diagnostics**.

### Root cause classification

- **Blocking synchronous inference in the request handler** — the primary UX
  defect. No background job, no progress, no redirect.
- **Vague global 500 page** — `do_GET`/`do_POST` `except` blocks render only
  `<h2>500 — Server error</h2>` with no summary, route, or suggested checks.
- **Status banner "13" marker** — the banner relied on a CSS `::before`
  pseudo-element: `.banner .b-item::before { content:"\2713 "; }`. The `\2713`
  is a CSS Unicode escape for the checkmark (U+2713 = ✓). Depending on the
  renderer/stylesheet handling, the escape can be mis-read; the literal text
  "Offline mode" then appears with a stray/blank marker, observed externally as
  "13 Offline mode". **Fix: render explicit, visible marker text in the HTML
  itself** (✓ or "OK"), not via a CSS pseudo-element.

## Fixes applied

1. **In-memory job system.** `POST /advisor/<name>` now creates a job, starts a
   background thread, and **immediately redirects (303) to `/job/<id>`**. The
   user is never left staring at a frozen form.
2. **Progress page.** `GET /job/<id>` renders a progress page that
   auto-refreshes every 3 seconds while the job is queued/running, shows the
   current step, the runtime message, and the final answer or a friendly error.
3. **Client-side loading feedback.** Advisor + demo forms include a tiny inline
   `<script>` (no external files) that disables the button and shows the
   "Running local model…" message on submit. Normal POST still works with JS off.
4. **Friendly error page.** The global handlers now render a diagnostic page:
   error summary, current route, suggested checks (model path, llama binary,
   timeout, terminal logs), and links back to Mission Control / Daily Advisor /
   Offline Status.
5. **Banner fix.** Explicit marker text in HTML (`✓ Offline mode · …`), with
   the CSS pseudo-element removed. Tests assert the page does not contain
   `13 Offline mode`.
6. **Status detail panel** on progress/result pages: model path exists, llama
   binary, retrieval index, locked candidate, local-only mode.
7. **Server-side logging** for POST + job lifecycle (no full question logged).

## No guessing

- The synchronous-blocking-with-no-progress defect is **confirmed** by code
  inspection (`do_POST` → `_run_advisor` inline) and by the 43–69s timings
  already captured in Task 005D.
- The bare 500 page is **confirmed** by reading the `except` blocks.
- The banner marker is **confirmed** as a CSS `content:"\2713 "` pseudo-element
  on line 30 of `web_templates.py`.

## No fabricated numbers

No timing/TPS numbers are claimed in this artifact. Inference timings already
captured in `artifacts/submission/task-005D-ubuntu-8gb-retest.md` are
referenced, not re-invented.
