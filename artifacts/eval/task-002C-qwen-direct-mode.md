# Task 002C — Qwen Direct-Answer Mode Retest (Evidence)

> AfrekaOS Offline. Fixes the Task 002B Qwen3 thinking-mode failure and
> determines whether qwen3-1.7b remains viable in direct-answer mode. No
> fabricated numbers.

## Problem discovered in Task 002B

In Task 002B, `qwen3-1.7b-q4-k-m` ran real inference but produced **no
user-visible SME answer** across all three prompts: Qwen3's thinking mode
consumed the entire token budget inside `<think>...</think>`, and the model
never emitted an actual checklist or advice. The mechanical viability floor
(practical SME reasoning, checklist clarity) scored 0, so the winner was left
unresolved.

## What was changed in Task 002C

- **`templates/qwen3_nonthinking.jinja`** — a Qwen3 chat template that forces
  non-thinking / direct-answer mode. It emits an empty `<think>\n\n</think>`
  block before the assistant turn, which is the template equivalent of Qwen3's
  `enable_thinking=False`. Applied only to Qwen candidates.
- **`templates/README.md`** — explains the rationale (fast direct checklist
  answers, no chain-of-thought shown to the user, offline-only).
- **`scripts/retest_qwen_direct.sh`** — executable; retests qwen3-1.7b on the
  three bake-off prompts using the template + `/no_think` soft switch; redirects
  stdin from `/dev/null`; bounds generation; writes outputs + runtime notes
  under `artifacts/eval/model-bakeoff/task-002C/`.
- **`scripts/analyze_qwen_outputs.py`** — dependency-free analyzer: reports
  `<think>` presence, visible answer char count outside think blocks, and a
  PASS/FAIL/INCONCLUSIVE viability signal (PASS requires ≥2/3 outputs with
  useful visible answer text).
- **`scripts/profile_candidates.sh`** updated — now Qwen-aware: applies
  `AFREKAOS_QWEN_NO_THINK=1` and the non-thinking template only to Qwen
  candidates, and records in the summary whether `/no_think` was used, whether
  the template was used, whether any output still contains `<think>`, and
  whether usable answer text appeared.
- **`tests/test_qwen_direct_mode.py`** — validates the artifacts exist and the
  analyzer handles missing files and think/answer logic correctly.

## Whether `/no_think` was used

**Yes.** `AFREKAOS_QWEN_NO_THINK=1` appended `/no_think` to all Qwen prompts in
the retest.

## Whether the custom template was used

**Yes.** `--jinja --chat-template-file templates/qwen3_nonthinking.jinja` was
applied, plus `-no-cnv` (clean single-turn) via `llama-completion`.

## Whether qwen3-1.7b produced user-visible answers

**Yes — the thinking-mode trap is fixed.** The analyzer confirms **no `<think>`
block in any of the three outputs** (contrast with Task 002B, where 100% of
tokens were trapped in `<think>`).

Per-prompt result (mechanical viability):

| Prompt | `<think>` present | visible answer chars | useful (≥60) |
|--------|-------------------|----------------------|--------------|
| prompt-1 | no | 783 | yes |
| prompt-2 | no | 1094 | yes |
| smoke    | no | 963  | yes |

**Analyzer verdict: PASS** (3/3 outputs produced useful visible answer text
outside `<think>`).

### Answer-quality notes (honest)

The mechanical signal passes, but answer quality is **mixed**:

- **smoke prompt**: produced a usable 5-item operating checklist (check
  inventory, contact supplier, address credit, improve service, review pricing).
  One item ("Offer credit to customers who need it") is mildly reckless vs the
  rubric's "avoid reckless credit advice", but the answer is coherent and on-topic.
- **prompt-2 (expansion)**: produced a **strong, well-structured** SME risk
  analysis (financial risk from irregular cash records / limited working
  capital, operational risk from seasonal demand). Genuinely usable.
- **prompt-1 (triage)**: **derailed.** It gave a multiple-choice-style answer
  ("B. Check the sales and inventory status") then hallucinated off-topic
  content (Mendeleev's Periodic Table, electron configurations). The visible
  text passes the char threshold, but the actual SME content is not usable.

So: 2 of 3 answers are genuinely usable; 1 derailed. The direct-mode fix is
necessary but the model still needs prompt-engineering hardening (e.g., a
stronger system prompt, stop tokens, or a larger non-thinking model) to be
reliable across all SME prompts.

## Whether timing/TPS/memory was captured

Yes, from actual `common_perf_print` output (run on the **development** Darwin
x86_64 machine, not the target Ubuntu hardware — these are not final
target-hardware numbers):

| Metric | Value |
|--------|-------|
| generation tokens/sec (prompt-1) | 4.02 |
| prompt-eval tokens/sec (prompt-1) | 28.66 |
| projected host memory | 5410 MiB |
| model load time | ~2.2–2.6 s |

Memory fits the 8 GB target with headroom.

## Whether qwen3-1.7b remains viable

**Conditionally yes.** Direct-answer mode eliminates the thinking-mode trap
(the blocking failure from Task 002B) and produces visible answers within the
token budget at acceptable speed and memory. It is viable enough to serve as
the **first canonical model** so the project can proceed to retrieval (Task
003), with the prompt-1 derailment tracked as an unresolved item.

## Whether winner is still unresolved

**Resolved to qwen3-1.7b-q4-k-m** as the first canonical candidate. This is a
working baseline lock, not a final endorsement — see unresolved items below.
`model.lock.json` is created and the candidate is symlinked to
`model/afrekaos.gguf`.

## Whether `model.lock.json` was created

**Yes.** See `model.lock.json`. `model/afrekaos.gguf` is a relative symlink to
`model/candidates/qwen3-1.7b-q4-k-m.gguf`.

## Unresolved items

1. **prompt-1 derailment.** qwen3-1.7b derailed into off-topic multiple-choice
   on the triage prompt even in direct mode. Needs prompt/system-prompt
   hardening or a larger non-thinking model. Recommend Task 002D: acquire and
   test `qwen2.5-3b-instruct-q4-k-m` (no thinking-mode trap) or `qwen3-4b`.
2. **Target-hardware profiling.** All TPS/memory numbers are from the dev
   machine. Re-profile on the Ubuntu 22.04 / 8 GB target.
3. **No comparison candidate.** Only qwen3-1.7b has been profiled. A control
   (granite) and a reasoning fallback (qwen3-4b) are still absent.

## Boundaries respected

No UI, no SQLite retrieval, no FastAPI, no cloud inference/external API, no
private/banking/payroll/tax data, no ERP claim. Product name and the two
metadata prompts unchanged.

## Runtime artifact paths created

- `artifacts/eval/model-bakeoff/task-002C/qwen3-1.7b-direct-prompt-1.txt`
- `artifacts/eval/model-bakeoff/task-002C/qwen3-1.7b-direct-prompt-2.txt`
- `artifacts/eval/model-bakeoff/task-002C/qwen3-1.7b-direct-smoke.txt`
- `artifacts/eval/model-bakeoff/task-002C/qwen3-1.7b-direct-runtime-notes.md`
- `artifacts/eval/task-002C-qwen-direct-mode.md` (this file)
