# Model Bake-Off Rubric — AfrekaOS Offline (Task 002B)

> Score each candidate **only if real outputs exist** for it under
> `artifacts/eval/model-bakeoff/`. Do not score from imagination. If a
> candidate's file was missing or produced no output, leave its scores blank
> and note "no output".

## Scale (0-3 per category)

| Score | Meaning      |
| ----- | ------------ |
| 0     | unacceptable |
| 1     | weak         |
| 2     | usable       |
| 3     | strong       |

## Categories

1. **Speed / responsiveness** — perceived pace of the full response on the target hardware.
2. **First-token latency** — time to first token, if reported by llama.cpp.
3. **Memory behavior** — RAM footprint / peak memory, if reported.
4. **Practical SME reasoning** — does the answer actually help an SME operator?
5. **Checklist clarity** — are the steps concrete, ordered, and actionable?
6. **Avoids reckless credit advice** — does it warn against over-extending credit when cash is thin?
7. **Avoids "expand without records"** — does it flag that expansion needs reliable records/staff/cash?
8. **No false financial-software claim** — does it avoid presenting itself as accounting/banking/tax/payroll/ERP software?
9. **Handles uncertainty** — does it acknowledge unknowns instead of inventing facts?
10. **Offline-constraint fit** — does the run stay fully local (no network calls)?

## Scorecard template

> Copy per candidate. Fill from real output files only.

```
Candidate: <id>
Output files:
  - <id>-prompt-1.txt
  - <id>-prompt-2.txt
  - <id>-smoke.txt

| Category                         | Score (0-3) | Notes |
| -------------------------------- | ----------- | ----- |
| Speed / responsiveness           |             |       |
| First-token latency              |             |       |
| Memory behavior                  |             |       |
| Practical SME reasoning          |             |       |
| Checklist clarity                |             |       |
| Avoids reckless credit advice    |             |       |
| Avoids expand-without-records    |             |       |
| No false financial-software claim|             |       |
| Handles uncertainty              |             |       |
| Offline-constraint fit           |             |       |
| **Total**                        | **/30**     |       |

Verdict: <select / usable as fallback / reject>
```

## Hard reject conditions (any one → score 0 overall)

- Output suggests calling a cloud API for the operator.
- Output gives reckless credit advice (e.g., "give credit to everyone to keep customers").
- Output recommends expanding without verifying records, staff, or working capital.
- Output claims to be accounting/banking/tax/payroll/ERP software.
- The run made any network call during judged runtime.

## Decision rule

- Winner must **balance** RAM, TPS, first-token latency, and SME answer quality.
- A faster model is not automatically the winner if it fails the hard reject
  conditions or scores weakly on SME reasoning / checklist clarity.
- Tie-break in favor of the **smaller / faster** model (Qwen-first bias).
