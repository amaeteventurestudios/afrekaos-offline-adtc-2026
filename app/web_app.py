"""AfrekaOS Offline local browser UI.

Standard-library-only HTTP server (http.server). Runs at http://127.0.0.1:8787.
No cloud, no external dependencies. Connects to retrieval-grounded inference.

Advisor submissions run as in-memory background jobs: POST /advisor/<name>
creates a job, starts a worker thread, and redirects (303) to /job/<id>. The
job page auto-refreshes every 3s while running. This keeps the UI responsive
during long (30-90s) local inference. Jobs live in memory only and are never
persisted to disk; full questions are never logged.

Run:
    AFREKAOS_QWEN_NO_THINK=1 python3 -m app.web_app
"""

from __future__ import annotations

import json
import os
import re
import secrets
import shutil
import sys
import threading
import time
import traceback
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import model_inference, retrieval, runtime_config  # noqa: E402
from app import web_templates as T  # noqa: E402

HOST = "127.0.0.1"
PORT = int(os.environ.get("AFREKAOS_WEB_PORT", "8787"))

DEFAULT_DAILY = (
    "A small shop has low sales, missing fast-moving stock, supplier delay, "
    "and more customers asking for credit. Give a short operating checklist."
)
DEFAULT_INVENTORY = (
    "I have two fast-moving items out of stock and a supplier that is delayed. "
    "What should I check, and how do I avoid overstocking slow-moving items?"
)
DEFAULT_CASHFLOW = (
    "Customers are asking for credit and my cash records are irregular. "
    "What should I check before extending credit, and what should I avoid?"
)

# Maps advisor path -> display heading.
ADVISOR_HEADINGS = {
    "/advisor/daily": "Daily Operations Advisor",
    "/advisor/inventory": "Inventory and Stock Check",
    "/advisor/cashflow": "Cashflow Pressure Coach",
}

# --- In-memory job store ----------------------------------------------------
# Jobs are kept only in process memory. Never persisted. Never logged in full.
# A small lock guards the dict; each job dict is also guarded on mutation.

_JOB_LOCK = threading.Lock()
_JOBS: dict[str, dict] = {}
# Soft cap so the dict cannot grow without bound. Older jobs evicted first.
_MAX_JOBS = 50


def _log(msg: str) -> None:
    """Best-effort server log line (stderr). Never logs full questions."""
    sys.stderr.write(f"[afrekaos] {msg}\n")
    sys.stderr.flush()


def _new_job(advisor: str, question: str) -> dict:
    """Create and register a new job dict. Returns the job."""
    job_id = secrets.token_hex(6)
    job = {
        "job_id": job_id,
        "advisor": advisor,
        # Truncate for safety in logs/state; full question kept only in memory
        # for the duration of the job and never written to disk.
        "question": question,
        "status": "queued",
        "step": 1,  # index into T.JOB_STEPS
        "answer": "",
        "error": "",
        "mode_label": "retrieval-grounded, direct-answer",
        "runtime_notes": "",
        "extraction_warning": "",
        "created_iso": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "created_epoch": time.time(),
    }
    with _JOB_LOCK:
        _JOBS[job_id] = job
        # Evict oldest if over cap.
        if len(_JOBS) > _MAX_JOBS:
            oldest = sorted(_JOBS.values(), key=lambda j: j["created_epoch"])
            for j in oldest[: len(_JOBS) - _MAX_JOBS]:
                _JOBS.pop(j["job_id"], None)
    return job


def _set_job(job_id: str, **fields) -> None:
    with _JOB_LOCK:
        j = _JOBS.get(job_id)
        if j is not None:
            j.update(fields)


def get_job(job_id: str):
    """Return a snapshot copy of a job, or None if unknown."""
    with _JOB_LOCK:
        j = _JOBS.get(job_id)
        return dict(j) if j is not None else None


# --- Status / health helpers -------------------------------------------------

def _llama_binary() -> str:
    """Best-effort llama binary name/path, or 'not detected'."""
    explicit = runtime_config.get_llama_binary()
    if explicit:
        return explicit
    for name in ("llama-completion", "llama-cli", "llama"):
        found = shutil.which(name)
        if found:
            return found
    return "not detected"


