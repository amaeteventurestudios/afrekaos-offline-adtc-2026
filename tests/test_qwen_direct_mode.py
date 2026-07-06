"""Tests for Task 002C Qwen direct-answer mode.

Validates that the template, retest script, and analyzer exist, and that the
analyzer handles missing files without crashing. Also sanity-checks the
analyzer's think/answer logic on synthetic strings. Standard library only.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Import the analyzer as a module by loading it from file (no package layout).
import importlib.util  # noqa: E402

_ANALYZER_PATH = REPO_ROOT / "scripts" / "analyze_qwen_outputs.py"
_spec = importlib.util.spec_from_file_location(
    "analyze_qwen_outputs", _ANALYZER_PATH
)
assert _spec is not None and _spec.loader is not None
analyze_qwen_outputs = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(analyze_qwen_outputs)


class TestTask002CArtifactsExist(unittest.TestCase):
    def test_template_exists(self) -> None:
        self.assertTrue(
            (REPO_ROOT / "templates" / "qwen3_nonthinking.jinja").is_file(),
            "templates/qwen3_nonthinking.jinja must exist",
        )

    def test_template_is_nonempty(self) -> None:
        text = (REPO_ROOT / "templates" / "qwen3_nonthinking.jinja").read_text()
        self.assertGreater(len(text.strip()), 0)

    def test_template_references_non_thinking(self) -> None:
        text = (REPO_ROOT / "templates" / "qwen3_nonthinking.jinja").read_text()
        # Should reference the think block mechanism.
        self.assertTrue("think" in text.lower())

    def test_retest_script_exists(self) -> None:
        p = REPO_ROOT / "scripts" / "retest_qwen_direct.sh"
        self.assertTrue(p.is_file(), "scripts/retest_qwen_direct.sh must exist")

    def test_analyzer_exists(self) -> None:
        p = REPO_ROOT / "scripts" / "analyze_qwen_outputs.py"
        self.assertTrue(p.is_file(), "scripts/analyze_qwen_outputs.py must exist")

    def test_templates_readme_exists(self) -> None:
        self.assertTrue(
            (REPO_ROOT / "templates" / "README.md").is_file(),
            "templates/README.md must exist",
        )


class TestAnalyzerLogic(unittest.TestCase):
    def test_visible_answer_strips_closed_think(self) -> None:
        text = "<think>\nsome hidden reasoning\n</think>\n\n1. Restock fast movers.\n2. Hold credit."
        ans = analyze_qwen_outputs.visible_answer(text)
        self.assertNotIn("hidden reasoning", ans)
        self.assertIn("Restock", ans)

    def test_visible_answer_strips_unclosed_think(self) -> None:
        text = "Some preamble\n<think>\nreasoning that never closes\nmore tokens"
        ans = analyze_qwen_outputs.visible_answer(text)
        self.assertNotIn("reasoning that never closes", ans)

    def test_analyze_file_handles_missing(self) -> None:
        result = analyze_qwen_outputs.analyze_file(
            "x", REPO_ROOT / "nonexistent_file_xyz.txt"
        )
        self.assertFalse(result["exists"])
        self.assertFalse(result["useful"])
        self.assertEqual(result["answer_chars"], 0)

    def test_verdict_inconclusive_when_missing(self) -> None:
        results = [
            {"exists": False},
            {"exists": True, "useful": True},
            {"exists": True, "useful": True},
        ]
        self.assertEqual(analyze_qwen_outputs.verdict(results), "INCONCLUSIVE")

    def test_verdict_pass_when_two_useful(self) -> None:
        results = [
            {"exists": True, "useful": True},
            {"exists": True, "useful": True},
            {"exists": True, "useful": False},
        ]
        self.assertEqual(analyze_qwen_outputs.verdict(results), "PASS")

    def test_verdict_fail_when_trapped(self) -> None:
        results = [
            {"exists": True, "useful": False},
            {"exists": True, "useful": False},
            {"exists": True, "useful": False},
        ]
        self.assertEqual(analyze_qwen_outputs.verdict(results), "FAIL")

    def test_strip_logs_excludes_llama_log_lines(self) -> None:
        text = (
            "0.00.013.763 I llama_completion: init\n"
            "0.24.055.128 I common_perf_print: eval time = ...\n"
            "1. Restock the fast-moving items.\n"
            "2. Hold off on extending credit.\n"
        )
        cleaned = analyze_qwen_outputs._strip_logs(text)
        self.assertNotIn("common_perf", cleaned)
        self.assertIn("Restock", cleaned)


if __name__ == "__main__":
    unittest.main()
