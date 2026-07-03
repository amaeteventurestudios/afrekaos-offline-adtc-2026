# Tasks — AfrekaOS Offline (001)

Status legend: `[ ]` pending · `[~]` in progress · `[x]` done

## Task 001 — Repository skeleton (this file's task)

- [x] Create directory structure (`model/`, `app/`, `data/*`, `scripts/`,
      `tests/`, `artifacts/*`, `specs/001-afrekaos-offline/`).
- [x] `metadata.json` with product, domain, runtime, model path placeholder, and
      exactly two test prompts.
- [x] `download_model.sh` safe placeholder (creates `model/`, executable, no
      fetch).
- [x] `REPORT.md` draft (Problem, African SME context, Offline design, Model and
      runtime, Retrieval layer, Limitations, How to run).
- [x] `README.md` (public ADTC-style edition, local-first thesis, no overclaim).
- [x] `SCORING.md` scoring discipline note.
- [x] `.gitignore` (model, gguf, venv, pycache, DS_Store; ignore generated JSON
      in artifacts but not markdown evidence).
- [x] `LICENSE`.
- [x] Spec kit: `spec.md`, `plan.md`, `tasks.md`, `research.md`,
      `data-model.md`, `quickstart.md`.
- [x] Placeholder corpus notes under `data/` (public, challenge-safe).
- [x] Initialize git, set remote, branch `main`, commit, push.

## Future tasks (sketched, not started)

### 002 — Model and runtime path

- [ ] Select and lock a GGUF model + quantization for 8 GB RAM / integrated
      graphics.
- [ ] Stand up llama.cpp runtime on Ubuntu 22.04.
- [ ] Verify zero network calls during judged runtime.
- [ ] Profile RAM and TPS; record evidence in `artifacts/eval/`.
- [ ] Update `download_model.sh` to fetch the locked model with a checksum.

### 003 — Retrieval layer

- [ ] Define the SQLite FTS5 schema (see `data-model.md`).
- [ ] Index the public SME operations corpus in `data/`.
- [ ] Wire retrieval into the reasoning path.

### 004 — Local browser app

- [ ] Localhost server scaffolding (no external deps).
- [ ] Operator flows: inventory, cashflow, credit, supplier, staffing,
      expansion.
- [ ] Yoruba mode (language target).

### 005 — Evaluation and submission

- [ ] Run the two test prompts and capture outputs.
- [ ] Package submission artifacts under `artifacts/submission/`.
