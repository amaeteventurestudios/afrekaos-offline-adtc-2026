# Scoring Discipline — AfrekaOS Offline (ADTC 2026)

> This note adapts an architecture/scoring discipline (originally developed for
> a different challenge shape) to AfrekaOS Offline. Only the discipline is
> reused; the product and use case here are SME operations.

## Core idea

Score the work in layers, and do not let a polished surface mask a weak core.
The model and runtime path are scored automatically and harshly; the app and
story are scored in the demo and defense. Treat them as separate disciplines.

## Layer 1 — Automated / core (the model and runtime path)

These are the things that automated scoring touches directly. Get them right
before anything else:

- The **bare GGUF model** is present and loadable.
- `metadata.json` is correct and consistent with the actual runtime.
- **Quantization** is appropriate for the target hardware (low-cost Ubuntu
  22.04 laptop, 8 GB RAM, integrated graphics).
- **RAM** footprint stays within budget at runtime.
- **TPS** (tokens per second) is acceptable on the target hardware.
- **Profiler / runtime behavior** is sane (no hidden network calls, no cloud
  dependency, no surprise external API usage during judged runtime).

If any of the above is weak, no amount of UI work recovers it.

## Layer 2 — Demo / story (the app and use case)

These support the demo, the African use-case story, and the live defense:

- The **local browser app** on localhost.
- The **SQLite FTS5 retrieval layer** over public SME operations notes.
- **Yoruba mode** as a language-mode target.
- The **UI** that lets an operator reason through inventory, cashflow, credit,
  supplier, staffing, and expansion questions.

## Sequencing rule

**Do not optimize the UI before the model path is clear.**

The order of effort should be:

1. Lock the model + quantization + runtime behavior (Layer 1).
2. Stand up retrieval (SQLite FTS5) so reasoning is grounded.
3. Build the app/UI and language modes on top of a working core (Layer 2).

A slick UI on top of a missing or slow model scores badly. A plain UI on top of
a correct, fast, offline model scores well and is easy to defend.

## Bake-off note (Task 002B)

- AfrekaOS is using a **Qwen-first bake-off** because speed and responsiveness
  matter for daily SME operations. The small/fast Qwen candidate is the default
  to beat; Granite is only a control baseline, not the default.
- The automated score still depends on **actual local profiling**: real RAM,
  real TPS, real first-token latency, and real metadata-prompt outputs — never
  on vendor specs or fabricated numbers.
- UI and retrieval should remain **secondary** until the runtime baseline is
  stable and a winner is locked (`model.lock.json`). See `model.candidates.json`
  and `artifacts/eval/model-bakeoff/rubric.md`.

## Direct-answer note (Task 002C)

- Qwen3 **speed is useful only if it produces visible final answers within the
  token budget.** Task 002B showed that thinking mode can consume the entire
  budget inside `<think>` and yield zero user-visible SME content.
- AfrekaOS should **prefer direct checklist answers over hidden thinking**.
  The non-thinking template (`templates/qwen3_nonthinking.jinja`) and the
  `/no_think` switch exist for exactly this reason.
- The scoring path must capture **actual visible answer quality**, not just
  generation speed. A model that generates fast but traps everything in
  `<think>` is not viable for AfrekaOS, no matter how high its TPS.

## Retrieval note (Task 003A)

- Retrieval (SQLite FTS5 over public SME notes) supports **demo quality and
  answer grounding** — it gives the model on-topic anchors before inference.
- The **automated score is still driven by the model/runtime metadata path**
  (Layer 1). Retrieval does not replace model profiling; it complements it.
- Retrieval should **reduce off-topic SME answers** (e.g. the Task 002C prompt-1
  derailment) but it does not replace model profiling, and it cannot be credited
  as a win until grounded prompts are actually run through the model.
- **Prompt previews are not benchmark answers.** They are inputs; only real
  inference produces scorable outputs.

## Grounded inference note (Task 003B)

- Grounded inference (retrieval context + answer rules before model call)
  supports **demo quality and answer discipline**.
- The automated score still depends on **model/runtime metadata behavior**
  (Layer 1) — grounded outputs do not change the RAM/TPS/model-path score.
- **Retrieval-grounded outputs should be evaluated separately** from raw model
  benchmark outputs. A grounded answer that stays on-topic is a demo-quality
  win, not a model-speed win.
