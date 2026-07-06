"""Tests for model.candidates.json contract (Task 002B bake-off).

Validates the candidate set, roles, canonical winner path, local path
location, and prohibited-use boundaries. Standard library only; does not
require model files, llama.cpp, or internet.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_model_candidates import (  # noqa: E402
    EXPECTED_CONTROL,
    EXPECTED_COUNT,
    EXPECTED_PRIMARY,
    EXPECTED_SECONDARY,
    EXPECTED_WINNER_PATH,
    check,
    load_candidates,
)

CANDIDATES_PATH = REPO_ROOT / "model.candidates.json"


class TestModelCandidates(unittest.TestCase):
    def setUp(self) -> None:
        self.data = load_candidates(CANDIDATES_PATH)

    def test_file_exists(self) -> None:
        self.assertTrue(CANDIDATES_PATH.is_file())

    def test_product(self) -> None:
        self.assertEqual(self.data.get("product"), "AfrekaOS Offline")

    def test_selection_mode(self) -> None:
        self.assertEqual(self.data.get("selection_mode"), "qwen_first_bakeoff")

    def test_canonical_winner_path(self) -> None:
        self.assertEqual(
            self.data.get("canonical_winning_model_path"),
            EXPECTED_WINNER_PATH,
        )

    def test_exactly_three_candidates(self) -> None:
        cands = self.data.get("candidates")
        self.assertIsInstance(cands, list)
        self.assertEqual(len(cands), EXPECTED_COUNT)

    def test_required_ids_and_roles(self) -> None:
        by_id = {c["id"]: c for c in self.data["candidates"]}
        self.assertIn(EXPECTED_PRIMARY, by_id)
        self.assertIn(EXPECTED_SECONDARY, by_id)
        self.assertIn(EXPECTED_CONTROL, by_id)
        self.assertEqual(by_id[EXPECTED_PRIMARY]["role"], "primary_speed_candidate")
        self.assertEqual(by_id[EXPECTED_SECONDARY]["role"], "secondary_reasoning_candidate")
        self.assertEqual(by_id[EXPECTED_CONTROL]["role"], "control_candidate")

    def test_local_paths_under_candidates_dir(self) -> None:
        for c in self.data["candidates"]:
            lcp = c["local_candidate_path"].replace("\\", "/")
            self.assertTrue(
                lcp.startswith("model/candidates/"),
                f"{c['id']} path not under model/candidates/: {lcp}",
            )
            self.assertTrue(lcp.endswith(".gguf"))

    def test_each_candidate_has_required_fields(self) -> None:
        required = ("id", "repo", "quantization", "format", "role",
                    "local_candidate_path", "selection_reason")
        for c in self.data["candidates"]:
            for f in required:
                self.assertIsInstance(c.get(f), str, f"{c.get('id')}: {f}")
                self.assertTrue(c.get(f, "").strip(), f"{c.get('id')}: {f} empty")
            self.assertEqual(c.get("format"), "GGUF")

    def test_quantizations_are_q4_k_m(self) -> None:
        for c in self.data["candidates"]:
            self.assertEqual(c.get("quantization"), "Q4_K_M")

    def test_repos_match_expected(self) -> None:
        by_id = {c["id"]: c for c in self.data["candidates"]}
        self.assertEqual(by_id[EXPECTED_PRIMARY]["repo"],
                         "bartowski/Qwen_Qwen3-1.7B-GGUF")
        self.assertEqual(by_id[EXPECTED_SECONDARY]["repo"],
                         "bartowski/Qwen_Qwen3-4B-GGUF")
        self.assertEqual(by_id[EXPECTED_CONTROL]["repo"],
                         "ibm-granite/granite-4.1-3b-GGUF")

    def test_prohibited_use_boundaries(self) -> None:
        prohibited = self.data.get("prohibited_use")
        self.assertIsInstance(prohibited, list)
        self.assertTrue(prohibited, "prohibited_use must be non-empty")
        joined = " ".join(prohibited).lower()
        for tok in ("cloud", "customer", "banking", "payroll", "tax", "erp"):
            self.assertIn(tok, joined, f"missing boundary token: {tok}")

    def test_check_returns_no_errors_for_real_data(self) -> None:
        errors = check(self.data)
        self.assertEqual(errors, [], f"unexpected contract errors: {errors}")

    def test_check_flags_wrong_count(self) -> None:
        bad = json.loads(json.dumps(self.data))
        bad["candidates"].append(json.loads(json.dumps(bad["candidates"][0])))
        self.assertTrue(any("exactly" in e for e in check(bad)))

    def test_check_flags_wrong_primary(self) -> None:
        bad = json.loads(json.dumps(self.data))
        for c in bad["candidates"]:
            if c["id"] == EXPECTED_PRIMARY:
                c["id"] = "something-else"
        errs = check(bad)
        self.assertTrue(any("missing required candidate" in e for e in errs))


if __name__ == "__main__":
    unittest.main()
