# Final Runbook — AfrekaOS Offline

> How to clone, validate, and run AfrekaOS Offline end to end.

## Clone

```bash
git clone https://github.com/amaeteventurestudios/afrekaos-offline-adtc-2026.git
cd afrekaos-offline-adtc-2026
```

## Model note

- `model/` is **gitignored** — the GGUF file is not committed (it is large).
- `model/afrekaos.gguf` **must exist locally** at runtime. It is a relative
  symlink to `model/candidates/qwen3-1.7b-q4-k-m.gguf`.
- `model.lock.json` records the selected baseline (`qwen3-1.7b-q4-k-m`).
- To acquire the model, see `download_model.sh` (or place the GGUF manually).
- Without a local model, the UI still renders; advisor answers show a clear
  "could not run local inference" error.

## Build the retrieval index

```bash
python3 scripts/build_retrieval_index.py
```

This creates `data/afrekaos_fts.sqlite` (8 documents, SQLite FTS5).

## Run full validation

```bash
python3 scripts/final_validation.py
```

This runs metadata checks, candidate checks, retrieval build/query, prompt
preview, grounded-output analyzer, web smoke test, UI evidence capture, and the
full unittest suite. Writes a log to `artifacts/submission/final-validation-log.md`.

## Run the web app

```bash
./scripts/run_local_web.sh
```

Then open: **http://127.0.0.1:8787**

## Run grounded inference (offline)

```bash
AFREKAOS_QWEN_NO_THINK=1 python3 scripts/run_grounded_inference.py
```

Runs the two metadata prompts + smoke prompt, grounded vs ungrounded, bounded
generation. Outputs under `artifacts/eval/task-003B-grounded-inference/`.

## Capture UI evidence

```bash
python3 scripts/capture_ui_evidence.py
```

Optional real inference capture (requires model + llama binary):

```bash
AFREKAOS_CAPTURE_INFERENCE=1 python3 scripts/capture_ui_evidence.py
```

## Quick commands summary

| Task | Command |
|------|---------|
| Build retrieval index | `python3 scripts/build_retrieval_index.py` |
| Full validation | `python3 scripts/final_validation.py` |
| Run web app | `./scripts/run_local_web.sh` |
| Grounded inference | `AFREKAOS_QWEN_NO_THINK=1 python3 scripts/run_grounded_inference.py` |
| UI evidence | `python3 scripts/capture_ui_evidence.py` |
| Smoke test (no model) | `python3 scripts/smoke_web.py` |
