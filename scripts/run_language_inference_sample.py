#!/usr/bin/env python3
"""Optional live inference sample for a selected language (Task 006A).

Runs ONE bounded grounded inference prompt in the selected language and saves
the raw output. Only run this manually when the model and llama runtime are
available. Fails gracefully if they are not.

Usage:
    AFREKAOS_QWEN_NO_THINK=1 python3 scripts/run_language_inference_sample.py [code]

Defaults to French (fr) if no code is supplied. Supported: en, yo, ha, sw, pcm, fr.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import language_mode as lm  # noqa: E402
from app import model_inference, retrieval  # noqa: E402

OUT_DIR = REPO_ROOT / "artifacts" / "eval" / "task-006A-language-mode"
DEFAULT_QUESTION = (
    "A small shop has lower sales than usual, two fast-moving items are out of "
    "stock, the supplier delivery is delayed, and more customers are asking for "
    "credit. Give a short operating checklist."
)


def main() -> int:
    code = sys.argv[1] if len(sys.argv) > 1 else "fr"
    lang_code = lm.normalize_language_code(code)
    lang_label = lm.get_language_label(lang_code)
    print(f"Language: {lang_code} ({lang_label})")

    # Ensure retrieval index.
    db = REPO_ROOT / "data" / "afrekaos_fts.sqlite"
    if not db.is_file():
        print("[index missing] building...")
        retrieval.build_index()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUT_DIR / f"live-{lang_code}.txt"

    print("Running one bounded grounded inference prompt...")
    result = model_inference.run_grounded(
        DEFAULT_QUESTION,
        output_path=str(out_path),
        max_tokens=256,
        timeout_seconds=180,
        language=lang_code,
    )

    if not result["ok"]:
        print(f"[failed] {result.get('error', 'unknown error')}")
        out_path.write_text(
            f"[live inference failed] {result.get('error', '')}\n",
            encoding="utf-8",
        )
        return 1

    print(f"[ok] return_code={result.get('return_code')}")
    print(f"[ok] clean_answer_chars={result.get('clean_answer_chars', 0)}")
    print(f"[ok] language={result.get('language_code')}/{result.get('language_label')}")
    print(f"[ok] output saved to {out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
