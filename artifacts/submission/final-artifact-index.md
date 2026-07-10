# Final Artifact Index — AfrekaOS Offline

> Task 005A. The most important evidence files and what each proves.

## Model and lock

| File | What it proves |
|------|---------------|
| `model.candidates.json` | The Qwen-first bake-off candidate set: qwen3-1.7b (primary), qwen3-4b (secondary), granite-4.1-3b (control). Records roles, repos, quantization, local paths, and prohibited-use boundaries. |
| `model.lock.json` | `qwen3-1.7b-q4-k-m` is locked as the first canonical baseline. Records mode (non-thinking/direct-answer), evidence artifacts, unresolved items, and prohibited-use boundaries. |

## Eval evidence (by task)

| File | What it proves |
|------|---------------|
| `artifacts/eval/task-002B-model-bakeoff.md` | The model bake-off ran: qwen3-1.7b was acquired and profiled; the other two candidates were absent. Two runtime bugs (conversation-mode runaway, stdin-stealing) were found and fixed. Winner was unresolved until 002C. |
| `artifacts/eval/task-002C-qwen-direct-mode.md` | Direct-answer mode fixes the thinking trap: no `<think>` in any retest output; analyzer PASS. qwen3-1.7b locked as the first canonical model. |
| `artifacts/eval/task-003A-retrieval.md` | SQLite FTS5 retrieval layer over 8 public SME notes; relevance verified on 3 default queries; grounded prompt builder works. |
| `artifacts/eval/task-003B-grounded-inference.md` | Grounded vs ungrounded comparison (6 real runs). The Task 002C prompt-1 derailment is fully resolved. Analyzer verdict: PASS. |
| `artifacts/eval/task-004A-local-web-ui.md` | Standard-library local browser UI; all routes return 200; `/health` returns JSON; manual real-inference POST verified. |
| `artifacts/eval/task-004B-ui-polish.md` | UI polished with offline banner, nav, demo cards; `/demo` route with 4 scenarios; evidence capture script; HTML/JSON snapshots captured. |

## UI evidence snapshots

| Path | What it proves |
|------|---------------|
| `artifacts/eval/task-004B-ui-evidence/home.html` | Mission Control renders with banner + cards. |
| `artifacts/eval/task-004B-ui-evidence/demo.html` | Demo Scenarios page renders with all 4 scenario titles. |
| `artifacts/eval/task-004B-ui-evidence/advisor-daily.html` | Daily Operations Advisor form renders. |
| `artifacts/eval/task-004B-ui-evidence/advisor-inventory.html` | Inventory and Stock Check form renders. |
| `artifacts/eval/task-004B-ui-evidence/advisor-cashflow.html` | Cashflow Pressure Coach form renders. |
| `artifacts/eval/task-004B-ui-evidence/status.html` | Offline System Status renders with model/retrieval/FTS status. |
| `artifacts/eval/task-004B-ui-evidence/health.json` | `/health` returns valid JSON. |

## Submission artifacts

| File | What it proves |
|------|---------------|
| `artifacts/submission/final-validation-log.md` | Full validation run (all checks + unittest); overall PASS/FAIL. |
| `artifacts/submission/final-evaluation-package.md` | Product, runtime, retrieval, UI, evidence, limitations, boundaries. |
| `artifacts/submission/final-demo-script.md` | 2–3 minute demo script. |
| `artifacts/submission/final-runbook.md` | Clone → validate → run instructions. |
| `artifacts/submission/final-risk-register.md` | Risk table with mitigations and statuses. |
| `artifacts/submission/final-artifact-index.md` | This index. |

## Target hardware retest (Task 005C)

| File | What it proves |
|------|---------------|
| `artifacts/submission/target-hardware-profile.md` | Live machine profile: OS, CPU, memory, model, retrieval, FTS5. |
| `artifacts/submission/target-hardware-benchmark/` | Real grounded inference outputs + timing (3 prompts). |
| `artifacts/submission/target-hardware-benchmark-analysis.md` | Analyzer verdict: PASS (no traps, no derailment, SME terms present). |
| `artifacts/submission/task-005C-target-hardware-retest.md` | Full retest report with honest hardware-gap documentation. |
