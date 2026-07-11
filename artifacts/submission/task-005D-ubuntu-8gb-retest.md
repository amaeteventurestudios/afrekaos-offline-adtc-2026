# Task 005D — Ubuntu 22.04 / 8 GB Target Retest (Evidence)

> AfrekaOS Offline. This task's goal was to run and document the true
> Ubuntu 22.04 / 8 GB target retest. This document records what actually
> happened: the run did **not** execute on Ubuntu. No numbers are fabricated.

## Headline

**This run was NOT executed on Ubuntu 22.04.** The only machine available for
this retest is the same macOS workstation used for Task 005C:

- **OS:** macOS 12.7.6 (Darwin 21.6.0, x86_64)
- **Total memory:** 32.00 GiB — **4× the 8 GB target**

Per the task's own contingency rules, because this was not run on Ubuntu, the
target-hardware risk remains **"Partially mitigated — open."** The numbers below
are real and freshly captured, but they are a dev-machine re-run, not a true
target-hardware run.

## Why this is documented as a non-target run

There is no Ubuntu 22.04 / 8 GB VM or host reachable from this environment. I
will not claim an Ubuntu result I did not obtain. What I can do — and did — is
re-run the entire validation + benchmark + UI pipeline on the available machine
and record the results honestly, so the submission carries a current, complete,
non-fabricated evidence set.

## Step 1 — Environment confirmation

Command: `python3 scripts/target_hardware_profile.py`

| Property | Value | Target |
|----------|-------|--------|
| OS | `macOS-12.7.6-x86_64-i386-64bit` | Ubuntu 22.04 |
| Ubuntu 22.04 detected | **False** | True |
| Python | 3.9.6 | — |
| CPU | Intel Core i7-6700K @ 4.00GHz | low-cost CPU |
| Physical cores | 4 | — |
| Logical cores | 8 | — |
| **Total memory** | **32.00 GiB (34,359,738,368 bytes)** | **~8 GB** |
| Available memory | 1.63 GiB (1,748,873,216 bytes) | — |
| Disk free (repo) | 14.39 GiB | — |

- **Was this run on Ubuntu 22.04?** **No.** macOS 12.7.6.
- **Total memory detected:** **32.00 GiB.**
- **Is the memory close to 8 GB?** **No.** It is 4× the target. A true 8 GB
  run remains the only way to close the memory-pressure risk.

Full profile: `artifacts/submission/target-hardware-profile.md`

## Step 2 — Model exists locally

- `model/afrekaos.gguf`: **exists** (relative symlink to
  `model/candidates/qwen3-1.7b-q4-k-m.gguf`).
- Model size: **1.19 GiB** (1,282,439,584 bytes).
- `llama-completion` binary detected at `/usr/local/bin/llama-completion`.
- Locked model: `qwen3-1.7b-q4-k-m` (per `model.lock.json`).
- The GGUF is gitignored and was **not** committed.

## Step 3 — Retrieval index built

Command: `python3 scripts/build_retrieval_index.py`

- Index exists: **yes** (`data/afrekaos_fts.sqlite`).
- Documents indexed: **8** (6 sme_operations + 1 language + 1 sources).
- SQLite FTS5: **available**.

## Step 4 — Final validation

Command: `python3 scripts/final_validation.py`

- **Overall: PASS.**
- All 9 checks passed: check_metadata, check_model_candidates,
  build_retrieval_index, query_retrieval, preview_grounded_prompt,
  analyze_grounded_outputs, smoke_web, capture_ui_evidence, unittest discover.
- Log: `artifacts/submission/final-validation-log.md`.

## Step 5 — Target inference benchmark

Command: `AFREKAOS_QWEN_NO_THINK=1 python3 scripts/target_inference_benchmark.py`

**Benchmark verdict: PASS** (3/3 grounded runs completed, no timeouts, no traps).
Bounded to 256 tokens, 180s timeout each. Real generation TPS and wall-clock
scraped from llama.cpp output; not estimated, not invented.

