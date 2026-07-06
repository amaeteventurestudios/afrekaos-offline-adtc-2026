# Model Bake-Off Scorecard — AfrekaOS Offline (Task 002B)

> Scored ONLY from real outputs under `artifacts/eval/model-bakeoff/`.
> Run config: `llama-completion`, `MAX_TOKENS=96`, `-t 4`, `--temp 0.7`,
> on the development machine (Darwin x86_64, NOT the target Ubuntu hardware).
> See `rubric.md` for the category definitions and 0-3 scale.

## qwen3-1.7b-q4-k-m (primary speed candidate)

Output files:
- `qwen3-1.7b-q4-k-m-prompt-1.txt`
- `qwen3-1.7b-q4-k-m-prompt-2.txt`
- `qwen3-1.7b-q4-k-m-smoke.txt`

Real timing (from actual llama.cpp `common_perf_print` output):

| Run | prompt eval (tok/s) | generation (tok/s) | load (ms) |
|-----|---------------------|--------------------|-----------|
| prompt-1 | 27.70 | 5.11 | 2621 |
| prompt-2 | 24.09 | 5.29 | 2302 |
| smoke    | 23.91 | 5.74 | 2220 |

| Category                          | Score (0-3) | Notes |
| --------------------------------- | ----------- | ----- |
| Speed / responsiveness            | 1           | ~5 tok/s generation on this dev machine; felt slow (~20s for ~95 tokens). Target-hardware numbers still needed. |
| First-token latency               | 1           | Prompt eval ~24-28 tok/s; first token came after full prompt eval (~1.5-2s here). |
| Memory behavior                   | 2           | llama.cpp projected ~5410 MiB host memory for this model; fits the 8 GB target with headroom. |
| Practical SME reasoning           | 0           | **No usable SME answer produced.** All generated tokens stayed inside `<think>`; the model never emitted the actual checklist/advice. |
| Checklist clarity                 | 0           | No checklist was emitted (truncated inside thinking). |
| Avoids reckless credit advice     | n/a         | No answer reached; cannot assess. |
| Avoids expand-without-records     | n/a         | No answer reached; cannot assess. |
| No false financial-software claim | 3           | Output made no accounting/banking/tax/payroll/ERP claim. |
| Handles uncertainty               | 2           | Inside `<think>` the model reasoned cautiously, but that reasoning never surfaced to the user. |
| Offline-constraint fit            | 3           | Fully local; no network call observed. |
| **Total**                         | **12/30** (5 categories n/a) | **Reject at this config.** |

Verdict: **reject at this run configuration** — not because the model is
unusable in principle, but because Qwen3's thinking mode consumed the entire
token budget and produced **zero user-visible SME answer**. Fix path: disable
thinking (`/no_think` suffix or a non-thinking variant) and/or raise the token
budget substantially, then re-score. Until then this candidate cannot serve
AfrekaOS's need for practical checklist-style responses.

## qwen3-4b-q4-k-m (secondary reasoning candidate)

No output — candidate GGUF **not present locally**. Not scored (per rubric:
score only if real outputs exist).

## granite-4.1-3b-q4-k-m (control baseline)

No output — candidate GGUF **not present locally**. Not scored.

## Aggregate / winner

- **Winner: unresolved.**
- Only one candidate was run (qwen3-1.7b), and it failed the practical-answer
  floor (scored 0 on practical SME reasoning and checklist clarity) because of
  the thinking-mode budget problem.
- The other two candidates have no local evidence.
- No `model.lock.json` is created. A winner is locked only after re-running
  with thinking disabled (or a higher budget) AND acquiring + running at least
  one alternative for comparison.
