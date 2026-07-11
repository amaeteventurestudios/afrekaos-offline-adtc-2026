"""Tests for Task 005C target hardware scripts.

Validates the profiler collects a dict, the analyzer handles missing dirs,
detects think traps, detects forbidden claims, and can PASS a fake SME output.
Standard library only; no model/llama.cpp/internet required.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Load the profiler and analyzer as modules.
_PROF_PATH = REPO_ROOT / "scripts" / "target_hardware_profile.py"
_spec_p = importlib.util.spec_from_file_location("target_hardware_profile", _PROF_PATH)
assert _spec_p is not None and _spec_p.loader is not None
prof = importlib.util.module_from_spec(_spec_p)
_spec_p.loader.exec_module(prof)

_AN_PATH = REPO_ROOT / "scripts" / "analyze_target_benchmark.py"
_spec_a = importlib.util.spec_from_file_location("analyze_target_benchmark", _AN_PATH)
assert _spec_a is not None and _spec_a.loader is not None
az = importlib.util.module_from_spec(_spec_a)
_spec_a.loader.exec_module(az)


class TestProfiler(unittest.TestCase):
    def test_collect_returns_dict(self) -> None:
        d = prof.collect()
        self.assertIsInstance(d, dict)

    def test_collect_has_required_keys(self) -> None:
        d = prof.collect()
        for key in (
            "os", "python_version", "ubuntu_22_04_detected",
            "cpu_model", "physical_cores", "logical_cores",
            "total_memory_bytes", "available_memory_bytes",
            "model_exists", "model_is_symlink", "llama_binary",
            "retrieval_index_exists", "sqlite_fts5_available",
        ):
            self.assertIn(key, d)

    def test_render_does_not_crash(self) -> None:
        d = prof.collect()
        out = prof.render(d)
        self.assertIsInstance(out, str)
        self.assertIn("Target Hardware Profile", out)


class TestAnalyzerMissingDir(unittest.TestCase):
    def test_missing_directory_no_crash(self) -> None:
        results = az.analyze_all(Path("/tmp/afrekaos_nonexistent_005c_xyz"))
        for f in az.FILES:
            self.assertFalse(results[f].get("exists", False))

    def test_verdict_inconclusive_when_missing(self) -> None:
        results = az.analyze_all(Path("/tmp/afrekaos_nonexistent_005c_xyz2"))
        self.assertEqual(az.verdict(results), "INCONCLUSIVE")


class TestAnalyzerThinkTrap(unittest.TestCase):
    def test_detects_unclosed_think(self) -> None:
        text = (
            "<think>\nLet me reason carefully about this shop's inventory "
            "and cashflow situation to provide a good checklist answer."
        )
        self.assertTrue(az._think_trap(text))

    def test_closed_think_not_trap(self) -> None:
        text = "<think>\n\n</think>\n\n1. Check inventory."
        self.assertFalse(az._think_trap(text))

    def test_contains_think_distinct_from_trap(self) -> None:
        # Empty template: contains_think True, think_trap False.
        text = "<think>\n\n</think>\n\n1. Check inventory."
        self.assertTrue(az._contains_think(text))
        self.assertFalse(az._think_trap(text))

    def test_no_think_when_absent(self) -> None:
        self.assertFalse(az._contains_think("1. Check inventory."))


class TestAnalyzerForbiddenClaims(unittest.TestCase):
    def test_detects_accounting_claim(self) -> None:
        text = "This is accounting software for your shop."
        self.assertTrue(az.FORBIDDEN_RE.search(text))

    def test_detects_erp_claim(self) -> None:
        text = "We are an ERP system."
        self.assertTrue(az.FORBIDDEN_RE.search(text))

    def test_no_claim_for_sme_content(self) -> None:
        text = "Check inventory levels and contact your supplier."
        self.assertFalse(az.FORBIDDEN_RE.search(text))


class TestAnalyzerVerdict(unittest.TestCase):
    def _make_results(self, texts: dict) -> dict:
        """texts: {filename: content}. Returns analyze_all-style dict."""
        with tempfile.TemporaryDirectory() as tmp:
            tmpd = Path(tmp)
            for fname, content in texts.items():
                (tmpd / fname).write_text(content, encoding="utf-8")
            return az.analyze_all(tmpd)

    def test_pass_for_good_sme_outputs(self) -> None:
        good = (
            "1. Check inventory for stockouts of fast-moving items.\n"
            "2. Contact the supplier about delivery delay and lead times.\n"
            "3. Hold off on extending credit until cash records are verified.\n"
            "4. Review cashflow before committing to new expenses."
        )
        texts = {f: good for f in az.FILES}
        results = self._make_results(texts)
        self.assertEqual(az.verdict(results), "PASS")

    def test_fail_for_derailed_output(self) -> None:
        good = "Check inventory. Contact supplier. Review credit. Verify cash records."
        derailed = "In Mendeleev's Periodic Table atomic number 112 is key."
        texts = {
            "prompt-1-grounded.txt": derailed,
            "prompt-2-grounded.txt": good,
            "smoke-grounded.txt": good,
        }
        results = self._make_results(texts)
        self.assertEqual(az.verdict(results), "FAIL")

    def test_fail_for_think_trap(self) -> None:
        good = "Check inventory. Contact supplier. Review credit. Verify cash records."
        trapped = (
            "<think>\nOkay let me reason through this shop problem carefully "
            "and figure out what to check first for the operator here."
        )
        texts = {
            "prompt-1-grounded.txt": trapped,
            "prompt-2-grounded.txt": good,
            "smoke-grounded.txt": good,
        }
        results = self._make_results(texts)
        self.assertEqual(az.verdict(results), "FAIL")

    def test_fail_for_forbidden_claim(self) -> None:
        good = "Check inventory. Contact supplier. Review credit. Verify cash records."
        claimed = "This is accounting software. Check inventory and cash."
        texts = {
            "prompt-1-grounded.txt": claimed,
            "prompt-2-grounded.txt": good,
            "smoke-grounded.txt": good,
        }
        results = self._make_results(texts)
        self.assertEqual(az.verdict(results), "FAIL")


if __name__ == "__main__":
    unittest.main()
