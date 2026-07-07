# Task 003B — Grounded Inference (Evidence)

> AfrekaOS Offline. Connects the SQLite FTS5 retrieval layer (Task 003A) to the
> locked Qwen model and compares grounded vs ungrounded outputs. No fabricated
> numbers.

## Why Task 003B exists

Task 002C locked `qwen3-1.7b-q4-k-m` as the first canonical model but left an
unresolved quality issue: prompt-1 (triage) derailed into off-topic
multiple-choice + chemistry hallucination, even in direct-answer mode. Task 003A
built the retrieval layer but did not connect it to the model. Task 003B closes
that loop: it runs grounded vs ungrounded inference and measures whether
retrieval reduces derailment.

## The Task 002C unresolved issue

Prompt-1 in Task 002C produced: *"B. Check the sales and inventory status"* then
drifted into *"Mendeleev's Periodic Table... atomic number 112..."* — completely
off-topic for an SME operations copilot.

## What grounded inference changed

- `app/model_inference.py` — inference helper. Uses `runtime_config` for model
  path/binary, `prompt_context` for grounded prompts. Prefers
  `llama-completion`; supports Qwen direct mode (`/no_think` + non-thinking
  template + `-no-cnv`); stdin from `DEVNULL`; bounded generation + subprocess
  timeout. Provides `build_ungrounded_prompt`, `run_model`, `run_ungrounded`,
  `run_grounded`, `inference_summary`. Returns structured dicts.
- `scripts/run_grounded_inference.py` — runs all 3 prompts × 2 modes (6 runs),
  bounded to 200 tokens, 150s timeout each. Writes outputs + runtime notes +
  comparison under `artifacts/eval/task-003B-grounded-inference/`.
- `scripts/analyze_grounded_outputs.py` — reports `<think>` traps, visible
  answer chars, derailment terms, SME-term presence; PASS/FAIL/INCONCLUSIVE
  verdict on prompt-1 grounding.

## Whether retrieval index was available

**Yes.** The Task 003A index (`data/afrekaos_fts.sqlite`, 8 documents) was
present and used directly.

## Whether model inference ran

**Yes — all 6 runs completed** via `llama-completion` (build 9700) on the
development Darwin x86_64 machine. No timeouts. All outputs non-empty.

## Whether Qwen direct-answer controls were used

**Yes.** `AFREKAOS_QWEN_NO_THINK=1` + `templates/qwen3_nonthinking.jinja`
(`--jinja --chat-template-file`) + `-no-cnv` via `llama-completion`.

## Whether outputs contained `<think>` traps

**No.** The analyzer's refined logic (which distinguishes the empty template
`<think>\n\n</think>` block from a real unclosed thinking trap) reports **no
thinking traps in any of the 6 outputs**. The raw `<think>` substring appears in
every output because the non-thinking template emits that empty block and the
answer-rule text mentions `<think>` — both are expected, neither is a trap.

## Whether grounded prompt-1 improved over ungrounded prompt-1

**Yes — the derailment is fully resolved.** Neither ungrounded nor grounded
prompt-1 derailed (the answer rules + AfrekaOS role in both modes already kept
the model on SME topics). Grounding further improved specificity:

- **Ungrounded prompt-1**: a correct but generic checklist (check inventory,
  verify stock records, confirm supplier delivery, review credit policies).
- **Grounded prompt-1**: a more focused answer referencing concrete checks
  (stock counts, expiration dates, supplier delivery status, current stock
  availability) drawn from the retrieved inventory/supplier notes.

Grounded outputs also include the term "stockout" (from retrieved notes) which
ungrounded outputs lack — evidence that retrieval context reaches the model.

**Analyzer verdict: PASS** (visible answer, no think trap, no derailment, ≥2
SME operating terms).

## Any visible timing/TPS/memory from actual runtime output

| Run | generation tok/s |
|-----|------------------|
| prompt-1 ungrounded | 4.06 |
| prompt-1 grounded | 3.48 |
| prompt-2 ungrounded | 3.80 |
| prompt-2 grounded | 3.35 |
| smoke ungrounded | 3.71 |
| smoke grounded | 3.44 |

Projected host memory: 5410 MiB (fits the 8 GB target). Grounded runs are
slightly slower because the prompt is longer (retrieved context increases
prompt-eval time); generation speed is similar.

> These are development-machine numbers, not target-hardware (Ubuntu 22.04 / 8
> GB) numbers.

## Whether the model remains locked as qwen3-1.7b-q4-k-m

**Yes.** `model.lock.json` is unchanged. `model/afrekaos.gguf` still points to
`model/candidates/qwen3-1.7b-q4-k-m.gguf`. Task 003B did not re-lock or change
the model — it validated that grounding + answer rules resolve the prompt-1
quality issue, which strengthens the case for the current lock.

## Limitations

- **Small sample.** 3 prompts × 2 modes = 6 runs. Not a statistically robust
  quality benchmark.
- **Dev machine, not target hardware.** TPS/memory are from Darwin x86_64.
- **Retrieval is BM25 keyword search**, not semantic. Paraphrased concepts may
  rank lower.
- **Answer quality is still imperfect.** The grounded prompt-1 answer is short
  and could be more actionable; the smoke checklist is good but occasionally
  generic. Corpus expansion and prompt tightening (Task 003C) would help.
- **The role+rules alone fixed the derailment**, so the marginal contribution
  of retrieval (vs just having good answer rules) is specificity, not
  derailment prevention per se.

## Boundaries respected

No UI, no FastAPI, no cloud database/inference/external API, no private/
banking/payroll/tax data, no ERP claim. Bounded generation prevented runaway
output. No fabricated numbers.

## Runtime artifact paths

- `artifacts/eval/task-003B-grounded-inference/prompt-1-ungrounded.txt`
- `artifacts/eval/task-003B-grounded-inference/prompt-1-grounded.txt`
- `artifacts/eval/task-003B-grounded-inference/prompt-2-ungrounded.txt`
- `artifacts/eval/task-003B-grounded-inference/prompt-2-grounded.txt`
- `artifacts/eval/task-003B-grounded-inference/smoke-ungrounded.txt`
- `artifacts/eval/task-003B-grounded-inference/smoke-grounded.txt`
- `artifacts/eval/task-003B-grounded-inference/runtime-notes.md`
- `artifacts/eval/task-003B-grounded-inference/comparison.md`
- `artifacts/eval/task-003B-grounded-inference.md` (this file)
