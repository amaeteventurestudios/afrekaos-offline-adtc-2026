# Task 004F — Qwen Marker Cleanup (Evidence)

> AfrekaOS Offline. The job answer panel showed the operating guidance but
> still began with `</think>` and ended with `[end of text]`. These are
> model/runtime artifacts and must not be shown to the user.

## What was observed

After Task 004E (prompt-echo fix), the answer panel rendered the correct
operating guidance — but the text began with a leftover `</think>` closing tag
and ended with `[end of text]`. These are Qwen / llama.cpp runtime control
markers that leaked into the visible answer stream.

Reproduced deterministically against the pre-fix extractor:

| Input | Pre-fix output |
|-------|----------------|
| `</think>\n- Check inventory` | `</think>\n- Check inventory` (marker survived) |
| `- Check inventory [end of text]` | `- Check inventory [end of text]` (marker survived) |
| `</think>\n- Check supplier\n[end of text]` | both markers survived |
| `<|endoftext|>\n- Check cash` | token survived |
| `- Check credit\n<|im_end|>` | token survived |

Only the complete `<think>\n\n</think>` block was already removed; lone closing
tags, EOS tokens, and turn markers were not.

## What markers were removed

`app/model_inference._clean_runtime_markers()` now strips (case-insensitive):

- lone leading/inline `</think>`
- lone `<think>` (and `<think />`)
- empty `<think></think>` block remnants
- `[end of text]`
- `[end of turn]`
- `<|endoftext|>`
- `<|im_end|>`
- `<|im_start|>`

After removal, excessive blank lines (3+ newlines) caused by marker deletion are
collapsed to at most 2, and the result is trimmed. Bullets and numbered lists
are preserved; no markdown conversion is forced.

## Is `</think>` no longer visible?

**Yes.** Post-fix, `</think>\n- Check inventory` → `- Check inventory`. A lone
closing `</think>` is **not** classified as a think trap (`think_trap=False`);
valid answer text following it is preserved.

## Is `[end of text]` no longer visible?

**Yes.** Post-fix, `- Check inventory [end of text]` → `- Check inventory`, and
trailing `[end of text]` on its own line is removed. Valid answer text before
it is preserved.

## Did tests pass?

**Yes.** 13 new test cases in `tests/test_model_output_extraction.py`
(`TestRuntimeMarkerCleanup`) cover every marker, the no-trap rule for a lone
`</think>`, `clean_answer_chars` matching the cleaned length, list/bullet
preservation, real-trap preservation, and blank-line collapsing. Full suite:
**227 tests, OK**. `final_validation.py` PASS; `smoke_web` PASS;
`smoke_submit_flow` PASS.

## Was real inference manually retested?

The marker leakage and the fix were reproduced/verified deterministically with
synthetic output mirroring the real model stream (no private data). A full live
re-run was not repeated for this artifact; the marker cleanup runs on every
extraction path (UI and scripts) regardless of input.

## Limitations

- Marker matching is regex-based; a future unknown EOS token could slip through,
  but it would appear as trailing extra text, not a missing answer.
- The cleanup is deliberately conservative: it only removes known control
  markers, never SME terms or business guidance.

## No fabricated numbers

Synthetic reproductions use clearly-labeled fake text. No real inference timing
is claimed here.
