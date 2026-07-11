# Target Hardware Benchmark — Runtime Notes

- **Model:** /Users/amaeteumanah/Desktop/Projects/afrekaos-offline-adtc-2026/model/afrekaos.gguf
- **Binary:** /usr/local/bin/llama-completion (llama-completion)
- **No-think:** True
- **Template:** True
- **Max tokens:** 256, timeout: 180s

| Prompt | rc | wall (s) | chars | gen tps | think trap | timed out |
|--------|----|----------|-------|---------|------------|-----------|
| prompt-1 | 0 | 69.43 | 5331 | 2.37 tokens per second | False | False |
| prompt-2 | 0 | 52.48 | 5669 | 3.83 tokens per second | False | False |
| smoke | 0 | 43.02 | 5203 | 3.33 tokens per second | False | False |

No fabricated numbers. All stats scraped from real llama.cpp output or measured by Python wall-clock.