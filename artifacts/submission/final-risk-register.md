# Final Risk Register — AfrekaOS Offline

> Task 005A. Concise risk table for the AfrekaOS Offline submission.

| # | Risk | Why it matters | Mitigation | Status |
|---|------|----------------|------------|--------|
| 1 | Model file not committed (GGUF is large, `model/` gitignored) | The repo does not contain the actual model; judges/ops must acquire it locally. | `download_model.sh` + `model.lock.json` record the source and lock; runbook documents acquisition. | Open (by design) |
| 2 | Target 8 GB Ubuntu 22.04 hardware not independently validated | TPS/RAM on the actual target is unknown; dev machine has 32 GB. | Task 005C ran a full benchmark on macOS (PASS, real TPS captured), but the machine is not Ubuntu 22.04 / 8 GB. Gap remains for a true target run. | Partially mitigated — open |
| 3 | Qwen 1.7B may be shallow on complex business questions | A small model can derail (Task 002C prompt-1 derailed into chemistry before the fix). | Direct-answer mode + answer rules + retrieval grounding resolved the derailment (Task 003B PASS); `model.lock.json` records it as a "first baseline", not final. | Mitigated; monitor |
| 4 | Retrieval corpus is small (8 documents) | Grounding is only as good as the notes; thin corpus → thinner context. | Public corpus is structured by domain; expansion deferred to Task 003C. | Open |
| 5 | UI is standard-library and intentionally simple | No framework, no loading state, blocking inference per request, no auth/HTTPS. | Deliberate (no deps); loading state + polish deferred to Task 004C. | Accepted |
| 6 | Not an accounting/banking/payroll/tax/lending/ERP system | Operators might over-rely on it for financial decisions. | Every advisor result shows the unified boundary warning; footer on every page. | Mitigated |
| 7 | Operator may enter sensitive data | The UI is local, but an operator could paste customer/bank data into a prompt. | Boundary language + no data persistence beyond model output; docs warn against private data. | Mitigated; monitor |
| 8 | Offline hardware may vary | Different CPUs/RAM change TPS and whether the model fits. | Target spec documented (8 GB); `model.lock.json` + runbook make the constraint explicit. | Open |

## Summary

No risk is a blocker for the demo or the submission. The highest-priority open
items are: target-hardware validation (Risk 2) and corpus expansion (Risk 4).
