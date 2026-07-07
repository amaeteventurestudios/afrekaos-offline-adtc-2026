"""Tests for app/model_inference.py.

Validates prompt construction and clean failure on missing model/binary.
Does not require actual model files, llama.cpp, or internet. Standard library
only.
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import model_inference, prompt_context  # noqa: E402


class TestBuildUngroundedPrompt(unittest.TestCase):
    def test_includes_role(self) -> None:
        p = model_inference.build_ungrounded_prompt("What should I check?")
        self.assertIn("AfrekaOS", p)
        self.assertIn("copilot", p.lower())

    def test_includes_question(self) -> None:
        q = "What should I check first?"
        p = model_inference.build_ungrounded_prompt(q)
        self.assertIn(q, p)

    def test_includes_answer_rules(self) -> None:
        p = model_inference.build_ungrounded_prompt("anything")
        self.assertIn("Answer rules", p)
        self.assertIn("checklist", p.lower())

    def test_forbids_financial_claims(self) -> None:
        p = model_inference.build_ungrounded_prompt("anything")
        for term in ("accounting", "banking", "payroll", "tax", "ERP"):
            self.assertIn(term.lower(), p.lower())

    def test_forbids_think_block(self) -> None:
        p = model_inference.build_ungrounded_prompt("anything")
        self.assertIn("<think>", p)

    def test_has_no_retrieved_context(self) -> None:
        # Ungrounded should NOT have the "Local SME operations context" block.
        p = model_inference.build_ungrounded_prompt("anything")
        self.assertNotIn("Local SME operations context", p)


class TestRunModelMissingHandling(unittest.TestCase):
    def setUp(self) -> None:
        self._old_model = os.environ.pop("AFREKAOS_MODEL_PATH", None)

    def tearDown(self) -> None:
        os.environ.pop("AFREKAOS_MODEL_PATH", None)
        if self._old_model is not None:
            os.environ["AFREKAOS_MODEL_PATH"] = self._old_model

    def test_missing_model_reports_cleanly(self) -> None:
        os.environ["AFREKAOS_MODEL_PATH"] = "/nonexistent/model_xyz.gguf"
        result = model_inference.run_model("test prompt")
        self.assertFalse(result["ok"])
        self.assertIsNotNone(result["error"])
        self.assertIn("not found", result["error"])

    def test_result_has_all_fields(self) -> None:
        os.environ["AFREKAOS_MODEL_PATH"] = "/nonexistent/model_xyz.gguf"
        result = model_inference.run_model("test prompt")
        for key in (
            "ok", "model_path", "llama_binary", "command_family",
            "output_path", "return_code", "timed_out",
            "stdout_chars", "stderr_chars", "visible_answer_chars",
            "contains_think", "error",
        ):
            self.assertIn(key, result)


class TestInferenceSummary(unittest.TestCase):
    def test_summary_shape(self) -> None:
        s = model_inference.inference_summary()
        for key in (
            "model_path", "model_exists", "llama_binary",
            "command_family", "qwen_template_present", "qwen_no_think_env",
        ):
            self.assertIn(key, s)

    def test_summary_does_not_raise(self) -> None:
        # Should never raise even with no model/binary.
        s = model_inference.inference_summary()
        self.assertIsInstance(s, dict)


class TestNoThinkSwitch(unittest.TestCase):
    def setUp(self) -> None:
        self._old = os.environ.pop("AFREKAOS_QWEN_NO_THINK", None)

    def tearDown(self) -> None:
        os.environ.pop("AFREKAOS_QWEN_NO_THINK", None)
        if self._old is not None:
            os.environ["AFREKAOS_QWEN_NO_THINK"] = self._old

    def test_no_think_appends_suffix(self) -> None:
        os.environ["AFREKAOS_QWEN_NO_THINK"] = "1"
        p = model_inference._maybe_no_think("base prompt")
        self.assertIn("/no_think", p)

    def test_no_env_no_suffix(self) -> None:
        p = model_inference._maybe_no_think("base prompt")
        self.assertNotIn("/no_think", p)


if __name__ == "__main__":
    unittest.main()
