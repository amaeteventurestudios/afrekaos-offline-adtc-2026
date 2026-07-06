# AfrekaOS Offline - Model Bake-Off Summary (Task 002B)

- **Date/time:** 2026-07-06 22:35:30 UTC
- **llama.cpp binary:** /usr/local/bin/llama-completion
- **Binary available:** yes

## Smoke prompt

> A small shop has low sales, missing fast-moving stock, supplier delay, and more customers asking for credit. Give a short operating checklist.

## Candidate matrix

| Candidate | File present | Prompt 1 | Prompt 2 | Smoke |
|-----------|--------------|----------|----------|-------|
| qwen3-1.7b-q4-k-m | yes | yes | yes | yes |
| qwen3-4b-q4-k-m | no | no | no | no |
| granite-4.1-3b-q4-k-m | no | no | no | no |

## Timing / token stats (from actual llama.cpp output)

- qwen3-1.7b-q4-k-m:
    - prompt-1 tokens/sec: 5.11 tokens per second
    - prompt-2 tokens/sec: 5.29 tokens per second
    - smoke   tokens/sec: 5.74 tokens per second

## Winner

- **Status:** unresolved (see artifacts/eval/task-002B-model-bakeoff.md)
- No winner is auto-selected. A winner is locked only after local evidence
  is reviewed and model.lock.json is explicitly created.

## Notes

- No cloud inference, no external API. Fully offline.
- Numbers above are scraped from actual llama.cpp output; nothing fabricated.
