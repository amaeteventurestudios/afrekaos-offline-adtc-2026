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

    def test_includes_language_selector(self) -> None:
        html_out = T.render_advisor_form("/advisor/daily", "H", "d", "x")
        self.assertIn('select name="language"', html_out)
        self.assertIn('value="en"', html_out)
        self.assertIn('value="fr"', html_out)
        self.assertIn('value="yo"', html_out)

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
            lambda: T.render_demo(),
        ):
            html_out = renderer()
            # No external src/href to http resources or cdn.
            self.assertNotIn("src=\"http", html_out)
            self.assertNotIn("href=\"http", html_out)
            self.assertNotIn("cdn", html_out.lower())


class TestBanner(unittest.TestCase):
    def test_home_has_offline_banner(self) -> None:
        html_out = T.render_home()
        self.assertIn("Offline mode", html_out)
        self.assertIn("Local model", html_out)
        self.assertIn("SQLite retrieval", html_out)
        self.assertIn("No cloud dependency", html_out)

    def test_all_pages_have_banner(self) -> None:
        for renderer in (
            lambda: T.render_home(),
            lambda: T.render_demo(),
            lambda: T.render_advisor_form("/x", "H", "d", "q"),
            lambda: T.render_advisor_result("H", "q", "a", "m"),
            lambda: T.render_status({"k": "v"}),
        ):
            self.assertIn("Offline mode", renderer())

    def test_banner_does_not_contain_13_marker(self) -> None:
        for renderer in (
            lambda: T.render_home(),
            lambda: T.render_demo(),
            lambda: T.render_advisor_form("/x", "H", "d", "q"),
            lambda: T.render_advisor_result("H", "q", "a", "m"),
            lambda: T.render_status({"k": "v"}),
        ):
            self.assertNotIn("13 Offline mode", renderer())

    def test_banner_has_explicit_checkmark(self) -> None:
        # The checkmark must be literal text in the HTML, not a CSS escape.
        html_out = T.render_home()
        self.assertIn("\u2713", html_out)


class TestLoadingFeedback(unittest.TestCase):
    def test_advisor_form_has_loading_message(self) -> None:
        html_out = T.render_advisor_form("/x", "H", "d", "q")
        self.assertIn(T.LOADING_MESSAGE, html_out)

    def test_advisor_form_has_submit_button_id(self) -> None:
        html_out = T.render_advisor_form("/x", "H", "d", "q")
        self.assertIn('id="submitBtn"', html_out)
        self.assertIn('type="submit"', html_out)

    def test_advisor_form_has_inline_script(self) -> None:
        html_out = T.render_advisor_form("/x", "H", "d", "q")
        self.assertIn("<script>", html_out)
        self.assertIn(T.LOADING_BUTTON_TEXT, html_out)

    def test_advisor_form_works_without_js(self) -> None:
        # The form must still be a normal POST even if JS is off: method + action.
        html_out = T.render_advisor_form("/advisor/daily", "H", "d", "q")
        self.assertIn('method="POST"', html_out)
        self.assertIn('action="/advisor/daily"', html_out)

    def test_demo_forms_have_loading_feedback(self) -> None:
        html_out = T.render_demo()
        self.assertIn("demoBtn1", html_out)
        self.assertIn(T.LOADING_BUTTON_TEXT, html_out)

    def test_demo_forms_have_language_selector(self) -> None:
        html_out = T.render_demo()
        self.assertIn('select name="language"', html_out)
        self.assertIn('value="fr"', html_out)


