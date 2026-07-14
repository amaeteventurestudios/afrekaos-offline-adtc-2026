"""Tests for app/prompt_context.py (grounded prompt builder).

Builds a temporary index, then validates the context block and grounded prompt.
Standard library only; no model/llama.cpp/internet required.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import prompt_context, retrieval  # noqa: E402


def _build_temp_index() -> str:
    tmp = tempfile.mkdtemp(prefix="afrekaos_promptctx_test_")
    sme = Path(tmp) / "sme_operations"
    sme.mkdir()
    (sme / "inventory.md").write_text(
        "# Inventory\n\nFast-moving items out of stock cost sales. Check reorder points.",
        encoding="utf-8",
    )
    (sme / "credit.md").write_text(
        "# Credit\n\nAvoid over-extending credit when cashflow is thin.",
        encoding="utf-8",
    )
    db_path = str(Path(tmp) / "test_fts.sqlite")
    retrieval.build_index(source_dirs=[str(sme)], db_path=db_path)
    return db_path


class TestPromptContext(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.db_path = _build_temp_index()

    def test_context_block_includes_snippets(self) -> None:
        block = prompt_context.build_context_block("credit cashflow", limit=5)
        self.assertIsInstance(block, str)
        # Should reference the retrieved note title or category.
        self.assertTrue(
            "credit" in block.lower() or "context" in block.lower(),
            f"context block missing content: {block!r}",
        )

    def test_context_block_missing_index_is_graceful(self) -> None:
        # Point retrieval at a nonexistent db by monkeypatching DEFAULT_DB_PATH.
        orig = retrieval.DEFAULT_DB_PATH
        retrieval.DEFAULT_DB_PATH = "/tmp/afrekaos_nonexistent_promptctx.sqlite"
        try:
            block = prompt_context.build_context_block("anything")
            self.assertIn("[no local context]", block)
        finally:
            retrieval.DEFAULT_DB_PATH = orig

    def test_grounded_prompt_has_role(self) -> None:
        prompt = prompt_context.build_grounded_prompt("What should I check first?")
        self.assertIn("AfrekaOS", prompt)
        self.assertIn("copilot", prompt.lower())

    def test_grounded_prompt_has_context(self) -> None:
        # Use the temp index by temporarily overriding DEFAULT_DB_PATH.
        orig = retrieval.DEFAULT_DB_PATH
        retrieval.DEFAULT_DB_PATH = self.db_path
        try:
            prompt = prompt_context.build_grounded_prompt("credit cashflow")
            self.assertIn("Local SME operations context", prompt)
        finally:
            retrieval.DEFAULT_DB_PATH = orig

    def test_grounded_prompt_has_question(self) -> None:
        q = "What should I check first?"
        prompt = prompt_context.build_grounded_prompt(q)
        self.assertIn(q, prompt)

    def test_grounded_prompt_has_answer_rules(self) -> None:
        prompt = prompt_context.build_grounded_prompt("anything")
        self.assertIn("Answer rules", prompt)
        self.assertIn("checklist", prompt.lower())

    def test_grounded_prompt_forbids_financial_claims(self) -> None:
        prompt = prompt_context.build_grounded_prompt("anything")
        for term in ("accounting", "banking", "payroll", "tax", "ERP"):
            self.assertIn(term.lower(), prompt.lower(), f"missing rule term: {term}")

    def test_grounded_prompt_forbids_cot(self) -> None:
        prompt = prompt_context.build_grounded_prompt("anything")
        self.assertIn("chain-of-thought", prompt.lower())
        self.assertIn("<think>", prompt)


class TestGroundedPromptLanguage(unittest.TestCase):
    def test_default_language_is_english(self) -> None:
        prompt = prompt_context.build_grounded_prompt("anything")
        self.assertIn("Response language: English", prompt)

    def test_french_prompt_has_french_label_and_instruction(self) -> None:
        prompt = prompt_context.build_grounded_prompt("anything", language="fr")
        self.assertIn("Response language: French", prompt)
        self.assertIn("French", prompt)

    def test_pidgin_prompt_has_pidgin_instruction(self) -> None:
        prompt = prompt_context.build_grounded_prompt("anything", language="pcm")
        self.assertIn("Response language: Nigerian Pidgin", prompt)
        self.assertIn("Pidgin", prompt)

    def test_unknown_language_falls_back_to_english(self) -> None:
        prompt = prompt_context.build_grounded_prompt("anything", language="zz")
        self.assertIn("Response language: English", prompt)

    def test_prompt_has_no_cloud_translation(self) -> None:
        for code in ("en", "yo", "ha", "sw", "pcm", "fr"):
            prompt = prompt_context.build_grounded_prompt("anything", language=code)
            self.assertIn("cloud translation", prompt.lower())

    def test_prompt_has_delimiter(self) -> None:
        for code in ("en", "yo", "ha", "sw", "pcm", "fr"):
            prompt = prompt_context.build_grounded_prompt("anything", language=code)
            self.assertIn(prompt_context.FINAL_GUIDANCE_DELIMITER, prompt)


if __name__ == "__main__":
    unittest.main()
