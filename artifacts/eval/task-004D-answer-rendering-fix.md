# Task 004D — Answer Rendering Fix (Evidence)

> AfrekaOS Offline. The job result page reported "model produced no visible
> answer text" even when the runtime summary reported `return_code=0` and
> `visible_chars > 0`. This document records the root cause and the fix.

## What was observed

On `/job/<id>`, a job completed successfully but the answer panel showed:

```
(model produced no visible answer text)
```

while the runtime summary reported something like:

```
return_code=0, visible_chars=2361, think_trap=True
```

`return_code=0` with `visible_chars > 0` means the model almost certainly
produced text — so an empty answer panel is a rendering/extraction bug, not a
model failure.

## Whether the issue was reproduced

**Reproduced by inspection + synthetic reconstruction (no private data).** A real
job was not re-run end-to-end for this artifact, but the failure mode was
reconstructed deterministically using synthetic output that mirrors the real
llama.cpp output shape. The reconstruction confirms the disagreement between the
two extraction functions.

## What raw output fields existed

`run_model()` runs the subprocess with `stderr=subprocess.STDOUT`, so llama.cpp
log lines and model tokens are interleaved in a single `stdout` string. The
output typically contains:

- llama.cpp log lines (all shaped like `0.03.201.688 I ...`, `W ...`, `L ...`,
  or bare `I llama_model_loader: ...` / `W system_info: ...`).
- the Qwen non-thinking template marker `<think>\n\n</think>` (empty — the
  intended direct-mode signal).
- the actual operating-guidance answer after the marker.

So **yes**, stdout contained the model answer; **yes**, llama logs were present
in the same stream; **yes**, `<think></think>` appeared; and **yes**, answer
text existed outside the think block.

## Root cause (confirmed)

There were **two divergent "visible answer" implementations** that disagreed:

1. `app/model_inference.py::_visible_answer` — used to compute
   `visible_answer_chars` (the number shown in the runtime summary). This
   version's line filter was *narrow* and counted many log lines as "answer".
2. `app/web_app.py::_extract_answer` — used to render the actual UI answer
   panel. This version added an **over-broad `^[IWL]\s+` line filter** that
   stripped *any* line starting with `I `, `W `, or `L ` followed by whitespace.

Because llama.cpp log lines all start with `I`/`W`/`L` (the log-level prefix),
the web_app filter stripped genuine content whenever the answer was sparse
relative to the logs. The two functions disagreed:

```
raw = "<think>\n\n</think>\nI llama_model_loader: loaded\nW system_info: threads\n..."
model_inference._visible_answer -> 186 chars   # counts log lines as "answer"
web_app._extract_answer         -> 0 chars      # over-filters everything
```

That is exactly the reported signature: `visible_chars > 0` (from #1) but an
empty answer panel (from #2).

A **second, related defect**: `model_inference.contains_think` used a bare
`"<think>" in out` substring test, so the intended empty Qwen non-thinking
template `<think>\n\n</think>` was reported as `contains_think=True`. The UI
then labeled that `think_trap=` in the runtime notes — which is how the report
showed `think_trap=True` for a valid direct-mode answer. (The two production
analyzers already correctly distinguished empty-template from a real trap; only
the app layer was wrong.)

## What was fixed

1. **Single source of truth.** Added `app.model_inference.extract_visible_answer(raw_stdout, raw_stderr="")`, which returns a structured dict:
   `clean_answer`, `clean_answer_chars`, `contains_think`, `think_trap`,
   `extraction_warning`. The web UI and `run_model` now both use it, so
   `visible_answer_chars == clean_answer_chars` always.
2. **Smarter log-line filtering.** Log lines are removed only when they match
   the llama.cpp log *shape* (a dotted timestamp, or `I/W/L` + a known log
   prefix like `llama_model_loader`, `system_info`, `common_perf_print`). A
   genuine answer sentence like `"I should restock fast-moving items today."`
   is **not** stripped.
3. **Correct think semantics.** `contains_think` = any `<think>` marker present
   (including the empty template). `think_trap` = an **unclosed** `<think>` with
   substantial trailing content. An empty `<think>\n\n</think>` is
   `contains_think=True, think_trap=False`.
4. **`run_model` structured return** now includes `clean_answer`,
   `clean_answer_chars`, `think_trap`, `extraction_warning`,
   `raw_stdout_chars`, `raw_stderr_chars` (plus backwards-compatible
   `visible_answer_chars`, `stdout_chars`, `stderr_chars`, `contains_think`).
5. **Job rendering.** The worker uses `result["clean_answer"]` directly; the
   job page shows it when `clean_answer_chars > 0`, shows the extraction warning
   if present, and only shows "(model produced no visible answer text)" when the
   answer is genuinely empty. Runtime summary now reports `clean_answer_chars`
   and `think_trap`.
6. **Analyzer consistency.** `analyze_grounded_outputs.py`,
   `analyze_target_benchmark.py`, and `analyze_qwen_outputs.py` now all expose
   distinct `contains_think` and `think_trap` keys; none classify an empty
   template block as a trap. (Dead code in `_has_thinking_trap` removed.)
7. **Optional debug.** `AFREKAOS_DEBUG_OUTPUT=1` writes a small, bounded
   snapshot (no user question) to `artifacts/eval/task-004D-debug/` for the most
   recent job.

## No fabricated numbers

The synthetic reconstructions above use clearly-labeled fake text. No real
inference timing/TPS is claimed here; real numbers live in
`artifacts/submission/task-005D-ubuntu-8gb-retest.md`.
