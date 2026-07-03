"""Tests for app.runtime_config.

Validates helper behavior without requiring the model file or llama.cpp to
exist, and without touching the network. Standard library only.
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import runtime_config  # noqa: E402


class TestRuntimeConfig(unittest.TestCase):
    def setUp(self) -> None:
        # Snapshot env so each test starts clean.
        self._old_model = os.environ.pop("AFREKAOS_MODEL_PATH", None)
        self._old_bin = os.environ.pop("LLAMA_CPP_BIN", None)

    def tearDown(self) -> None:
        os.environ.pop("AFREKAOS_MODEL_PATH", None)
        os.environ.pop("LLAMA_CPP_BIN", None)
        if self._old_model is not None:
            os.environ["AFREKAOS_MODEL_PATH"] = self._old_model
        if self._old_bin is not None:
            os.environ["LLAMA_CPP_BIN"] = self._old_bin

    def test_default_model_path_constant(self) -> None:
        self.assertEqual(runtime_config.DEFAULT_MODEL_PATH, "model/afrekaos.gguf")

    def test_get_model_path_default_resolves_under_repo(self) -> None:
        p = runtime_config.get_model_path()
        self.assertTrue(p.is_absolute())
        self.assertEqual(p.name, "afrekaos.gguf")
        # default resolves under the repo root
        self.assertTrue(str(p).startswith(str(runtime_config.REPO_ROOT)))

    def test_get_model_path_env_override(self) -> None:
        os.environ["AFREKAOS_MODEL_PATH"] = "/tmp/some/other.gguf"
        p = runtime_config.get_model_path()
        self.assertEqual(p, Path("/tmp/some/other.gguf"))

    def test_get_model_path_relative_override(self) -> None:
        os.environ["AFREKAOS_MODEL_PATH"] = "model/custom.gguf"
        p = runtime_config.get_model_path()
        self.assertTrue(p.is_absolute())
        self.assertEqual(p.name, "custom.gguf")

    def test_get_llama_binary_default_empty(self) -> None:
        self.assertEqual(runtime_config.get_llama_binary(), "")

    def test_get_llama_binary_env_override(self) -> None:
        os.environ["LLAMA_CPP_BIN"] = "/usr/local/bin/llama-cli"
        self.assertEqual(
            runtime_config.get_llama_binary(), "/usr/local/bin/llama-cli"
        )

    def test_model_exists_is_bool(self) -> None:
        self.assertIsInstance(runtime_config.model_exists(), bool)

    def test_runtime_summary_shape(self) -> None:
        summary = runtime_config.runtime_summary()
        self.assertIsInstance(summary, dict)
        for key in (
            "model_path",
            "model_exists",
            "llama_cpp_bin",
            "llama_cpp_bin_configured",
            "llama_cpp_bin_exists",
            "default_model_path",
            "afrekaos_model_path_env",
        ):
            self.assertIn(key, summary)
        self.assertIsInstance(summary["model_exists"], bool)
        self.assertIsInstance(summary["model_path"], str)
        self.assertEqual(
            summary["default_model_path"],
            runtime_config.DEFAULT_MODEL_PATH,
        )


if __name__ == "__main__":
    unittest.main()
