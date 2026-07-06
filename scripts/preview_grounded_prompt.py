#!/usr/bin/env python3
"""Preview a grounded AfrekaOS prompt (retrieval context + question + rules).

Usage:
  python3 scripts/preview_grounded_prompt.py "<user question>"
  python3 scripts/preview_grounded_prompt.py    # uses metadata prompt 1

This does NOT call the model. It only shows the prompt that would be sent.
If the retrieval index is missing, it builds it first.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import prompt_context, retrieval  # noqa: E402


def main() -> int:
    args = sys.argv[1:]
    if args:
        question = " ".join(args)
    else:
        meta = json.loads((REPO_ROOT / "metadata.json").read_text(encoding="utf-8"))
        question = meta["test_prompts"][0]["prompt"]

    # Ensure the index exists; build it if missing.
    db = REPO_ROOT / retrieval.DEFAULT_DB_PATH
    if not db.is_file():
        print("[index missing] building retrieval index first...")
        try:
            summary = retrieval.build_index()
            print(
                f"[index built] {summary['documents']} documents at "
                f"{summary['db_path']}"
            )
        except (RuntimeError, ValueError) as exc:
            print(f"ERROR: could not build index: {exc}", file=sys.stderr)
            return 2

    preview = prompt_context.build_grounded_prompt(question, limit=5)
    print("=" * 72)
    print("GROUNDED PROMPT PREVIEW (not a model answer)")
    print("=" * 72)
    print(preview)
    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main())
