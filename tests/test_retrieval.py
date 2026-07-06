"""Tests for app/retrieval.py (SQLite FTS5 layer).

Builds a temporary index from small temporary markdown files. Standard library
only; does not require model files, llama.cpp, or internet.
"""

from __future__ import annotations

import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import retrieval  # noqa: E402


def _make_temp_corpus() -> tuple[Path, str]:
    """Create a temp dir of markdown notes; return (dir, db_path)."""
    tmp = tempfile.mkdtemp(prefix="afrekaos_retrieval_test_")
    sme = Path(tmp) / "sme_operations"
    lang = Path(tmp) / "language"
    sme.mkdir()
    lang.mkdir()
    (sme / "inventory.md").write_text(
        "# Inventory\n\nFast-moving items out of stock cost sales. Check reorder points and lead times.",
        encoding="utf-8",
    )
    (sme / "credit.md").write_text(
        "# Credit\n\nCustomer credit ties up cash. Avoid over-extending credit when cashflow is thin.",
        encoding="utf-8",
    )
    (sme / "expansion.md").write_text(
        "# Expansion readiness\n\nDo not expand to a second location without reliable cash records and a trusted second in command.",
        encoding="utf-8",
    )
    (lang / "yoruba_mode.md").write_text(
        "# Yoruba mode\n\nLanguage-mode placeholder for offline SME reasoning.",
        encoding="utf-8",
    )
    db_path = str(Path(tmp) / "test_fts.sqlite")
    return Path(tmp), db_path


class TestRetrievalBuild(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp, cls.db_path = _make_temp_corpus()
        cls.summary = retrieval.build_index(
            source_dirs=[
                str(cls.tmp / "sme_operations"),
                str(cls.tmp / "language"),
            ],
            db_path=cls.db_path,
        )

    def test_build_returns_summary(self) -> None:
        self.assertEqual(self.summary["documents"], 4)
        self.assertTrue(self.summary["fts5"])

    def test_db_file_exists(self) -> None:
        self.assertTrue(Path(self.db_path).is_file())

    def test_retrieval_summary(self) -> None:
        s = retrieval.retrieval_summary(db_path=self.db_path)
        self.assertEqual(s["documents"], 4)
        self.assertIn("sme_operations", s["categories"])
        self.assertEqual(s["categories"]["sme_operations"], 3)


class TestRetrievalSearch(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp, cls.db_path = _make_temp_corpus()
        retrieval.build_index(
            source_dirs=[str(cls.tmp / "sme_operations"), str(cls.tmp / "language")],
            db_path=cls.db_path,
        )

    def test_search_returns_results(self) -> None:
        results = retrieval.search("stock reorder", db_path=self.db_path)
        self.assertGreater(len(results), 0)
        self.assertEqual(results[0]["category"], "sme_operations")

    def test_search_result_shape(self) -> None:
        results = retrieval.search("credit cash", db_path=self.db_path)
        for r in results:
            self.assertIn("doc_id", r)
            self.assertIn("path", r)
            self.assertIn("title", r)
            self.assertIn("category", r)
            self.assertIn("snippet", r)

    def test_search_relevance_credit(self) -> None:
        results = retrieval.search("customer credit cashflow", db_path=self.db_path)
        self.assertGreater(len(results), 0)
        titles = [r["title"].lower() for r in results]
        self.assertTrue(any("credit" in t for t in titles))

    def test_search_relevance_expansion(self) -> None:
        results = retrieval.search(
            "expand second location cash records", db_path=self.db_path
        )
        titles = [r["title"].lower() for r in results]
        self.assertTrue(any("expansion" in t for t in titles))

    def test_search_limit(self) -> None:
        results = retrieval.search("sme", limit=2, db_path=self.db_path)
        self.assertLessEqual(len(results), 2)


class TestRetrievalGetDocument(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmp, cls.db_path = _make_temp_corpus()
        retrieval.build_index(
            source_dirs=[str(cls.tmp / "sme_operations"), str(cls.tmp / "language")],
            db_path=cls.db_path,
        )

    def test_get_document_found(self) -> None:
        # doc_id is the repo-relative path; in the temp corpus it is relative to
        # the source dir parent. Fetch via search first to get a real doc_id.
        results = retrieval.search("inventory", db_path=self.db_path)
        self.assertGreater(len(results), 0)
        doc = retrieval.get_document(results[0]["doc_id"], db_path=self.db_path)
        self.assertIsNotNone(doc)
        self.assertIn("body", doc)

    def test_get_document_missing_returns_none(self) -> None:
        doc = retrieval.get_document("does/not/exist.md", db_path=self.db_path)
        self.assertIsNone(doc)


class TestRetrievalMissingIndex(unittest.TestCase):
    def test_search_missing_index_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            retrieval.search("anything", db_path="/tmp/afrekaos_does_not_exist.sqlite")

    def test_summary_missing_index_raises(self) -> None:
        with self.assertRaises(FileNotFoundError):
            retrieval.retrieval_summary(db_path="/tmp/afrekaos_does_not_exist.sqlite")

    def test_build_no_documents_raises(self) -> None:
        empty = tempfile.mkdtemp(prefix="afrekaos_empty_")
        with self.assertRaises(ValueError):
            retrieval.build_index(
                source_dirs=[empty], db_path=str(Path(empty) / "x.sqlite")
            )


if __name__ == "__main__":
    unittest.main()
