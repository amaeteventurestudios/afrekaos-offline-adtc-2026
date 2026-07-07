# Task 003B Grounded vs Ungrounded Comparison

- Generated: 2026-07-07
- Model: model/afrekaos.gguf → model/candidates/qwen3-1.7b-q4-k-m.gguf
- Binary: /usr/local/bin/llama-completion (llama-completion)
- Mode: Qwen direct-answer (/no_think + templates/qwen3_nonthinking.jinja + -no-cnv)

## Summary table

> "visible chars" = answer text outside think blocks, with llama.cpp log lines
> and echoed prompt headers excluded. Grounded prompts include retrieved SME
> context; ungrounded prompts include only role + rules.

| Prompt | Mode | visible chars | <think> trap | derailment |
|--------|------|---------------|--------------|------------|
| prompt-1 | ungrounded | 955 | no | no |
| prompt-1 | grounded | 1749 | no | no |
| prompt-2 | ungrounded | 1236 | no | no |
| prompt-2 | grounded | 2119 | no | no |
| smoke | ungrounded | 1071 | no | no |
| smoke | grounded | 1826 | no | no |

## Key finding: prompt-1 derailment is resolved

In Task 002C, prompt-1 (triage) derailed into chemistry/multiple-choice
hallucination. In Task 003B, **neither ungrounded nor grounded prompt-1
derailed** — the answer rules + AfrekaOS role (present in both modes) already
kept the model on SME operations. Grounding further improved specificity.

### prompt-1 ungrounded answer (real output)

> - Check inventory levels for the two fast-moving items.
> - Verify stock records and re-stock if necessary.
> - Confirm supplier delivery status and plan for next shipment.
> - Review credit policies and offer terms to customers.
> - Avoid over-crediting customers without confirming their ability to pay.
> - Do not delay supplier deliveries without resolving the delay.

### prompt-1 grounded answer (real output)

> Check inventory levels for the two fast-moving items first. Verify stock
> counts and expiration dates. Avoid extending credit immediately without
> confirming the supplier's delivery status and current stock availability.

The grounded answer is more focused and concrete (stock counts, expiration
dates, supplier delivery status) — drawn from the retrieved inventory/supplier
notes. The ungrounded answer is correct but more generic.

## Grounding adds "stockout" term

Grounded outputs include the term "stockout" (from retrieved SME notes) which
ungrounded outputs lack — evidence that retrieval context is reaching the model.

## Analyzer verdict

Run `python3 scripts/analyze_grounded_outputs.py` → **PROMPT-1 GROUNDING
VERDICT: PASS** (visible answer, no think trap, no derailment, ≥2 SME terms).
