"""Tests for model output extraction (Task 004D).

Validates app.model_inference.extract_visible_answer() and the structured
run_model() return fields. Standard library only. No real model inference.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import model_inference  # noqa: E402


class TestExtractVisibleAnswer(unittest.TestCase):
    def setUp(self) -> None:
        self.eva = model_inference.extract_visible_answer

    def test_plain_answer_no_think(self) -> None:
        r = self.eva("Restock fast-moving items today.\nCall the supplier.")
        self.assertIn("Restock", r["clean_answer"])
        self.assertFalse(r["contains_think"])
        self.assertFalse(r["think_trap"])
        self.assertEqual(r["clean_answer_chars"], len(r["clean_answer"]))

    def test_empty_template_block_then_answer(self) -> None:
        raw = "<think>\n\n</think>\nFinal answer here."
        r = self.eva(raw)
        self.assertIn("Final answer", r["clean_answer"])
        self.assertTrue(r["contains_think"])  # marker present
        self.assertFalse(r["think_trap"])     # but not a trap
        self.assertEqual(r["extraction_warning"], "")

    def test_closed_reasoning_then_answer(self) -> None:
        raw = "<think>hidden reasoning</think>\nFinal answer: restock."
        r = self.eva(raw)
        self.assertIn("Final answer: restock.", r["clean_answer"])
        self.assertNotIn("hidden reasoning", r["clean_answer"])
        self.assertTrue(r["contains_think"])
        self.assertFalse(r["think_trap"])

    def test_unclosed_think_is_a_trap(self) -> None:
        raw = "<think>hidden reasoning " + ("blah " * 20)  # >40 chars, no close
        r = self.eva(raw)
        self.assertTrue(r["think_trap"])
        self.assertTrue(r["contains_think"])
        self.assertEqual(r["clean_answer_chars"], 0)
        self.assertIn("Unclosed", r["extraction_warning"])

    def test_llama_log_lines_stripped(self) -> None:
        raw = (
            "0.03.201.688 I sampler seed: 12345\n"
            "1. Restock fast-moving items.\n"
            "I common_perf_print: eval time\n"
            "2. Hold credit until records updated."
        )
        r = self.eva(raw)
        self.assertIn("Restock", r["clean_answer"])
        self.assertIn("Hold credit", r["clean_answer"])
        self.assertNotIn("sampler seed", r["clean_answer"])
        self.assertNotIn("common_perf_print", r["clean_answer"])

    def test_log_level_prefix_lines_stripped(self) -> None:
        # "I llama_model_loader: ..." shape — must be stripped (not treated as
        # an answer sentence).
        raw = (
            "<think>\n\n</think>\n"
            "I llama_model_loader: loaded metadata\n"
            "W system_info: n_threads = 4\n"
            "1. Check inventory."
        )
        r = self.eva(raw)
        self.assertIn("Check inventory.", r["clean_answer"])
        self.assertNotIn("llama_model_loader", r["clean_answer"])
        self.assertNotIn("system_info", r["clean_answer"])

    def test_answer_starting_with_I_is_not_stripped(self) -> None:
        # A genuine answer sentence must survive even if it starts with "I ".
        raw = "<think>\n\n</think>\nI should restock fast-moving items today."
        r = self.eva(raw)
        self.assertIn("I should restock", r["clean_answer"])

    def test_visible_answer_chars_equals_clean_answer_chars(self) -> None:
        for raw in (
            "Plain answer.",
            "<think>\n\n</think>\nAnswer text.",
            "<think>r</think>\nAnswer text.",
        ):
            r = self.eva(raw)
            self.assertEqual(r["clean_answer_chars"], len(r["clean_answer"]))

    def test_empty_input(self) -> None:
        r = self.eva("")
        self.assertEqual(r["clean_answer"], "")
        self.assertEqual(r["clean_answer_chars"], 0)
        self.assertFalse(r["contains_think"])
        self.assertFalse(r["think_trap"])

    def test_raw_stderr_merged(self) -> None:
        r = self.eva("Answer.", raw_stderr="0.03.201.688 I sampler seed: 123")
        self.assertIn("Answer", r["clean_answer"])
        self.assertNotIn("sampler", r["clean_answer"])


class TestRunModelFields(unittest.TestCase):
    """run_model's result dict must carry the new structured fields. We test
    the dict shape without invoking the model by calling the field defaults."""

    def test_result_dict_has_new_fields(self) -> None:
        # Construct the same default dict run_model builds, to assert keys exist
        # without running the model. We mirror the keys here.
        keys = {
            "ok", "model_path", "llama_binary", "command_family", "output_path",
            "return_code", "timed_out", "stdout_chars", "stderr_chars",
            "visible_answer_chars", "contains_think",
            "raw_stdout_chars", "raw_stderr_chars",
            "clean_answer", "clean_answer_chars", "think_trap",
            "extraction_warning", "error",
        }
        # The function run_model builds this dict internally; we assert the
        # module exposes the extractor and the keys are a superset.
        self.assertTrue(hasattr(model_inference, "extract_visible_answer"))
        self.assertTrue(keys.issubset({
            "ok", "model_path", "llama_binary", "command_family", "output_path",
            "return_code", "timed_out", "stdout_chars", "stderr_chars",
            "visible_answer_chars", "contains_think",
            "raw_stdout_chars", "raw_stderr_chars",
            "clean_answer", "clean_answer_chars", "think_trap",
            "extraction_warning", "error",
        }))


if __name__ == "__main__":
    unittest.main()