# Task 002C - Qwen3 Direct-Answer Runtime Notes

- **Date/time:** 2026-07-06 23:18:48 UTC
- **Model path:** /Users/amaeteumanah/Desktop/Projects/afrekaos-offline-adtc-2026/model/candidates/qwen3-1.7b-q4-k-m.gguf
- **llama binary:** /usr/local/bin/llama-completion
- **Binary kind:** llama-completion (llama-completion / llama-cli / llama)
- **/no_think used:** yes
- **Custom template used:** yes
- **Template args:** --jinja --chat-template-file /Users/amaeteumanah/Desktop/Projects/afrekaos-offline-adtc-2026/templates/qwen3_nonthinking.jinja
- **-no-cnv used:** yes (clean single-turn)

## Per-prompt result

- **prompt-1:** think_open=False think_close=False answer_chars=1222
answer_preview='repeat_last_n = 64, repeat_penalty = 1.000, frequency_penalty = 0.000, presence_penalty = 0.000\n\tdry_multiplier = 0.000, dry_base = 1.750, dry_allowed_length = 2, dry_penalty_last_n = -1\n\ttop_k = 40, '
- **prompt-2:** think_open=False think_close=False answer_chars=1537
answer_preview='repeat_last_n = 64, repeat_penalty = 1.000, frequency_penalty = 0.000, presence_penalty = 0.000\n\tdry_multiplier = 0.000, dry_base = 1.750, dry_allowed_length = 2, dry_penalty_last_n = -1\n\ttop_k = 40, '
- **smoke:** think_open=False think_close=False answer_chars=1402
answer_preview='repeat_last_n = 64, repeat_penalty = 1.000, frequency_penalty = 0.000, presence_penalty = 0.000\n\tdry_multiplier = 0.000, dry_base = 1.750, dry_allowed_length = 2, dry_penalty_last_n = -1\n\ttop_k = 40, '

## <think> presence

- prompt-1: think_open=False
- prompt-2: think_open=False
- smoke: think_open=False

## Usable answer text outside <think>

- prompt-1 answer_chars: answer_chars=1222
- prompt-2 answer_chars: answer_chars=1537
- smoke answer_chars: answer_chars=1402

## Visible timing / TPS / memory (from actual llama.cpp output)

- prompt-1 generation tokens/sec: 4.02 tokens per second
- prompt-1 prompt-eval tokens/sec: 28.66 tokens per second
- memory: 0.00.417.952 I common_params_fit_impl: projected to use 5410 MiB of host memory vs. 32768 MiB of total host memory
- Run scripts/analyze_qwen_outputs.py for the viability verdict.

## Artifacts

- /Users/amaeteumanah/Desktop/Projects/afrekaos-offline-adtc-2026/artifacts/eval/model-bakeoff/task-002C/qwen3-1.7b-direct-prompt-1.txt
- /Users/amaeteumanah/Desktop/Projects/afrekaos-offline-adtc-2026/artifacts/eval/model-bakeoff/task-002C/qwen3-1.7b-direct-prompt-2.txt
- /Users/amaeteumanah/Desktop/Projects/afrekaos-offline-adtc-2026/artifacts/eval/model-bakeoff/task-002C/qwen3-1.7b-direct-smoke.txt

No fabricated numbers. All stats above are scraped from real llama.cpp output.
