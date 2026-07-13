# Task 004E — Prompt Echo & Final Answer Display Fix (Evidence)

> AfrekaOS Offline. The job answer panel was showing the entire grounded prompt
> (role line, retrieved context, source paths, answer rules) instead of just the
> final operating guidance. This document records the root cause and the fix.

## What was observed

After Task 004D, the job flow rendered text in the answer panel — but the text
was the **full echoed grounded prompt** followed by the answer:

- "You are AfrekaOS..."
- "Local SME operations context..."
- `source:` file paths (e.g. `data/sme_operations/inventory.md`)
- retrieved snippets
- "Operator question:"
- "Answer rules:"
- then the actual checklist

The user-facing answer should show **only** the final operating guidance.

## Whether prompt echo was reproduced

**Yes — reproduced deterministically** by feeding the real grounded prompt
(plus a trailing answer) through the extractor. Before the fix:

```
clean_answer starts with: 'You are AfrekaOS, an offline SME operations copilot...'
contains 'You are AfrekaOS': True
contains 'source:':           True
contains 'Answer rules':      True
clean_chars: 1919            (mostly prompt, not answer)
```

## Root cause (confirmed)

1. **The runtime echoes the prompt into stdout.** `run_model` invokes
   `llama-completion`/`llama-cli` with `-p <prompt>`; depending on the binary,
   the prompt text is echoed at the top of stdout before the model's tokens.
   No `--no-display-prompt` flag was being passed.
2. **The extractor had no prompt-echo awareness.** `extract_visible_answer`
   stripped `<think>` blocks and log lines, but nothing removed the echoed
   prompt — so the role/context/rules/source-paths flowed straight into the
   answer panel.
3. **Latent bug surfaced during the fix:** the answer rules mention `<think>` as
   literal text ("...or a `<think>` block"). The think-strip regex
   `<think>.*` (DOTALL) treated that mention as a real tag and deleted the
   delimiter and everything after it. This is why a delimiter-only fix would
   have silently failed without reordering.

## What was fixed

1. **Explicit answer delimiter.** Both `build_grounded_prompt` and
   `build_ungrounded_prompt` now end with `BEGIN FINAL OPERATING GUIDANCE`
   followed by instructions: answer only after this line; do not repeat local
   context, sources, answer rules, or hidden CoT; give only the final checklist.
2. **`strip_prompt_echo()` + extractor integration.** Extraction now accepts
   the original `prompt` and: (a) prefers text **after** the delimiter; (b) else
   drops an exact prompt prefix; (c) else drops known prompt-echo sections
   (role line, context header, source-path lines, answer-rules header). Returns
   `prompt_echo_detected` and `prompt_echo_stripped`.
3. **Extraction order fixed.** Prompt-echo stripping runs **before** think-block
   stripping, so the `<think>` mention inside the answer rules cannot trigger a
   false think-strip. Think-trap detection was also corrected to run before the
   unclosed-think regex removes its evidence.
4. **Best-effort `--no-display-prompt`.** `run_model` now adds
   `--no-display-prompt` (or `-no-display-prompt`) when the binary supports it
   (checked via `--help`); if unsupported, it silently falls back to
   post-processing. No hard-coded flag that breaks older binaries.
5. **UI cleanup.** The answer panel is titled **"Operating Guidance"** (not the
   old `Operating guidance (retrieval-grounded, direct-answer)`). Mode is shown
   separately in the status panel: Retrieval-grounded / Direct-answer mode /
   Local-only. When prompt echo was stripped, a small runtime note reads
   "Prompt echo removed from display." Runtime summary includes
   `prompt_echo_stripped` when applicable.
6. **Analyzer consistency.** `analyze_grounded_outputs`,
   `analyze_target_benchmark`, and `analyze_qwen_outputs` now report
   `prompt_echo_detected` and `prompt_echo_status` ("clean" / "echo in answer")
   over the *cleaned* answer text. Older artifacts are not auto-failed.

## Whether extraction now strips prompt echo

**Yes.** After the fix, the same echoed input yields:

```
clean_answer: '1. Restock fast-moving items first.\n2. Contact supplier...'
contains 'You are AfrekaOS': False
contains 'source:':           False
contains 'Answer rules':      False
prompt_echo_detected: True, prompt_echo_stripped: True
```

## Whether the delimiter was added

**Yes** — to both grounded and ungrounded prompts (verified by tests in
`tests/test_prompt_echo_extraction.py`).

## Whether real inference was manually tested

The failure and the fix were reproduced/verified deterministically with
synthetic output mirroring the real prompt shape (no private data). A full live
re-run was not repeated for this artifact; the unified extractor + delimiter
make prompt echo structurally removable regardless of whether the binary echoes.

## Whether the final answer now displays only operating guidance

**Yes.** The answer panel shows only the post-delimiter checklist; the prompt,
context, source paths, and rules are stripped. SME terms (stockout, supplier,
cash, credit, records, inventory) in the real answer are preserved — they are
never stripped just for being SME terms.

## Limitations

- Log-line filtering and prompt-echo marker matching are heuristic; an unusual
  future prompt section could occasionally slip through, but it would appear as
  extra text, not as a missing answer.
- `--no-display-prompt` support is binary-dependent; the post-processing
  fallback covers binaries that lack the flag.
- The "Local context used" section (titles + source paths only) was not added as
  a separate panel to avoid new feature complexity; context is consumed by the
  model but not surfaced in the answer.

## No fabricated numbers

The synthetic reproductions use clearly-labeled fake text. No real inference
timing/TPS is claimed here.
