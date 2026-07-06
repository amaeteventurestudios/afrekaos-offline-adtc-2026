# templates/

Chat templates for AfrekaOS Offline local inference. Offline-only.

## qwen3_nonthinking.jinja

A Qwen3 chat template that forces **non-thinking / direct-answer mode**.

### Why it exists

- Task 002B found that `qwen3-1.7b-q4-k-m` spent its **entire token budget
  inside `<think>...</think>`** and never produced a user-visible SME answer.
- AfrekaOS needs **fast, practical, checklist-style answers** for everyday SME
  operators.
- This template is used **only for local offline inference**. No chain-of-thought
  should be shown to the user; user-visible answers should be practical and
  concise.

### How it works

It is the template equivalent of Qwen3's `enable_thinking=False`. When the
assistant turn begins, it emits an empty `<think>\n\n</think>` block. This
pre-satisfies the model's thinking step so the model proceeds directly to the
final answer within the token budget.

### Usage

```bash
llama-completion -m model/candidates/qwen3-1.7b-q4-k-m.gguf \
  --jinja --chat-template-file templates/qwen3_nonthinking.jinja \
  -p "<prompt>" -no-cnv -n 256
```

Apply this template **only to Qwen3 candidates**. Granite is not Qwen3 and is
unaffected. See `scripts/retest_qwen_direct.sh` for the working invocation.

### Soft switch

A prompt-level soft switch is also supported via `AFREKAOS_QWEN_NO_THINK=1`,
which appends `/no_think` to the prompt for Qwen candidates. The template is the
stronger mechanism; the soft switch is a fallback when `--chat-template-file` /
`--jinja` are unavailable.
