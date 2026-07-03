# Quickstart — AfrekaOS Offline (001)

> Skeleton stage. There is **no runnable app yet**. This documents the intended
> shape and the only thing that runs today.

## Today (skeleton)

The only executable piece right now is the safe model-fetch placeholder:

```bash
# Create model/ if missing. Does NOT download anything.
./download_model.sh
```

That's it. No server, no UI, no model is loaded.

## Intended quickstart (once later tasks land)

```bash
# 1. (Later) Fetch the locked GGUF model.
./download_model.sh

# 2. (Later) Build the SQLite FTS5 index from the public corpus.
#    scripts/build_index.sh     # not implemented yet

# 3. (Later) Start the local browser app on localhost.
#    scripts/run.sh             # not implemented yet

# 4. Open the local app in a browser and run a prompt.
```

## Runtime expectations (target)

- OS: Ubuntu 22.04
- RAM: 8 GB
- GPU: integrated graphics
- Network: **none required** during judged runtime

## Test prompts

The two canonical test prompts live in `../../metadata.json` under
`test_prompts`. Use those exact strings for evaluation.

## What is not supported

- No cloud, no external API, no internet dependency during judged runtime.
- No customer, bank, tax, or payroll data.
- Not accounting, banking, tax, payroll software, or an ERP.

If something in this quickstart claims more than the repo can do, the repo is
wrong, not the operator. File it under Task 001 follow-ups.