- **Do not count prompt previews as model answers.** Task 003B ran real
  inference; only those outputs are scorable. The Task 003A previews were inputs.

## UI note (Task 004A)

- The local browser UI supports the **demo and local operator experience**.
- Automated scoring still depends on the **model/runtime path and metadata
  prompts** (Layer 1). The UI does not change the model/TPS/RAM score.
- **UI should not be optimized at the expense of runtime reliability.** A slick
  UI on a broken or slow model scores badly; the runtime baseline comes first.
- **Browser answers should be grounded and bounded.** Inference through the UI
  uses retrieval-grounded prompts, bounded generation, and a subprocess timeout
  to avoid runaway output.

## UI evidence note (Task 004B)

- UI evidence (HTML/JSON snapshots, demo scenarios) supports **demo review and
  operator experience**.
- Automated scoring still depends on the **model/runtime metadata path**
  (Layer 1). UI snapshots are not performance benchmarks.
- **Inference evidence must be labeled separately** from static page evidence.
  A static HTML capture of `/advisor/daily` (the form) is not the same as a
  captured model answer; only the latter is scorable output.

## Submit feedback note (Task 004C)

- **UI responsiveness matters for demo trust.** A frozen submit button or a blank
  500 page reads as broken even when the model is working correctly underneath.
- **Long local inference must show progress feedback.** Local CPU inference can
  take 30–90 seconds; the job progress page and client-side loading message make
  that latency visible and explainable rather than silent.
- **Runtime failures must be visible and diagnosable.** A vague "500 — Server
  error" is unacceptable; the friendly error page shows the summary, route, and
  suggested checks (model path, llama binary, timeout, terminal logs).
- **Static UI polish is secondary to functional submit behavior.** A pretty form
  that freezes on submit scores worse than a plain form that redirects to a live
  progress page and returns a grounded answer.

## Answer rendering note (Task 004D)

- **The UI must display the cleaned visible answer text.** A job that completes
  with `return_code=0` and `clean_answer_chars > 0` must show the answer — an
  empty panel under those conditions is a bug, not a model failure.
- **Empty Qwen template think blocks are not thinking traps.** The non-thinking
  template emits `<think>\n\n</think>`; that is `contains_think=True` but
  `think_trap=False`. Only an *unclosed* `<think>` with substantial hidden
  reasoning is a trap.
- **Runtime answer quality is evaluated from `clean_answer`, not raw llama
  logs.** Log lines, timestamps, and the think marker are stripped before
  scoring; the char count shown to the user equals the scored text length.

## Prompt echo note (Task 004E)

- **User-facing answers must not include the hidden prompt, retrieved snippets,
  answer rules, or source paths.** If the answer panel shows "You are AfrekaOS,"
  "Local SME operations context," `source:` paths, or "Answer rules," the
  runtime is echoing the prompt — that is a display defect, not an answer.
- **Retrieval context can support the model, but should not be confused with
  final answer quality.** Grounding improves the answer; it is not the answer
  itself. Score the post-extraction `clean_answer`, not the raw echoed stream.

## Final evaluation note (Task 005A)

- Final validation (`scripts/final_validation.py`) confirms **repo health and
  demo readiness** — all checks pass, all routes render, tests are green.
- UI and retrieval evidence support the **demo story**; they are not
  performance benchmarks.
- Automated scoring still depends on the **model/runtime metadata behavior**
  (Layer 1) — the final package does not change that.
- **The final package does not replace target-hardware benchmarking.** Dev-machine
  TPS/RAM numbers must be re-validated on the Ubuntu 22.04 / 8 GB target.

## Target hardware retest note (Task 005C)

- Target hardware retest is **stronger evidence** than dev-machine timing — it
  captures real wall-clock + TPS on the actual (closest available) machine.
- **Results are machine-specific.** The Task 005C run was on macOS (32 GB), not
  Ubuntu 22.04 / 8 GB, so it is real evidence but **not** final target evidence.
- Automated scoring still depends on the **challenge runtime and metadata
  behavior** — the retest does not change the scoring path.
- **Do not mix static UI evidence with runtime performance evidence.** A UI
  snapshot is not a benchmark; a benchmark output is not a UI screenshot.
