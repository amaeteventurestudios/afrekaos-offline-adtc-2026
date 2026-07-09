"""Tests for app/web_app.py.

Validates route handling, health payload shape, status rendering, and that
no real model inference is triggered in unit tests. Standard library only.
No model/llama.cpp/internet required.
"""

from __future__ import annotations

import json
import os
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import web_app  # noqa: E402


class TestHealthPayload(unittest.TestCase):
    def test_shape(self) -> None:
        h = web_app.health_payload()
        for key in ("ok", "product", "model_exists", "retrieval_index_exists",
                     "llama_binary", "locked_candidate"):
            self.assertIn(key, h)
        self.assertEqual(h["product"], "AfrekaOS Offline")
        self.assertIsInstance(h["model_exists"], bool)
        self.assertIsInstance(h["retrieval_index_exists"], bool)

    def test_ok_is_true(self) -> None:
        h = web_app.health_payload()
        self.assertTrue(h["ok"])


class TestStatusPayload(unittest.TestCase):
    def test_shape(self) -> None:
        s = web_app.status_payload()
        for key in (
            "product", "model_lock", "canonical_model_path",
            "model_path_exists", "model_path_is_symlink",
            "llama_binary_detected", "retrieval_index_exists",
            "indexed_documents", "sqlite_fts_status",
            "qwen_direct_answer", "cloud_dependency",
        ):
            self.assertIn(key, s)
        self.assertEqual(s["product"], "AfrekaOS Offline")

    def test_cloud_dependency_is_none(self) -> None:
        s = web_app.status_payload()
        self.assertIn("none", s["cloud_dependency"].lower())
        self.assertIn("local", s["cloud_dependency"].lower())

    def test_handles_missing_model(self) -> None:
        # status_payload should not crash even if model is missing.
        s = web_app.status_payload()
        self.assertIsInstance(s["model_path_exists"], bool)


class TestRouteHandling(unittest.TestCase):
    """Test the Handler routing logic without starting a real server.

    We instantiate the handler's logic by checking that the render functions
    referenced by each route exist and produce valid HTML containing expected
    content.
    """

    def test_home_route_renders(self) -> None:
        from app import web_templates as T

        html = T.render_home()
        self.assertIn("AfrekaOS Offline", html)
        self.assertIn("Mission Control", html)

    def test_status_route_renders(self) -> None:
        from app import web_templates as T

        html = T.render_status(web_app.status_payload())
        self.assertIn("Offline System Status", html)

    def test_health_route_is_json(self) -> None:
        from app import web_templates as T

        out = T.health_json(web_app.health_payload())
        data = json.loads(out)
        self.assertTrue(data["ok"])

    def test_advisor_daily_form_renders(self) -> None:
        from app import web_templates as T

        html = T.render_advisor_form(
            "/advisor/daily", "Daily Operations Advisor", "desc",
            web_app.DEFAULT_DAILY,
        )
        self.assertIn("Daily Operations Advisor", html)
        self.assertIn(web_app.DEFAULT_DAILY, html)


class TestExtractAnswer(unittest.TestCase):
    def test_strips_think_block(self) -> None:
        raw = "<think>\n\n</think>\n\n1. Check inventory.\n2. Call supplier."
        out = web_app._extract_answer(raw)
        self.assertIn("Check inventory", out)
        self.assertNotIn("<think>", out)

    def test_strips_log_lines(self) -> None:
        raw = (
            "0.03.201.688 I sampler seed: 123\n"
            "0.24.055.128 I common_perf_print: eval time\n"
            "1. Restock fast-moving items.\n2. Hold credit."
        )
        out = web_app._extract_answer(raw)
        self.assertIn("Restock", out)
        self.assertNotIn("common_perf", out)
        self.assertNotIn("sampler seed", out)

    def test_empty_input(self) -> None:
        self.assertEqual(web_app._extract_answer(""), "")


class TestNoInferenceInTests(unittest.TestCase):
    """Ensure importing web_app does not trigger model inference."""

    def test_import_does_not_call_model(self) -> None:
        # If import had called the model, it would need a model file; since
        # tests pass without one, import is safe.
        self.assertTrue(hasattr(web_app, "Handler"))


if __name__ == "__main__":
    unittest.main()
