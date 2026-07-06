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
