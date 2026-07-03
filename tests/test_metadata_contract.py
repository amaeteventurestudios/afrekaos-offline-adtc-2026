"""Metadata contract tests for AfrekaOS Offline.

Validates the structure of metadata.json against the fixed product contract.
Standard library only; does not require the model or llama.cpp; no network.
"""

from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_metadata import (  # noqa: E402
    EXPECTED_DOMAIN,
    EXPECTED_MODEL_PATH,
    EXPECTED_PRODUCT_TOKEN,
    EXPECTED_PROMPT_COUNT,
    check,
    load_metadata,
)

METADATA_PATH = REPO_ROOT / "metadata.json"


class TestMetadataContract(unittest.TestCase):
    def setUp(self) -> None:
        self.metadata = load_metadata(METADATA_PATH)

    def test_metadata_file_exists(self) -> None:
        self.assertTrue(METADATA_PATH.is_file(), "metadata.json must exist")

    def test_product_name(self) -> None:
        product = self.metadata.get("product_name")
        self.assertIsInstance(product, str)
        self.assertIn(EXPECTED_PRODUCT_TOKEN, product)

    def test_domain(self) -> None:
        self.assertEqual(self.metadata.get("domain"), EXPECTED_DOMAIN)

    def test_model_path(self) -> None:
        model = self.metadata.get("model")
        self.assertIsInstance(model, dict)
        self.assertEqual(model.get("path"), EXPECTED_MODEL_PATH)

    def test_exactly_two_prompts(self) -> None:
        prompts = self.metadata.get("test_prompts")
        self.assertIsInstance(prompts, list)
        self.assertEqual(len(prompts), EXPECTED_PROMPT_COUNT)

    def test_prompts_are_non_empty_strings(self) -> None:
        prompts = self.metadata.get("test_prompts", [])
        for i, item in enumerate(prompts):
            self.assertIsInstance(item, dict, f"prompt {i} must be an object")
            text = item.get("prompt")
            self.assertIsInstance(text, str, f"prompt {i} text must be string")
            self.assertTrue(text.strip(), f"prompt {i} text must be non-empty")

    def test_check_returns_no_errors_for_real_metadata(self) -> None:
        errors = check(self.metadata)
        self.assertEqual(errors, [], f"unexpected contract errors: {errors}")

    def test_check_flags_bad_domain(self) -> None:
        bad = json.loads(json.dumps(self.metadata))
        bad["domain"] = "wrong"
        errors = check(bad)
        self.assertTrue(any("domain" in e for e in errors))

    def test_check_flags_wrong_prompt_count(self) -> None:
        bad = json.loads(json.dumps(self.metadata))
        bad["test_prompts"] = bad["test_prompts"] + [
            {"id": "p3", "label": "x", "prompt": "extra"}
        ]
        errors = check(bad)
        self.assertTrue(any("exactly" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
