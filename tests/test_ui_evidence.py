"""Tests for scripts/capture_ui_evidence.py.

Validates the capture script can be imported and its helper functions work
without starting a real model. Standard library only; no model/llama.cpp/
internet required.
"""

from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

# Load the capture script as a module.
_CAP_PATH = REPO_ROOT / "scripts" / "capture_ui_evidence.py"
_spec = importlib.util.spec_from_file_location("capture_ui_evidence", _CAP_PATH)
assert _spec is not None and _spec.loader is not None
capture = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(capture)


class TestCaptureScriptImports(unittest.TestCase):
    def test_module_loads(self) -> None:
        self.assertTrue(hasattr(capture, "main"))

    def test_routes_defined(self) -> None:
        self.assertIsInstance(capture.ROUTES, list)
        self.assertGreater(len(capture.ROUTES), 0)
        # Each route is (path, filename, label).
        for item in capture.ROUTES:
            self.assertEqual(len(item), 3)

    def test_routes_include_key_pages(self) -> None:
        paths = [r[0] for r in capture.ROUTES]
        for p in ("/", "/demo", "/status"):
            self.assertIn(p, paths)

    def test_output_dir_is_under_artifacts(self) -> None:
        self.assertIn("artifacts", str(capture.OUT_DIR))
        self.assertIn("task-004B", str(capture.OUT_DIR))


class TestFinishHelper(unittest.TestCase):
    def test_finish_writes_notes(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            # Monkeypatch OUT_DIR to a temp location.
            orig = capture.OUT_DIR
            capture.OUT_DIR = Path(tmp) / "task-004B-ui-evidence"
            capture.OUT_DIR.mkdir(parents=True, exist_ok=True)
            try:
                rc = capture._finish(
                    failures=[],
                    captured=["home.html", "health.json"],
                    health_data={"ok": True},
                    proc=None,
                )
                self.assertEqual(rc, 0)
                notes = (capture.OUT_DIR / "evidence-notes.md").read_text()
                self.assertIn("home.html", notes)
                self.assertIn("health.json", notes)
            finally:
                capture.OUT_DIR = orig

    def test_finish_reports_failures(self) -> None:
        import tempfile

        with tempfile.TemporaryDirectory() as tmp:
            orig = capture.OUT_DIR
            capture.OUT_DIR = Path(tmp) / "ev"
            capture.OUT_DIR.mkdir(parents=True, exist_ok=True)
            try:
                rc = capture._finish(
                    failures=["bad route"],
                    captured=[],
                    health_data={},
                    proc=None,
                )
                self.assertEqual(rc, 1)
                notes = (capture.OUT_DIR / "evidence-notes.md").read_text()
                self.assertIn("bad route", notes)
            finally:
                capture.OUT_DIR = orig


if __name__ == "__main__":
    unittest.main()
