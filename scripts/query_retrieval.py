#!/usr/bin/env python3
"""Query the AfrekaOS SQLite FTS5 retrieval index.

Usage:
  python3 scripts/query_retrieval.py "<query>"
  python3 scripts/query_retrieval.py        # runs three default AfrekaOS queries

If the index is missing, tells the user to run:
  python3 scripts/build_retrieval_index.py
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import retrieval  # noqa: E402

DEFAULT_QUERIES = [
    "low sales stockout supplier delay customer credit",
    "expand to second location irregular cash records trusted staff seasonal demand",
    "daily operating checklist small shop inventory cashflow customers supplier",
]


def print_results(query: str, results: list[dict]) -> None:
    print(f"\nQuery: {query}")
    print("-" * 60)
    if not results:
        print("  (no results)")
        return
    for i, r in enumerate(results, 1):
        print(f"  {i}. [{r['category']}] {r['title']}")
        print(f"     path  : {r['path']}")
        print(f"     snippet: {r['snippet']}")


def main() -> int:
    args = sys.argv[1:]
    queries = [" ".join(args)] if args else DEFAULT_QUERIES

    for q in queries:
        try:
            results = retrieval.search(q, limit=5)
        except FileNotFoundError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            print(
                "Run: python3 scripts/build_retrieval_index.py",
                file=sys.stderr,
            )
            return 1
        except RuntimeError as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2
        print_results(q, results)
    return 0


if __name__ == "__main__":
    sys.exit(main())
