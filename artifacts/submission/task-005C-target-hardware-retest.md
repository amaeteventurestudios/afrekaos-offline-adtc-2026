# Task 005C — Target Hardware Retest (Evidence)

> AfrekaOS Offline. Runs the target hardware retest package on the closest
> available environment, documenting real performance and quality.

## Why this retest exists

Task 005A flagged "dev-machine timing is not target hardware timing" as the
highest-priority open risk. This task runs the profiler + benchmark + analyzer
to capture real local numbers and document whether the current machine matches
the Ubuntu 22.04 / 8 GB RAM target.

## Hardware / OS profile

| Property | Value |
|----------|-------|
| OS | macOS 12.7.6 x86_64 |
| Python | 3.9.6 |
| Ubuntu 22.04 detected | **False** |
| CPU | Intel Core i7-6700K @ 4.00GHz (4 physical / 8 logical cores) |
| Total memory | 32.00 GiB |
| Available memory | ~4.24 GiB |
| Disk free (repo) | ~11.79 GiB |

Full profile: `artifacts/submission/target-hardware-profile.md`

## Whether the environment matches Ubuntu 22.04 / 8 GB RAM

**No.** The current machine is macOS 12.7.6 (Darwin x86_64) with 32 GB RAM —
not Ubuntu 22.04, and 4× the target RAM. This means:

- **Memory headroom is more favorable** than the 8 GB target. The model (1.19 GiB)
  fits easily. On an actual 8 GB machine, available memory would be tighter.
- **TPS may differ** on Ubuntu / different CPU. The i7-6700K is a desktop CPU;
  a low-cost Ubuntu laptop with integrated graphics may be slower or faster.
- **These numbers are real local measurements**, but they are **not** a substitute
  for a true Ubuntu 22.04 / 8 GB target run.

## Model path status

- `model/afrekaos.gguf`: **exists** (relative symlink to
  `model/candidates/qwen3-1.7b-q4-k-m.gguf`).
- Model size: 1.19 GiB (1,282,439,584 bytes).
- `llama-completion` binary detected at `/usr/local/bin/llama-completion`.

## Retrieval index status

- Index exists: **yes** (`data/afrekaos_fts.sqlite`).
- Documents: **8**.
- SQLite FTS5: **available**.

## Whether inference ran

**Yes — all 3 grounded inference runs completed** (prompt-1, prompt-2, smoke),
bounded to 200 tokens, 150s timeout each. No timeouts, no failures.

## Timing / TPS / memory (actually captured)

| Prompt | wall-clock (s) | generation tps | output chars | think trap |
|--------|----------------|----------------|--------------|------------|
| prompt-1 grounded | 63.5 | 2.77 | 5291 | no |
| prompt-2 grounded | 59.2 | 2.63 | 5472 | no |
| smoke grounded | 45.6 | 2.86 | 5134 | no |

> Generation TPS is lower than the Task 003B dev-machine runs (~3.4–4.1 tok/s).
> This is real variance — the machine was under more load during this run. The
> numbers are not fabricated; they are scraped from actual llama.cpp output +
> Python wall-clock.

## Output quality verdict

**Analyzer verdict: PASS.**

All 3 outputs:
- Contain visible answer text (2437–2775 chars outside think blocks)
- No think traps (no unclosed `<think>` with real content)
- No derailment terms (no chemistry/MCQ)
- No forbidden product claims (no accounting/banking/tax/payroll/ERP/lending)
- Contain all 8 SME terms (stockout, supplier, credit, cash, records, inventory, expansion, staff)

Full analysis: `artifacts/submission/target-hardware-benchmark-analysis.md`

## Limitations

- **Not Ubuntu 22.04.** This is macOS. A true target run on Ubuntu 22.04 is still
  needed for final validation.
- **32 GB RAM, not 8 GB.** Memory pressure behavior on an 8 GB machine is
  untested here.
- **Single run per prompt.** Not a statistically robust benchmark; variance is
  real (see TPS difference vs Task 003B).
- **Grounded prompts include retrieved context**, so prompt length (and thus
  wall-clock) is longer than ungrounded would be.

## Remaining risks

1. **Target hardware gap** — must re-run on an actual Ubuntu 22.04 / 8 GB
   machine to close the highest-priority risk.
2. **TPS variance** — the same machine produced different TPS across runs
   (Task 003B vs this task). Target-hardware TPS is unknown.
3. **Memory pressure** — untested at 8 GB (this machine has 32 GB).

## No fabricated numbers

All numbers above are scraped from real llama.cpp output or measured by Python
wall-clock. Nothing is estimated or invented.

## Runtime artifact paths

- `artifacts/submission/target-hardware-profile.md`
- `artifacts/submission/target-hardware-benchmark/prompt-1-grounded.txt`
- `artifacts/submission/target-hardware-benchmark/prompt-2-grounded.txt`
- `artifacts/submission/target-hardware-benchmark/smoke-grounded.txt`
- `artifacts/submission/target-hardware-benchmark/runtime-notes.md`
- `artifacts/submission/target-hardware-benchmark/benchmark-summary.md`
- `artifacts/submission/target-hardware-benchmark-analysis.md`
- `artifacts/submission/task-005C-target-hardware-retest.md` (this file)
