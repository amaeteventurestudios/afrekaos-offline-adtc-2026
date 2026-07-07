"""Tests for scripts/analyze_grounded_outputs.py.

Validates the analyzer handles missing directories, detects <think>, detects
derailment terms, and returns PASS/FAIL correctly on synthetic outputs.
Standard library only; no model/llama.cpp/internet required.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Load the analyzer module from file (no package layout for scripts).
_ANALYZER_PATH = REPO_ROOT / "scripts" / "analyze_grounded_outputs.py"
_spec = importlib.util.spec_from_file_location(
    "analyze_grounded_outputs", _ANALYZER_PATH
)
assert _spec is not None and _spec.loader is not None
ag = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(ag)


class TestAnalyzeMissingDir(unittest.TestCase):
    def test_missing_directory_no_crash(self) -> None:
        results = ag.analyze_all(Path("/tmp/afrekaos_nonexistent_003b_xyz"))
        # All entries should report exists=False.
        for tag in ag.TAGS:
            for mode in ag.MODES:
                self.assertFalse(results[tag][mode].get("exists", False))

    def test_verdict_inconclusive_when_missing(self) -> None:
        results = ag.analyze_all(Path("/tmp/afrekaos_nonexistent_003b_xyz2"))
        self.assertEqual(ag.verdict(results), "INCONCLUSIVE")


class TestAnalyzeThink(unittest.TestCase):
    def test_closed_think_block_is_not_a_trap(self) -> None:
        # A closed <think>...</think> block (incl. the empty template block) is
        # the intended non-thinking mechanism, NOT a thinking trap.
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("<think>\nhidden reasoning\n</think>\n\n1. Restock items.")
            path = Path(f.name)
        try:
            r = ag.analyze_output(path)
            self.assertFalse(r["contains_think"])
        finally:
            path.unlink()

    def test_unclosed_think_block_is_a_trap(self) -> None:
        # An unclosed <think> with real reasoning after it IS a trap.
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(
                "<think>\nOkay let me reason through this carefully. "
                "The shop has low sales and stockouts so I need to figure out "
                "what to check first and what to avoid doing immediately here."
            )
            path = Path(f.name)
        try:
            r = ag.analyze_output(path)
            self.assertTrue(r["contains_think"])
        finally:
            path.unlink()

    def test_empty_template_think_block_is_not_a_trap(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("<think>\n\n</think>\n\n1. Restock fast-moving items.")
            path = Path(f.name)
        try:
            r = ag.analyze_output(path)
            self.assertFalse(r["contains_think"])
        finally:
            path.unlink()

    def test_no_think_when_absent(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write("1. Check inventory levels.\n2. Contact supplier.")
            path = Path(f.name)
        try:
            r = ag.analyze_output(path)
            self.assertFalse(r["contains_think"])
        finally:
            path.unlink()


class TestAnalyzeDerailment(unittest.TestCase):
    def test_detects_chemistry_derailment(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(
                "In the Mendeleev's Periodic Table, the position of the element "
                "with atomic number 112 is important for this shop."
            )
            path = Path(f.name)
        try:
            r = ag.analyze_output(path)
            self.assertTrue(r["has_derailment"])
        finally:
            path.unlink()

    def test_no_derailment_for_sme_content(self) -> None:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as f:
            f.write(
                "1. Check inventory for stockouts of fast-moving items.\n"
                "2. Contact the supplier about delivery delay.\n"
                "3. Hold off on extending credit until cash records are verified."
            )
            path = Path(f.name)
        try:
            r = ag.analyze_output(path)
            self.assertFalse(r["has_derailment"])
            self.assertGreaterEqual(len(r["sme_terms_found"]), 3)
        finally:
            path.unlink()


class TestVerdict(unittest.TestCase):
    def _make_results(self, p1_grounded_text: str) -> dict:
        """Build a results dict where only prompt-1-grounded is a real file."""
        with tempfile.TemporaryDirectory() as tmp:
            tmpd = Path(tmp)
            (tmpd / "prompt-1-grounded.txt").write_text(p1_grounded_text, encoding="utf-8")
            results = ag.analyze_all(tmpd)
            return results

    def test_pass_for_good_sme_output(self) -> None:
        text = (
            "1. Check inventory for stockouts of fast-moving items.\n"
            "2. Contact the supplier about the delivery delay and lead times.\n"
            "3. Hold off on extending credit until cash records are verified.\n"
            "4. Review cashflow and avoid panic reordering."
        )
        results = self._make_results(text)
        self.assertEqual(ag.verdict(results), "PASS")

    def test_fail_for_derailed_output(self) -> None:
        text = (
            "B. Check the sales and inventory status.\n\n"
            "In Mendeleev's Periodic Table, the position of the element with "
            "atomic number 112 is in the 1st period."
        )
        results = self._make_results(text)
        self.assertEqual(ag.verdict(results), "FAIL")

    def test_fail_for_empty_output(self) -> None:
        results = self._make_results("")
        self.assertEqual(ag.verdict(results), "FAIL")

    def test_fail_for_think_trap(self) -> None:
        text = "<think>\nOkay let me reason about this shop.\n"
        results = self._make_results(text)
        self.assertEqual(ag.verdict(results), "FAIL")


if __name__ == "__main__":
    unittest.main()
