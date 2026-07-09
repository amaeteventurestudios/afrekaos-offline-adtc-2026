"""Tests for app/web_templates.py.

Validates HTML rendering, escaping, and page structure. Standard library only.
No model/llama.cpp/internet required.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import web_templates as T  # noqa: E402


class TestEscaping(unittest.TestCase):
    def test_escapes_script_injection(self) -> None:
        html_out = T.render_advisor_result(
            "Test", "<script>alert(1)</script>", "answer", "mode"
        )
        self.assertNotIn("<script>alert(1)</script>", html_out)
        self.assertIn("&lt;script&gt;", html_out)

    def test_escapes_in_form_default(self) -> None:
        html_out = T.render_advisor_form(
            "/x", "H", "d", "default <b>bold</b> 'quote\""
        )
        self.assertNotIn("<b>bold</b>", html_out)
        self.assertIn("&lt;b&gt;", html_out)

    def test_escapes_answer_text(self) -> None:
        html_out = T.render_advisor_result(
            "H", "q", "<img src=x onerror=alert(1)>", "mode"
        )
        self.assertNotIn("<img src=x", html_out)

    def test_escapes_status_values(self) -> None:
        html_out = T.render_status({"key": "<script>", "ok": True})
        self.assertNotIn("<script>", html_out)


class TestHomePage(unittest.TestCase):
    def test_includes_product_name(self) -> None:
        html_out = T.render_home()
        self.assertIn("AfrekaOS Offline", html_out)

    def test_includes_mission_control(self) -> None:
        html_out = T.render_home()
        self.assertIn("Mission Control", html_out)

    def test_includes_advisor_links(self) -> None:
        html_out = T.render_home()
        for href in ("/advisor/daily", "/advisor/inventory", "/advisor/cashflow", "/status"):
            self.assertIn(href, html_out)

    def test_includes_description(self) -> None:
        html_out = T.render_home()
        self.assertIn("offline sme operations copilot", html_out.lower())
        self.assertIn("copilot", html_out.lower())


class TestAdvisorForm(unittest.TestCase):
    def test_includes_textarea(self) -> None:
        html_out = T.render_advisor_form("/x", "H", "d", "default")
        self.assertIn("<textarea", html_out)
        self.assertIn("name=\"question\"", html_out)

    def test_includes_default_question(self) -> None:
        html_out = T.render_advisor_form("/x", "H", "d", "my default text")
        self.assertIn("my default text", html_out)

    def test_form_posts_to_action(self) -> None:
        html_out = T.render_advisor_form("/advisor/daily", "H", "d", "x")
        self.assertIn('action="/advisor/daily"', html_out)
        self.assertIn("POST", html_out)


class TestAdvisorResult(unittest.TestCase):
    def test_includes_warning(self) -> None:
        html_out = T.render_advisor_result("H", "q", "a", "mode")
        self.assertIn("not accounting", html_out.lower())
        self.assertIn("banking", html_out.lower())
        self.assertIn("payroll", html_out.lower())

    def test_includes_question_and_answer(self) -> None:
        html_out = T.render_advisor_result("H", "my question", "my answer", "mode")
        self.assertIn("my question", html_out)
        self.assertIn("my answer", html_out)

    def test_includes_mode_label(self) -> None:
        html_out = T.render_advisor_result("H", "q", "a", "retrieval-grounded")
        self.assertIn("retrieval-grounded", html_out)


class TestStatusPage(unittest.TestCase):
    def test_renders_keys(self) -> None:
        html_out = T.render_status({"product": "AfrekaOS Offline", "ok": True})
        self.assertIn("AfrekaOS Offline", html_out)
        self.assertIn("product", html_out)

    def test_handles_missing_model_gracefully(self) -> None:
        html_out = T.render_status(
            {"model_path_exists": False, "llama_binary_detected": "not detected"}
        )
        self.assertIn("no", html_out)  # the pill for False


class TestHealthJson(unittest.TestCase):
    def test_returns_valid_json(self) -> None:
        import json

        out = T.health_json({"ok": True, "product": "AfrekaOS Offline"})
        data = json.loads(out)
        self.assertTrue(data["ok"])
        self.assertEqual(data["product"], "AfrekaOS Offline")


class TestNoExternalDeps(unittest.TestCase):
    def test_no_external_css_js_links(self) -> None:
        for renderer in (
            lambda: T.render_home(),
            lambda: T.render_advisor_form("/x", "H", "d", "q"),
            lambda: T.render_advisor_result("H", "q", "a", "m"),
            lambda: T.render_status({"k": "v"}),
        ):
            html_out = renderer()
            # No external src/href to http resources or cdn.
            self.assertNotIn("src=\"http", html_out)
            self.assertNotIn("href=\"http", html_out)
            self.assertNotIn("cdn", html_out.lower())


if __name__ == "__main__":
    unittest.main()
