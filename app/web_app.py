"""AfrekaOS Offline local browser UI.

Standard-library-only HTTP server (http.server). Runs at http://127.0.0.1:8787.
No cloud, no external dependencies. Connects to retrieval-grounded inference.

Run:
    AFREKAOS_QWEN_NO_THINK=1 python3 -m app.web_app
"""

from __future__ import annotations

import json
import os
import re
import shutil
import sys
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from app import model_inference, retrieval, runtime_config  # noqa: E402
from app import web_templates as T  # noqa: E402

HOST = "127.0.0.1"
PORT = 8787

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

def _run_advisor(
    question: str,
) -> tuple[str, str, str]:
    """Run grounded inference for an advisor question.

    Returns (answer_text, mode_label, runtime_notes).
    Handles missing model/binary gracefully with a browser-friendly message
    folded into answer_text.
    """
    # Ensure index exists (best-effort).
    db_path = REPO_ROOT / retrieval.DEFAULT_DB_PATH
    if not db_path.is_file():
        try:
            retrieval.build_index()
        except Exception:
            pass

    result = model_inference.run_grounded(
        question,
        max_tokens=int(os.environ.get("AFREKAOS_UI_MAX_TOKENS", "256")),
        timeout_seconds=int(os.environ.get("AFREKAOS_UI_TIMEOUT", "150")),
    )

    mode_label = "retrieval-grounded, direct-answer"
    notes = ""

    if not result["ok"]:
        err = result.get("error", "unknown error")
        return (
            f"Could not run local inference: {err}",
            mode_label,
            notes,
        )

    # Extract the visible answer from the output file if present.
    out_path = result.get("output_path")
    answer_text = ""
    if out_path and Path(out_path).is_file():
        raw = Path(out_path).read_text(encoding="utf-8", errors="replace")
        answer_text = _extract_answer(raw)
    if not answer_text:
        answer_text = "(model produced no visible answer text)"

    # Light runtime notes.
    rc = result.get("return_code")
    notes = (
        f"return_code={rc}, visible_chars={result.get('visible_answer_chars', 0)}, "
        f"think_trap={result.get('contains_think', False)}"
    )
    return answer_text, mode_label, notes


def _extract_answer(raw: str) -> str:
    """Pull the user-visible answer from raw llama-completion output.

    Strips <think> blocks, llama.cpp log lines, and echoed prompt headers.
    """
    out = re.sub(r"<think>.*?</think>", "", raw, flags=re.DOTALL)
    out = re.sub(r"<think>.*", "", out, flags=re.DOTALL)
    lines = []
    for ln in out.splitlines():
        s = ln.strip()
        if not s:
            continue
        if re.match(r"^\d+\.\d+\.\d+\.\d+\s+", ln):
            continue
        if re.match(r"^[IWL]\s+", s):
            continue
        if re.match(
            r"^(?:repeat_last_n|dry_|top_k|top_p|min_p|xtc_|typical_p|"
            r"top_n_sigma|mirostat|adaptive_|frequency_penalty|"
            r"presence_penalty|repeat_penalty|sampler|generate|llama_|"
            r"common_|chat template|interactive|Press|To return|"
            r"If you want|Not using|system_info|system prompt|"
            r"warming up|threadpool|backend init|fitting params|"
            r"control-looking|load the model|llama_completion)",
            s,
            re.IGNORECASE,
        ):
            continue
        lines.append(ln)
    return "\n".join(lines).strip()


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

    # --- GET routes ----------------------------------------------------------

    def do_GET(self) -> None:
        try:
            path = self.path.split("?")[0]
            if path == "/":
                self._send_html(200, T.render_home())
            elif path == "/demo":
                self._send_html(200, T.render_demo())
            elif path == "/advisor/daily":
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
            elif path == "/advisor/inventory":
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
            elif path == "/advisor/cashflow":
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
            elif path == "/status":
                self._send_html(200, T.render_status(status_payload()))
            elif path == "/health":
                self._send_json(200, T.health_json(health_payload()))
            else:
                self._send_html(404, T._page("Not found", "<h2>404 — Not found</h2><p><a href=\"/\">Home</a></p>"))
        except Exception:
            traceback.print_exc()
            self._send_html(500, T._page("Error", "<h2>500 — Server error</h2>"))

    # --- POST routes ---------------------------------------------------------

    def do_POST(self) -> None:
        try:
            path = self.path.split("?")[0]
            length = int(self.headers.get("Content-Length", 0) or 0)
            raw_body = self.rfile.read(length) if length else b""
            params = parse_qs(raw_body.decode("utf-8", errors="replace"))
            question = (params.get("question", [""])[0] or "").strip()

            if path == "/advisor/daily":
                heading = "Daily Operations Advisor"
            elif path == "/advisor/inventory":
                heading = "Inventory and Stock Check"
            elif path == "/advisor/cashflow":
                heading = "Cashflow Pressure Coach"
            else:
                self._redirect("/")
                return

            if not question:
                # No question: redisplay the form with a note.
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

            answer, mode_label, notes = _run_advisor(question)
            self._send_html(
                200,
                T.render_advisor_result(
                    heading, question, answer, mode_label, runtime_notes=notes,
                    active="daily",
                ),
            )
        except Exception:
            traceback.print_exc()
            self._send_html(500, T._page("Error", "<h2>500 — Server error</h2>"))


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
