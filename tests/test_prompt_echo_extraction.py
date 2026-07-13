"""Tests for prompt-echo stripping and delimiter-based extraction (Task 004E).

Validates that the UI answer shows only final operating guidance, not the
echoed grounded prompt (role line, context, source paths, answer rules).
Standard library only. No real model inference.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import model_inference as mi  # noqa: E402
from app import prompt_context as pc  # noqa: E402


class TestStripPromptEcho(unittest.TestCase):
    def test_exact_prompt_prefix_stripped(self) -> None:
        prompt = "You are AfrekaOS.\nBEGIN FINAL OPERATING GUIDANCE\n- Do X.\n\n"
        text = prompt + "1. Restock items.\n2. Call supplier."
        cleaned, stripped = mi.strip_prompt_echo(text, prompt=prompt)
        self.assertTrue(stripped)
        self.assertIn("Restock items", cleaned)
        self.assertNotIn("You are AfrekaOS", cleaned)

    def test_delimiter_preferred(self) -> None:
        text = (
            "You are AfrekaOS...\n"
            "Local SME operations context...\n"
            "BEGIN FINAL OPERATING GUIDANCE\n"
            "- Answer only after this line.\n"
            "1. Restock items.\n2. Call supplier."
        )
        cleaned, stripped = mi.strip_prompt_echo(text)
        self.assertTrue(stripped)
        self.assertIn("Restock items", cleaned)
        self.assertNotIn("You are AfrekaOS", cleaned)
        self.assertNotIn("Local SME operations context", cleaned)

    def test_markers_stripped_without_delimiter(self) -> None:
        text = (
            "You are AfrekaOS, a copilot.\n"
            "Local SME operations context:\n"
            "source: data/sme_operations/inventory.md\n"
            "Answer rules:\n- Do X.\n"
            "1. Restock items.\n2. Call supplier."
        )
        cleaned, stripped = mi.strip_prompt_echo(text)
        self.assertTrue(stripped)
        self.assertIn("Restock items", cleaned)
        self.assertNotIn("You are AfrekaOS", cleaned)
        self.assertNotIn("source:", cleaned)
        self.assertNotIn("Answer rules", cleaned)

    def test_no_echo_preserved(self) -> None:
        text = "1. Restock items.\n2. Call supplier."
        cleaned, stripped = mi.strip_prompt_echo(text)
        self.assertFalse(stripped)
        self.assertIn("Restock items", cleaned)

    def test_sme_terms_not_stripped(self) -> None:
        text = (
            "Check inventory levels and supplier stockout. Hold credit and "
            "review cash records before expanding."
        )
        cleaned, stripped = mi.strip_prompt_echo(text)
        self.assertFalse(stripped)
        self.assertIn("inventory", cleaned)
        self.assertIn("supplier", cleaned)
        self.assertIn("credit", cleaned)


class TestExtractVisibleAnswerEcho(unittest.TestCase):
    def test_full_echo_returns_only_answer(self) -> None:
        prompt = pc.build_grounded_prompt("low sales stockouts checklist")
        answer = "1. Restock fast-moving items.\n2. Contact supplier."
        r = mi.extract_visible_answer(prompt + answer, prompt=prompt)
        self.assertTrue(r["prompt_echo_detected"])
        self.assertTrue(r["prompt_echo_stripped"])
        self.assertNotIn("You are AfrekaOS", r["clean_answer"])
        self.assertNotIn("Local SME operations context", r["clean_answer"])
        self.assertNotIn("source:", r["clean_answer"])
        self.assertNotIn("Answer rules", r["clean_answer"])
        self.assertIn("Restock fast-moving items", r["clean_answer"])

    def test_delimiter_extraction(self) -> None:
        text = (
            "<think>\n\n</think>\n"
            "You are AfrekaOS...\n"
            "BEGIN FINAL OPERATING GUIDANCE\n"
            "- Answer only after this line.\n"
            "- Give only the final checklist.\n"
            "1. Restock items.\n2. Call supplier."
        )
        r = mi.extract_visible_answer(text)
        self.assertTrue(r["prompt_echo_stripped"])
        self.assertIn("Restock items", r["clean_answer"])
        self.assertNotIn("You are AfrekaOS", r["clean_answer"])

    def test_no_echo_preserved(self) -> None:
        r = mi.extract_visible_answer("1. Restock items.\n2. Call supplier.")
        self.assertFalse(r["prompt_echo_detected"])
        self.assertIn("Restock items", r["clean_answer"])

    def test_returns_echo_fields(self) -> None:
        r = mi.extract_visible_answer("answer")
        self.assertIn("prompt_echo_detected", r)
        self.assertIn("prompt_echo_stripped", r)


class TestPromptBuilderDelimiter(unittest.TestCase):
    def test_grounded_prompt_has_delimiter(self) -> None:
        prompt = pc.build_grounded_prompt("a question")
        self.assertIn(pc.FINAL_GUIDANCE_DELIMITER, prompt)

    def test_grounded_prompt_has_no_repeat_instructions(self) -> None:
        prompt = pc.build_grounded_prompt("a question")
        self.assertIn("Do not repeat the local context", prompt)
        self.assertIn("Do not repeat the source list", prompt)
        self.assertIn("Do not repeat the answer rules", prompt)

    def test_ungrounded_prompt_has_delimiter(self) -> None:
        prompt = mi.build_ungrounded_prompt("a question")
        self.assertIn(pc.FINAL_GUIDANCE_DELIMITER, prompt)
        self.assertIn("Do not repeat these instructions", prompt)


if __name__ == "__main__":
    unittest.main()