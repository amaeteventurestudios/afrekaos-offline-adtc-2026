# Plan — AfrekaOS Offline (001)

> Sequencing note. Only Task 001 is implemented now; later tasks are sketched so
> the direction is clear.

## Principle

Follow the scoring discipline (see `../../SCORING.md`): **do not optimize the
UI before the model path is clear.** Layer 1 (model + runtime behavior) is
automated and harsh; Layer 2 (app, retrieval, language, UI) supports the demo
and defense.

## Phase 0 — Skeleton (this task, 001)

- Create repo structure.
- Create `metadata.json`, `download_model.sh`, root docs, spec kit.
- No model, no UI, no dependencies.

**Exit criteria:** committed and pushed to `main`.

## Phase 1 — Model and runtime path (later)

- Lock the GGUF model and quantization for 8 GB RAM / integrated graphics.
- Stand up llama.cpp runtime on Ubuntu 22.04.
- Verify offline behavior: no network calls during judged runtime.
- Profile RAM and TPS; record evidence under `artifacts/eval/`.
- Wire `model/afrekaos.gguf` as the runtime path.

**Exit criteria:** model loads, runs the two test prompts offline, within RAM
budget, at acceptable TPS.

## Phase 2 — Retrieval layer (later)

- Build SQLite FTS5 index over public SME operations notes in `data/`.
- Implement retrieval that grounds the model's reasoning.
- Keep the corpus public and challenge-safe.

**Exit criteria:** retrieval returns relevant operational context for the two
test prompts, fully offline.

## Phase 3 — App and story (later)

- Local browser app on localhost.
- Operator-facing flows for inventory, cashflow, credit, supplier, staffing,
  expansion.
- Yoruba mode as a language-mode target.

**Exit criteria:** demoable, defensible, offline.

## Sequencing rules

1. Lock model + runtime before building UI.
2. Retrieval before UI.
3. Never introduce a cloud/external-API dependency at any phase.
