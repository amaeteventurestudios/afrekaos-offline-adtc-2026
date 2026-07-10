# Target Hardware Benchmark — Runtime Notes

- **Model:** /Users/amaeteumanah/Desktop/Projects/afrekaos-offline-adtc-2026/model/afrekaos.gguf
- **Binary:** /usr/local/bin/llama-completion (llama-completion)
- **No-think:** True
- **Template:** True
- **Max tokens:** 200, timeout: 150s

| Prompt | rc | wall (s) | chars | gen tps | think trap | timed out |
|--------|----|----------|-------|---------|------------|-----------|
| prompt-1 | 0 | 63.52 | 5291 | 2.77 tokens per second | False | False |
| prompt-2 | 0 | 59.15 | 5472 | 2.63 tokens per second | False | False |
| smoke | 0 | 45.57 | 5134 | 2.86 tokens per second | False | False |

No fabricated numbers. All stats scraped from real llama.cpp output or measured by Python wall-clock.