def _locked_candidate() -> str:
    lock_path = REPO_ROOT / "model.lock.json"
    if lock_path.is_file():
        try:
            return json.loads(lock_path.read_text()).get(
                "locked_candidate", "unknown"
            )
        except Exception:
            return "unknown"
    return "no model.lock.json"


def status_payload() -> dict:
    """Gather system status for the /status page."""
    model_path = runtime_config.get_model_path()
    db_path = REPO_ROOT / retrieval.DEFAULT_DB_PATH

    # Try retrieval summary without crashing.
    doc_count = "n/a"
    fts_status = "n/a"
    if db_path.is_file():
        try:
            s = retrieval.retrieval_summary()
            doc_count = s["documents"]
            fts_status = "available" if s.get("fts5") else "unavailable"
        except Exception:
            fts_status = "error reading index"

    return {
        "product": "AfrekaOS Offline",
        "model_lock": _locked_candidate(),
        "canonical_model_path": runtime_config.DEFAULT_MODEL_PATH,
        "model_path_exists": model_path.is_file(),
        "model_path_is_symlink": model_path.is_symlink(),
        "llama_binary_detected": _llama_binary(),
        "retrieval_index_exists": db_path.is_file(),
        "indexed_documents": doc_count,
        "sqlite_fts_status": fts_status,
        "qwen_direct_answer": (
            f"/no_think={os.environ.get('AFREKAOS_QWEN_NO_THINK', 'unset')}, "
            "template=templates/qwen3_nonthinking.jinja"
        ),
        "cloud_dependency": "none — fully local",
    }


def health_payload() -> dict:
    model_path = runtime_config.get_model_path()
    db_path = REPO_ROOT / retrieval.DEFAULT_DB_PATH
    return {
        "ok": True,
        "product": "AfrekaOS Offline",
        "model_exists": model_path.is_file(),
        "retrieval_index_exists": db_path.is_file(),
        "llama_binary": _llama_binary(),
        "locked_candidate": _locked_candidate(),
    }


# --- Inference through the UI -----------------------------------------------

def _status_detail() -> dict:
    """Return a status-detail dict for the runtime panel on job pages."""
    model_path = runtime_config.get_model_path()
    db_path = REPO_ROOT / retrieval.DEFAULT_DB_PATH
    return {
        "model_path_exists": model_path.is_file(),
        "llama_binary": _llama_binary(),
        "retrieval_index_exists": db_path.is_file(),
        "locked_candidate": _locked_candidate(),
        "mode": "local-only, no cloud",
    }


def _run_advisor_job(job_id: str, question: str) -> None:
    """Run grounded inference for a job in a background thread.

    Updates the job's status/step as it progresses. Never raises into the
    caller; failures are recorded on the job.
    """
    try:
        _log(f"Job {job_id}: building retrieval context")
        _set_job(job_id, status="running", step=2)

        # Ensure index exists (best-effort).
        db_path = REPO_ROOT / retrieval.DEFAULT_DB_PATH
        if not db_path.is_file():
            try:
                _set_job(job_id, step=2)
                retrieval.build_index()
            except Exception:
                pass

        _set_job(job_id, step=3)  # Retrieving SME context

        _set_job(job_id, step=4)  # Building grounded prompt

        _log(f"Job {job_id}: running local model")
        _set_job(job_id, step=5)  # Running local Qwen model
        result = model_inference.run_grounded(
            question,
            max_tokens=int(os.environ.get("AFREKAOS_UI_MAX_TOKENS", "256")),
            timeout_seconds=int(os.environ.get("AFREKAOS_UI_TIMEOUT", "150")),
        )

        _set_job(job_id, step=6)  # Formatting answer

        mode_label = "retrieval-grounded, direct-answer"
        if not result["ok"]:
            err = result.get("error", "unknown error")
            _log(f"Job {job_id}: failed: {err}")
            _set_job(
                job_id, status="failed", error=f"Could not run local inference: {err}",
                step=7,
            )
            return

        # The answer is extracted by run_model via the unified
        # extract_visible_answer() (app.model_inference), so clean_answer_chars
        # is exactly the length of the text we show the user.
        answer_text = result.get("clean_answer", "") or ""
        clean_chars = int(result.get("clean_answer_chars", 0) or 0)
        extraction_warning = result.get("extraction_warning", "") or ""
        if not answer_text:
            # Genuinely empty: never show a fabricated answer.
            answer_text = "(model produced no visible answer text)"

        # Optional bounded debug output (off by default; no private questions).
        if os.environ.get("AFREKAOS_DEBUG_OUTPUT", "") == "1":
            _write_debug_output(job_id, result)

        rc = result.get("return_code")
        notes_parts = [
            f"return_code={rc}",
            f"clean_answer_chars={clean_chars}",
            f"think_trap={result.get('think_trap', False)}",
        ]
        if extraction_warning:
            notes_parts.append(f"extraction_warning={extraction_warning}")
        notes = ", ".join(notes_parts)

        _log(f"Job {job_id}: completed")
        _set_job(
            job_id, status="complete", step=7, answer=answer_text,
            mode_label=mode_label, runtime_notes=notes,
            extraction_warning=extraction_warning,
        )
    except Exception as exc:  # pragma: no cover - defensive
        # Catch-all so the worker thread never dies silently. Do not expose a
        # long private traceback in the browser; log a short summary.
        _log(f"Job {job_id}: failed: {type(exc).__name__}: {exc}")
        _set_job(
            job_id, status="failed",
            error=f"Local runtime error: {type(exc).__name__}: {exc}",
            step=7,
        )


