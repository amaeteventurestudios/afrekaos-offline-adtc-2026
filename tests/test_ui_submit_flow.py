"""Tests for the advisor submit → job progress flow (Task 004C).

Validates that:
- POSTing an advisor question returns a 303 redirect to /job/<id>.
- The job page renders progress/completion/failure content.
- Demo scenario forms submit to the right advisor action.
- The status banner no longer shows "13 Offline mode".
- No real model inference is required (model path forced to nonexistent).

Uses only the Python standard library: http.server + urllib in-process.
"""

from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
import unittest
import urllib.request
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

HOST = "127.0.0.1"
PORT = 8791  # dedicated port to avoid clashes
BASE = f"http://{HOST}:{PORT}"


def _wait_for_health(timeout: float = 20.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"{BASE}/health", timeout=2) as r:
                if r.status == 200:
                    return True
        except Exception:
            time.sleep(0.3)
    return False


def _start_server() -> subprocess.Popen:
    env = dict(os.environ)
    env["AFREKAOS_QWEN_NO_THINK"] = "1"
    # Force a nonexistent model so any job fails fast without real inference.
    env["AFREKAOS_MODEL_PATH"] = "/nonexistent/submit_flow_test.gguf"
    env["AFREKAOS_UI_TIMEOUT"] = "5"
    env["AFREKAOS_WEB_PORT"] = str(PORT)
    return subprocess.Popen(
        [sys.executable, "-m", "app.web_app"],
        cwd=str(REPO_ROOT),
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )


class _ServerFixture(unittest.TestCase):
    """Base class that starts/stops the server once for the test class."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.proc = _start_server()
        if not _wait_for_health():
            cls.proc.send_signal(signal.SIGTERM)
            try:
                cls.proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                cls.proc.kill()
            raise RuntimeError("server did not become healthy")

    @classmethod
    def tearDownClass(cls) -> None:
        cls.proc.send_signal(signal.SIGTERM)
        try:
            cls.proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            cls.proc.kill()
            cls.proc.wait(timeout=5)


class TestAdvisorPostRedirect(_ServerFixture):
    def test_post_daily_returns_303_to_job(self) -> None:
        # Don't follow redirects; we want the raw 303 + Location.
        class _NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None

        opener = urllib.request.build_opener(_NoRedirect)
        data = b"question=" + urllib.request.quote(
            "A small shop has low sales and stockouts. Give a short checklist."
        ).encode()
        req = urllib.request.Request(
            f"{BASE}/advisor/daily", data=data, method="POST"
        )
        try:
            opener.open(req, timeout=10)
            self.fail("expected a redirect")
        except urllib.error.HTTPError as exc:
            self.assertEqual(exc.code, 303)
            loc = exc.headers.get("Location", "")
            self.assertTrue(loc.startswith("/job/"), f"unexpected Location: {loc}")
        else:
            self.fail("expected HTTPError for the redirect")

    def test_post_inventory_returns_303_to_job(self) -> None:
        class _NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k):
                return None

        opener = urllib.request.build_opener(_NoRedirect)
        data = b"question=" + urllib.request.quote("stockout checklist").encode()
        req = urllib.request.Request(
            f"{BASE}/advisor/inventory", data=data, method="POST"
        )
        try:
            opener.open(req, timeout=10)
        except urllib.error.HTTPError as exc:
            self.assertEqual(exc.code, 303)
            self.assertTrue(exc.headers.get("Location", "").startswith("/job/"))

    def test_post_empty_question_does_not_create_job(self) -> None:
        # Empty question should NOT redirect to a job; it re-renders a result
        # page with a "please enter" note (HTTP 200).
        data = b"question="
        req = urllib.request.Request(
            f"{BASE}/advisor/daily", data=data, method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as r:
            body = r.read().decode("utf-8", errors="replace")
            self.assertEqual(r.status, 200)
            self.assertIn("enter an operations question", body.lower())


class TestJobPage(_ServerFixture):
    def _create_job_via_post(self, advisor: str = "/advisor/daily") -> str:
        """POST and follow the redirect; return the job id."""
        data = b"question=" + urllib.request.quote("demo q").encode()
        req = urllib.request.Request(f"{BASE}{advisor}", data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            # After 303 redirect, urllib follows to the job page.
            return r.geturl(), r.read().decode("utf-8", errors="replace")

    def test_job_page_renders_progress(self) -> None:
        url, body = self._create_job_via_post()
        self.assertIn("/job/", url)
        # The page should show the advisor and the runtime status panel.
        self.assertIn("Daily Operations Advisor", body)
        self.assertIn("Runtime status", body)
        # Either the progress message (running) or a final error/answer.
        self.assertTrue(
            "30 to 90 seconds" in body or "runtime error" in body.lower(),
            "expected progress message or error",
        )

    def test_job_page_has_status_detail_panel(self) -> None:
        _, body = self._create_job_via_post()
        self.assertIn("Locked candidate", body)
        self.assertIn("Local-only", body)
        self.assertIn("Retrieval-grounded", body)
        self.assertIn("Direct-answer mode", body)

    def test_job_page_has_no_13_marker(self) -> None:
        _, body = self._create_job_via_post()
        self.assertNotIn("13 Offline mode", body)

    def test_unknown_job_returns_not_found(self) -> None:
        try:
            urllib.request.urlopen(
                f"{BASE}/job/definitely-missing", timeout=10
            )
            self.fail("expected 404")
        except urllib.error.HTTPError as exc:
            self.assertEqual(exc.code, 404)
            body = exc.read().decode("utf-8", errors="replace")
            self.assertIn("Job not found", body)


class TestDemoForms(_ServerFixture):
    def test_demo_forms_post_to_advisors(self) -> None:
        from app import web_templates as T

        html_out = T.render_demo()
        # Each demo scenario form must post to one of the advisor actions.
        for _title, action, _advisor, _prompt in T.DEMO_SCENARIOS:
            self.assertIn(f'action="{action}"', html_out)
            self.assertIn("method=\"POST\"", html_out)
        self.assertIn("name=\"question\"", html_out)
        self.assertIn("type=\"submit\"", html_out)


class TestBannerAcrossRoutes(_ServerFixture):
    def test_advisor_form_no_13_marker(self) -> None:
        with urllib.request.urlopen(
            f"{BASE}/advisor/daily", timeout=10
        ) as r:
            body = r.read().decode("utf-8", errors="replace")
            self.assertNotIn("13 Offline mode", body)
            self.assertIn("Offline mode", body)
            self.assertIn("Local model", body)
            self.assertIn("SQLite retrieval", body)
            self.assertIn("No cloud dependency", body)

    def test_home_no_13_marker(self) -> None:
        with urllib.request.urlopen(f"{BASE}/", timeout=10) as r:
            body = r.read().decode("utf-8", errors="replace")
            self.assertNotIn("13 Offline mode", body)


if __name__ == "__main__":
    unittest.main()