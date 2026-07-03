# scripts/

Operational scripts. **Mostly not implemented yet.**

## Current

- `../download_model.sh` — safe placeholder model fetch (lives at repo root).

## Planned (later tasks)

- `build_index.sh` — build the SQLite FTS5 index from `data/`.
- `run.sh` — start the local browser app on localhost.
- `eval.sh` — run the two test prompts and capture outputs under
  `artifacts/eval/`.

All scripts must respect the offline constraint: no network calls during judged
runtime.