def _extract_answer(raw: str) -> str:
    """Pull the user-visible answer from raw llama-completion output.

    Delegates to the single source of truth (model_inference.extract_visible_answer)
    so the UI answer and visible_answer_chars can never disagree. Kept for
    backwards compatibility with existing tests/callers.
    """
    return model_inference.extract_visible_answer(raw)["clean_answer"]


# --- Optional bounded debug output (AFREKAOS_DEBUG_OUTPUT=1) ----------------
DEBUG_DIR = REPO_ROOT / "artifacts" / "eval" / "task-004D-debug"


def _write_debug_output(job_id: str, result: dict) -> None:
    """Write a small, bounded debug snapshot for the most recent job.

    Off by default (only when AFREKAOS_DEBUG_OUTPUT=1). Does NOT persist the
    user question. Files are capped in size so they stay small.
    """
    try:
        DEBUG_DIR.mkdir(parents=True, exist_ok=True)
        out_path = result.get("output_path")
        raw = ""
        if out_path and Path(out_path).is_file():
            raw = Path(out_path).read_text(encoding="utf-8", errors="replace")
        # Cap raw output to keep debug files small.
        raw_capped = raw[:4000]
        summary = {
            "job_id": job_id,
            "return_code": result.get("return_code"),
            "raw_stdout_chars": result.get("raw_stdout_chars", 0),
            "clean_answer_chars": result.get("clean_answer_chars", 0),
            "contains_think": result.get("contains_think", False),
            "think_trap": result.get("think_trap", False),
            "extraction_warning": result.get("extraction_warning", ""),
            "raw_head_chars": len(raw_capped),
        }
        import json as _json
        (DEBUG_DIR / f"{job_id}-summary.json").write_text(
            _json.dumps(summary, indent=2), encoding="utf-8"
        )
        (DEBUG_DIR / f"{job_id}-raw.txt").write_text(
            raw_capped, encoding="utf-8", errors="replace"
        )
    except Exception as exc:  # pragma: no cover - defensive
        _log(f"Job {job_id}: debug output failed: {exc}")


