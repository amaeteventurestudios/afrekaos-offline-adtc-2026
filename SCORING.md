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
