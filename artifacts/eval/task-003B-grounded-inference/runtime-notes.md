# Task 003B Runtime Notes

- **Date/time:** 2026-07-07 (runs captured on development Darwin x86_64 machine)
- **Model path:** model/afrekaos.gguf → model/candidates/qwen3-1.7b-q4-k-m.gguf
- **llama binary:** /usr/local/bin/llama-completion
- **Command family:** llama-completion
- **Index built this run:** no (existing index from Task 003A)
- **Documents indexed:** 8 (6 sme_operations + 1 language + 1 sources)
- **Qwen template present:** yes (templates/qwen3_nonthinking.jinja)
- **/no_think env (AFREKAOS_QWEN_NO_THINK):** 1
- **Max tokens:** 200, timeout: 150s

## Per-prompt comparison

> "<think> trap" below uses the analyzer's refined logic: only an *unclosed*
> `<think>` with real reasoning counts as a trap. The non-thinking template's
> empty `<think>\n\n</think>` block is the intended direct-mode mechanism, not a
> trap. (The raw `<think>` substring appears in every output because the
> template emits that empty block and the answer-rule text mentions `<think>`.)

| Prompt | Mode | ok | <think> trap | visible chars | timed out |
|--------|------|----|--------------|---------------|-----------|
| prompt-1 | ungrounded | yes | no | 955 | no |
| prompt-1 | grounded | yes | no | 1749 | no |
| prompt-2 | ungrounded | yes | no | 1236 | no |
| prompt-2 | grounded | yes | no | 2119 | no |
| smoke | ungrounded | yes | no | 1071 | no |
| smoke | grounded | yes | no | 1826 | no |

## Visible timing / TPS / memory (scraped from actual llama.cpp output)

- prompt-1-ungrounded generation tokens/sec: 4.06
- prompt-1-grounded generation tokens/sec: 3.48
- prompt-2-ungrounded generation tokens/sec: 3.80
- prompt-2-grounded generation tokens/sec: 3.35
- smoke-ungrounded generation tokens/sec: 3.71
- smoke-grounded generation tokens/sec: 3.44
- projected host memory: 5410 MiB (fits 8 GB target)

Note: grounded runs are slightly slower (3.35–3.48 tok/s) than ungrounded
(3.71–4.06 tok/s) because the grounded prompt is longer (includes retrieved
context), so prompt evaluation takes longer. Generation speed is similar.

No fabricated numbers. All stats scraped from real llama.cpp output.