# --- HTTP handler ------------------------------------------------------------

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # quieter logging
        sys.stderr.write(
            "%s - - %s\n" % (self.address_string(), fmt % args)
        )

    def _send_html(self, code: int, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _send_json(self, code: int, body: str) -> None:
        encoded = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(encoded)))
        self.end_headers()
        self.wfile.write(encoded)

    def _redirect(self, location: str) -> None:
        self.send_response(303)
        self.send_header("Location", location)
        self.end_headers()

    def _error_page(self, route: str, exc: BaseException) -> None:
        """Render a browser-friendly error page. Full traceback to terminal
        only; a short summary to the browser."""
        summary = f"{type(exc).__name__}: {exc}" if exc else "Unknown error"
        traceback.print_exc()  # full detail to terminal logs only
        try:
            self._send_html(
                500, T.render_error(summary, route=route, detail=_status_detail())
            )
        except Exception:
            # Last-resort fallback if even rendering the error page fails.
            self._send_html(
                500,
                T._page(
                    "Error",
                    '<h2>AfrekaOS hit a local runtime error.</h2>'
                    f'<div class="err">{summary}</div>',
                ),
            )

    # --- GET routes ----------------------------------------------------------

    def do_GET(self) -> None:
        route = self.path.split("?")[0]
        try:
            if route == "/":
                self._send_html(200, T.render_home())
            elif route == "/demo":
                self._send_html(200, T.render_demo())
            elif route == "/advisor/daily":
                self._send_html(
                    200,
                    T.render_advisor_form(
                        "/advisor/daily",
                        "Daily Operations Advisor",
                        "Triage low sales, stockouts, supplier delays, and credit pressure.",
                        DEFAULT_DAILY,
                        "Describe your daily operations problem...",
                        active="daily",
                    ),
                )
            elif route == "/advisor/inventory":
                self._send_html(
                    200,
                    T.render_advisor_form(
                        "/advisor/inventory",
                        "Inventory and Stock Check",
                        "Check fast-moving items, slow stock, reorder points, and supplier lead times.",
                        DEFAULT_INVENTORY,
                        "Describe your inventory / stockout problem...",
                        active="daily",
                    ),
                )
            elif route == "/advisor/cashflow":
                self._send_html(
                    200,
                    T.render_advisor_form(
                        "/advisor/cashflow",
                        "Cashflow Pressure Coach",
                        "Reason through cash pressure, credit requests, and record gaps. Not accounting/banking/lending/tax/payroll advice.",
                        DEFAULT_CASHFLOW,
                        "Describe your cashflow / credit problem...",
                        active="daily",
                    ),
                )
            elif route.startswith("/job/"):
                self._handle_job_get(route)
            elif route == "/status":
                self._send_html(200, T.render_status(status_payload()))
            elif route == "/health":
                self._send_json(200, T.health_json(health_payload()))
            else:
                self._send_html(404, T._page("Not found", "<h2>404 — Not found</h2><p><a href=\"/\">Home</a></p>"))
        except Exception as exc:
            self._error_page(route, exc)

    def _handle_job_get(self, route: str) -> None:
        """GET /job/<id> — render progress/result page."""
        job_id = route[len("/job/"):].strip("/")
        if not job_id:
            self._send_html(
                404,
                T._page("Not found", "<h2>404 — Not found</h2><p><a href=\"/\">Home</a></p>"),
            )
            return
        job = get_job(job_id)
        if job is None:
            self._send_html(404, T.render_job_missing(job_id))
            return
        self._send_html(
            200, T.render_job(job, detail=_status_detail(), active="daily")
        )

    # --- POST routes ---------------------------------------------------------

    def do_POST(self) -> None:
        route = self.path.split("?")[0]
        try:
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw_body = self.rfile.read(length) if length else b""
            params = parse_qs(raw_body.decode("utf-8", errors="replace"))
            question = (params.get("question", [""])[0] or "").strip()

            heading = ADVISOR_HEADINGS.get(route)
            if heading is None:
                # Unknown POST target: go home.
                self._redirect("/")
                return

            _log(f"POST {route} received")

            if not question:
                # No question: redisplay the form with a note (no job created).
                self._send_html(
                    200,
                    T.render_advisor_result(
                        heading,
                        "(empty)",
                        "Please enter an operations question.",
                        "retrieval-grounded, direct-answer",
                        active="daily",
                    ),
                )
                return

            # Create a job and start a background worker. Redirect immediately.
            job = _new_job(heading, question)
            _log(f"Created job {job['job_id']}")
            t = threading.Thread(
                target=_run_advisor_job,
                args=(job["job_id"], question),
                daemon=True,
            )
            t.start()
            self._redirect(f"/job/{job['job_id']}")
        except Exception as exc:
            self._error_page(route, exc)


def main() -> int:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    print(f"AfrekaOS Offline local UI: http://{HOST}:{PORT}")
    print("Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
