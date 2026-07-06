#!/usr/bin/env python3
"""Build the AfrekaOS SQLite FTS5 retrieval index from local markdown notes.

Indexes only public SME operations notes. Never indexes model files, artifacts,
.git, or private/hidden files. Standard library only.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import retrieval  # noqa: E402


def main() -> int:
    try:
        summary = retrieval.build_index()
    except RuntimeError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print("AfrekaOS retrieval index built")
    print("-" * 40)
    print(f"database path    : {summary['db_path']}")
    print(f"documents indexed : {summary['documents']}")
    print(f"FTS5 available    : {summary['fts5']}")
    print("source directories:")
    for d in summary["source_dirs"]:
        print(f"  - {d}")

    # Print category breakdown.
    cat_summary = retrieval.retrieval_summary()
    print("documents by category:")
    for cat, n in cat_summary["categories"].items():
        print(f"  - {cat}: {n}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