| Prompt | rc | wall-clock (s) | output chars | generation tps | prompt-eval tps | think trap | timed out |
|--------|----|----------------|--------------|----------------|-----------------|------------|-----------|
| prompt-1 grounded | 0 | 69.43 | 5331 | 2.37 | 25.18 | no | no |
| prompt-2 grounded | 0 | 52.48 | 5669 | 3.83 | 40.69 | no | no |
| smoke grounded | 0 | 43.02 | 5203 | 3.33 | 40.80 | no | no |

**Memory projection (scraped from llama.cpp log, identical across runs):**
llama.cpp projected to use **5410 MiB of host memory vs. 32768 MiB total**.
This is the model's projected footprint (~5.3 GB), which is *under* the 8 GB
target but leaves a modest margin on a true 8 GB host. It is a useful signal,
not a substitute for an actual 8 GB measurement.

**Did outputs contain think traps?** **No.** `think_trap=False` for all three.

**Analyzer command:** `python3 scripts/analyze_target_benchmark.py`

**Analyzer verdict: PASS.** Per-output:
- **prompt-1:** think trap False, 2634 visible chars, no derailment, no forbidden
  claims, 8/8 SME terms.
- **prompt-2:** think trap False, 2972 visible chars, no derailment, no forbidden
  claims, 8/8 SME terms.
- **smoke:** think trap False, 2506 visible chars, no derailment, no forbidden
  claims, 8/8 SME terms.

Analysis: `artifacts/submission/target-hardware-benchmark-analysis.md`

## Step 6 — Local web smoke test + UI evidence

- `python3 scripts/smoke_web.py` → **SMOKE TEST PASSED** (`/`, `/status`,
  `/health` all 200; `/health` valid JSON).
- `python3 scripts/capture_ui_evidence.py` → **EVIDENCE CAPTURE PASSED**
  (7 files: home, demo, advisor-daily, advisor-inventory, advisor-cashflow,
  status, health.json). Inference was skipped (optional path not enabled).

## Limitations

1. **Not Ubuntu 22.04.** This is the single most important limitation. The
   target-hardware risk (Risk 2) is **not closed** by this run. A true
   Ubuntu 22.04 run — on an actual Ubuntu host, ideally in an 8 GB VM — is
   still required.
2. **32 GB RAM, not 8 GB.** Memory-pressure behavior on an 8 GB host is
   untested here. The llama.cpp projection (~5.3 GB host memory) suggests the
   model should fit within 8 GB, but projection ≠ measured free RAM at runtime.
3. **Single run per prompt.** Not a statistically robust benchmark; TPS varies
   run-to-run (2.37–3.83 tok/s across these three runs).
4. **Grounded prompts include retrieved context**, so wall-clock is longer than
   ungrounded inference would be.
5. **Same physical machine as Task 005C.** This is a fresh re-run with current
   numbers, not a new platform. It does not advance the target-hardware
   question beyond 005C; it refreshes the evidence and records that the Ubuntu
   target was attempted but not achievable from this environment.

## No fabricated numbers

Every number in this document is either scraped from real llama.cpp output or
measured by Python wall-clock on the run documented above. No value was
estimated, projected as if measured, or invented. The OS is reported as macOS
because that is what `platform.platform()` returned; it is not relabeled as
Ubuntu.

## Risk register update (result of this run)

Because this was **not** run on Ubuntu, Risk 2 remains:

> **"Partially mitigated — open."**

It will move to "Mitigated with Ubuntu 22.04 / 8 GB retest evidence" only after
a genuine Ubuntu 22.04 run (ideally ≤ 8 GB) passes the same pipeline.

## Runtime artifact paths

- `artifacts/submission/target-hardware-profile.md`
- `artifacts/submission/target-hardware-benchmark/prompt-1-grounded.txt`
- `artifacts/submission/target-hardware-benchmark/prompt-2-grounded.txt`
- `artifacts/submission/target-hardware-benchmark/smoke-grounded.txt`
- `artifacts/submission/target-hardware-benchmark/runtime-notes.md`
- `artifacts/submission/target-hardware-benchmark/benchmark-summary.md`
- `artifacts/submission/target-hardware-benchmark-analysis.md`
- `artifacts/submission/task-005D-ubuntu-8gb-retest.md` (this file)