class TestJobPage(unittest.TestCase):
    def _job(self, **over) -> dict:
        base = {
            "job_id": "abc123",
            "advisor": "Daily Operations Advisor",
            "status": "running",
            "step": 5,
            "question": "demo question",
            "answer": "",
            "error": "",
            "mode_label": "retrieval-grounded, direct-answer",
            "runtime_notes": "",
        }
        base.update(over)
        return base

    def test_running_job_shows_steps_and_message(self) -> None:
        html_out = T.render_job(self._job())
        self.assertIn("30 to 90 seconds", html_out)
        self.assertIn("Running local Qwen model", html_out)  # step text present
        # Auto-refresh only while in progress.
        self.assertIn('http-equiv="refresh"', html_out)

    def test_complete_job_shows_answer(self) -> None:
        html_out = T.render_job(self._job(status="complete", step=7, answer="Restock items."))
        self.assertIn("Restock items.", html_out)
        # No auto-refresh once complete.
        self.assertNotIn('http-equiv="refresh"', html_out)

    def test_failed_job_shows_error(self) -> None:
        html_out = T.render_job(
            self._job(status="failed", error="model file not found")
        )
        self.assertIn("AfrekaOS hit a local runtime error", html_out)
        self.assertIn("model file not found", html_out)

    def test_status_detail_panel(self) -> None:
        detail = {
            "model_path_exists": True,
            "llama_binary": "/usr/local/bin/llama-completion",
            "retrieval_index_exists": True,
            "locked_candidate": "qwen3-1.7b-q4-k-m",
            "retrieval_grounded": True,
            "direct_answer": True,
            "local_only": True,
        }
        html_out = T.render_job(self._job(), detail=detail)
        self.assertIn("Locked candidate", html_out)
        self.assertIn("qwen3-1.7b-q4-k-m", html_out)
        self.assertIn("Retrieval-grounded", html_out)
        self.assertIn("Direct-answer mode", html_out)
        self.assertIn("Local-only", html_out)

    def test_complete_job_renders_clean_answer(self) -> None:
        html_out = T.render_job(
            self._job(status="complete", step=7, answer="Restock fast-moving items today.")
        )
        self.assertIn("Restock fast-moving items today.", html_out)
        # Must NOT show the empty-answer fallback when an answer exists.
        self.assertNotIn("(model produced no visible answer text)", html_out)

    def test_complete_job_shows_fallback_only_when_answer_empty(self) -> None:
        html_out = T.render_job(
            self._job(status="complete", step=7, answer="")
        )
        self.assertIn("(model produced no visible answer text)", html_out)

    def test_extraction_warning_renders_when_present(self) -> None:
        html_out = T.render_job(
            self._job(
                status="complete", step=7, answer="Restock items.",
                extraction_warning="Unclosed <think> block detected; hidden reasoning was removed.",
            )
        )
        self.assertIn("Unclosed", html_out)

    def test_runtime_summary_uses_clean_answer_chars(self) -> None:
        html_out = T.render_job(
            self._job(
                status="complete", step=7, answer="Restock items.",
                runtime_notes="return_code=0, clean_answer_chars=14, think_trap=False",
            )
        )
        self.assertIn("clean_answer_chars=14", html_out)
        self.assertIn("think_trap=False", html_out)

    def test_answer_panel_titled_operating_guidance(self) -> None:
        html_out = T.render_job(
            self._job(status="complete", step=7, answer="Restock items.")
        )
        self.assertIn("Operating Guidance", html_out)
        # The old parenthetical mode label is no longer in the title.
        self.assertNotIn(
            "Operating guidance (retrieval-grounded", html_out.lower()
        )

    def test_prompt_echo_note_shown_when_stripped(self) -> None:
        html_out = T.render_job(
            self._job(
                status="complete", step=7, answer="Restock items.",
                prompt_echo_stripped=True,
            )
        )
        self.assertIn("Prompt echo removed from display", html_out)

    def test_answer_panel_does_not_show_prompt_markers(self) -> None:
        # Even if a buggy caller passed echo text as the answer, the title
        # structure must not label it as prompt echo. This asserts the panel
        # title is clean.
        html_out = T.render_job(
            self._job(status="complete", step=7, answer="1. Restock items.")
        )
        self.assertNotIn("You are AfrekaOS", html_out)
        self.assertNotIn("Local SME operations context", html_out)
        self.assertNotIn("Answer rules", html_out)

    def test_job_page_shows_response_language(self) -> None:
        html_out = T.render_job(
            self._job(status="complete", step=7, answer="x", language_label="French")
        )
        self.assertIn("Response language:", html_out)
        self.assertIn("French", html_out)


class TestErrorPage(unittest.TestCase):
    def test_error_page_is_not_bare_500(self) -> None:
        html_out = T.render_error("boom", route="/advisor/daily")
        self.assertNotIn("500 — Server error", html_out)
        self.assertIn("AfrekaOS hit a local runtime error", html_out)

    def test_error_page_includes_route_and_checks(self) -> None:
        html_out = T.render_error("boom", route="/advisor/daily")
        self.assertIn("/advisor/daily", html_out)
        self.assertIn("model/afrekaos.gguf", html_out)
        self.assertIn("llama-completion", html_out)
        self.assertIn("time out", html_out.lower())

    def test_error_page_has_nav_links(self) -> None:
        html_out = T.render_error("boom")
        self.assertIn('href="/"', html_out)
        self.assertIn('href="/advisor/daily"', html_out)
        self.assertIn('href="/status"', html_out)

    def test_job_missing_page(self) -> None:
        html_out = T.render_job_missing("nope")
        self.assertIn("Job not found", html_out)
        self.assertIn("nope", html_out)


class TestUnifiedWarning(unittest.TestCase):
    def test_warning_text_constant(self) -> None:
        self.assertIn("not accounting", T.WARNING_TEXT.lower())
        self.assertIn("banking", T.WARNING_TEXT.lower())
        self.assertIn("payroll", T.WARNING_TEXT.lower())
        self.assertIn("tax", T.WARNING_TEXT.lower())
        self.assertIn("lending", T.WARNING_TEXT.lower())
        self.assertIn("erp", T.WARNING_TEXT.lower())

    def test_advisor_result_includes_unified_warning(self) -> None:
        html_out = T.render_advisor_result("H", "q", "a", "m")
        self.assertIn(T.WARNING_TEXT, html_out)


class TestDemoPage(unittest.TestCase):
    def test_demo_includes_heading(self) -> None:
        html_out = T.render_demo()
        self.assertIn("Demo Scenarios", html_out)

    def test_demo_includes_all_scenario_titles(self) -> None:
        html_out = T.render_demo()
        for title, _, _, _ in T.DEMO_SCENARIOS:
            self.assertIn(title, html_out)

    def test_demo_has_four_scenarios(self) -> None:
        self.assertEqual(len(T.DEMO_SCENARIOS), 4)

    def test_demo_scenarios_have_forms(self) -> None:
        html_out = T.render_demo()
        self.assertIn("<form", html_out)
        self.assertIn("Run this scenario", html_out)

    def test_demo_includes_nav_links(self) -> None:
        html_out = T.render_demo()
        self.assertIn("Mission Control", html_out)
        self.assertIn("Offline Status", html_out)


class TestNavLinks(unittest.TestCase):
    def test_advisor_result_has_nav(self) -> None:
        html_out = T.render_advisor_result("H", "q", "a", "m")
        self.assertIn('href="/"', html_out)
        self.assertIn('href="/demo"', html_out)
        self.assertIn('href="/status"', html_out)


if __name__ == "__main__":
    unittest.main()
