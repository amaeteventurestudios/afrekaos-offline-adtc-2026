"""HTML rendering helpers for the AfrekaOS Offline local web UI.

Standard library only. No external CSS, JS, fonts, CDNs, or images. All user
content is escaped. Plain CSS is embedded in each page.
"""

from __future__ import annotations

import html
from typing import Optional

# --- Embedded CSS -----------------------------------------------------------

_CSS = """
:root { --bg:#0f1115; --card:#1a1d24; --accent:#4ade80; --text:#e5e7eb;
        --muted:#9ca3af; --warn:#fbbf24; --err:#f87171; --border:#2d3139;
        --banner:#15201a; }
* { box-sizing:border-box; }
body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,
       Helvetica,Arial,sans-serif; background:var(--bg); color:var(--text);
       line-height:1.6; }
.container { max-width:900px; margin:0 auto; padding:1.5rem 1rem 4rem; }
header { border-bottom:1px solid var(--border); padding-bottom:1rem; margin-bottom:1rem; }
header h1 { margin:0; font-size:1.5rem; }
header .tagline { color:var(--muted); font-size:.9rem; }
.banner { background:var(--banner); border:1px solid var(--accent);
          border-radius:10px; padding:.6rem 1rem; margin-bottom:1.2rem;
          display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; }
.banner .b-item { font-size:.78rem; color:var(--accent); }
.banner .b-mark { font-weight:700; margin-right:.2rem; }
.banner .b-sep { color:var(--muted); font-size:.78rem; }
nav.topnav { display:flex; flex-wrap:wrap; gap:.7rem; margin-bottom:1.5rem;
             font-size:.88rem; }
nav.topnav a { color:var(--muted); }
nav.topnav a:hover { color:var(--accent); }
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }
.cards { display:grid; gap:.9rem; grid-template-columns:1fr; }
@media(min-width:600px){ .cards{ grid-template-columns:1fr 1fr; } }
.card { background:var(--card); border:1px solid var(--border); border-radius:10px;
        padding:1.2rem; transition:border-color .15s; }
.card:hover { border-color:var(--accent); }
.card h2 { margin:0 0 .3rem; font-size:1.1rem; }
.card h2 a { color:var(--text); }
.card p { margin:0; color:var(--muted); font-size:.88rem; }
.card .card-tag { display:inline-block; font-size:.7rem; color:var(--accent);
                  border:1px solid var(--accent); border-radius:99px;
                  padding:.05rem .5rem; margin-bottom:.5rem; }
form { background:var(--card); border:1px solid var(--border); border-radius:10px;
       padding:1.2rem; margin-bottom:1.5rem; }
textarea { width:100%; min-height:110px; background:#0b0d11; color:var(--text);
           border:1px solid var(--border); border-radius:8px; padding:.7rem;
           font-size:.95rem; resize:vertical; }
textarea:focus { outline:none; border-color:var(--accent); }
select { width:100%; background:#0b0d11; color:var(--text); border:1px solid var(--border);
         border-radius:8px; padding:.55rem; font-size:.95rem; margin-top:.3rem; }
select:focus { outline:none; border-color:var(--accent); }
button { background:var(--accent); color:#06120c; border:none; border-radius:8px;
         padding:.6rem 1.2rem; font-size:.95rem; font-weight:600; cursor:pointer;
         margin-top:.7rem; }
button:hover { filter:brightness(1.1); }
section.result { background:var(--card); border:1px solid var(--border);
                 border-radius:10px; padding:1.2rem; margin-bottom:1.2rem;
                 white-space:pre-wrap; word-wrap:break-word; }
.label { color:var(--muted); font-size:.78rem; text-transform:uppercase;
         letter-spacing:.05em; margin-bottom:.3rem; }
.warn { background:rgba(251,191,36,.1); border:1px solid var(--warn);
        color:var(--warn); border-radius:8px; padding:.7rem 1rem; font-size:.85rem;
        margin-bottom:1rem; }
.err { background:rgba(248,113,113,.1); border:1px solid var(--err);
       color:var(--err); border-radius:8px; padding:.7rem 1rem; font-size:.85rem;
       margin-bottom:1rem; }
.meta { color:var(--muted); font-size:.82rem; margin-top:.8rem; }
.status-grid { display:grid; gap:.5rem; }
.status-grid .row { display:flex; justify-content:space-between; gap:1rem;
                    border-bottom:1px solid var(--border); padding:.4rem 0; }
.status-grid .row .k { color:var(--muted); }
.status-grid .row .v { font-family:monospace; text-align:right; }
.pill { display:inline-block; padding:.1rem .5rem; border-radius:99px; font-size:.75rem; }
.pill.ok { background:rgba(74,222,128,.15); color:var(--accent); }
.pill.no { background:rgba(248,113,113,.15); color:var(--err); }
.result-nav { display:flex; flex-wrap:wrap; gap:1rem; margin-top:1rem; font-size:.88rem; }
ol.steps { list-style:none; padding-left:0; margin:.4rem 0 1rem; }
ol.steps li { padding:.35rem .6rem; border-radius:6px; margin-bottom:.3rem;
              font-size:.88rem; border:1px solid var(--border); }
ol.steps li.step-done { color:var(--muted); }
ol.steps li.step-current { color:var(--accent); border-color:var(--accent);
                           font-weight:600; }
ol.steps li.step-todo { color:var(--muted); opacity:.6; }
footer { margin-top:2rem; color:var(--muted); font-size:.8rem;
         border-top:1px solid var(--border); padding-top:1rem; }
"""

# The unified boundary warning text used on every advisor result.
WARNING_TEXT = (
    "AfrekaOS provides operational guidance only. It is not accounting, "
    "banking, payroll, tax, lending, or ERP software."
)

# Loading message shown client-side when an advisor form is submitted.
LOADING_MESSAGE = (
    "AfrekaOS received your question. It is building local retrieval context "
    "and running the local model. This can take 30 to 90 seconds on CPU-only "
    "hardware."
)
LOADING_BUTTON_TEXT = "Running local model..."

# Ordered progress steps shown on the job page. A job stores a 1-based index
# into this list as its current step.
JOB_STEPS = [
    "Request received",
    "Building local retrieval index",
    "Retrieving SME context",
    "Building grounded prompt",
    "Running local Qwen model",
    "Formatting answer",
    "Complete",
]


def _loading_script(button_id: str = "submitBtn") -> str:
    """Inline JS that disables the submit button and shows a loading message.

    No external files or dependencies. If JavaScript is disabled, the form
    submits normally as a plain POST. The script is intentionally tiny.
    """
    return (
        "<script>\n"
        "(function(){\n"
        f"  var btn = document.getElementById({button_id!r});\n"
        "  if(!btn || !btn.form){ return; }\n"
        "  btn.form.addEventListener('submit', function(){\n"
        f"    btn.disabled = true;\n"
        f"    btn.textContent = {_esc(LOADING_BUTTON_TEXT)!r};\n"
        "    var msg = document.getElementById('loadingMsg');\n"
        "    if(msg){ msg.style.display = 'block'; }\n"
        "  });\n"
        "})();\n"
        "</script>\n"
    )


def _language_selector(selected: str = "en") -> str:
    """Render a language <select> for advisor/demo forms.

    Works without JavaScript (plain form POST). Uses name="language". Defaults
    to English. Imported lazily so the template module stays import-safe even
    before language_mode is fully wired.
    """
    from app import language_mode as lm
    langs = lm.get_supported_languages()
    options = []
    for code in sorted(langs):
        v = langs[code]
        sel = " selected" if code == selected else ""
        options.append(
            f'<option value="{code}"{sel}>{_esc(v["label"])}</option>'
        )
    return (
        '<div class="label">Response language</div>\n'
        '<select name="language">\n'
        + "\n".join(options) + "\n"
        "</select>\n"
    )


def _esc(s: object) -> str:
    """HTML-escape a value."""
    return html.escape(str(s), quote=True)


def _topnav(active: str = "") -> str:
    """Render the top navigation bar."""
    links = [
        ("/", "Mission Control", "home"),
        ("/demo", "Demo Scenarios", "demo"),
        ("/advisor/daily", "Daily Advisor", "daily"),
        ("/status", "Offline Status", "status"),
    ]
    items = []
    for href, label, key in links:
        cls = ' style="color:var(--accent);font-weight:600;"' if key == active else ""
        items.append(f'<a href="{href}"{cls}>{_esc(label)}</a>')
    return '<nav class="topnav">' + "\n".join(items) + "</nav>\n"


def _banner() -> str:
    """Render the offline status banner.

    The marker is explicit text in the HTML (\u2713 = checkmark), not a CSS
    pseudo-element, so it never renders as a stray "13" if a renderer mishandles
    a CSS Unicode escape. Each item reads "OK <label>" if rendered without the
    checkmark glyph.
    """
    mark = "\u2713"  # U+2713 CHECK MARK
    items = [
        "Offline mode",
        "Local model",
        "SQLite retrieval",
        "No cloud dependency",
    ]
    parts = []
    for i, label in enumerate(items):
        if i > 0:
            parts.append('<span class="b-sep">\u00b7</span>')
        parts.append(
            f'<span class="b-item"><span class="b-mark">{mark}</span>'
            f"{_esc(label)}</span>"
        )
    return '<div class="banner">' + "".join(parts) + "</div>\n"


def _page(title: str, body: str, active: str = "",
          head_extra: str = "") -> str:
    """Wrap body in a full HTML document with embedded CSS."""
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"{head_extra}"
        f"<title>{_esc(title)}</title>\n"
        f"<style>{_CSS}</style>\n"
        "</head>\n<body>\n"
        '<div class="container">\n'
        f"<header><h1>AfrekaOS Offline</h1>"
        '<div class="tagline">Offline SME operations copilot</div></header>\n'
        f"{_banner()}"
        f"{_topnav(active)}"
        f"{body}\n"
        "<footer>AfrekaOS Offline — local-only. No cloud. "
        "Operational guidance, not accounting/banking/payroll/tax/ERP software."
        "</footer>\n"
        "</div>\n</body>\n</html>\n"
    )


# --- Page renderers ---------------------------------------------------------

def render_home() -> str:
    cards = [
        ("/advisor/daily", "Daily Operations Advisor", "advisor",
         "Triage low sales, stockouts, supplier delays, and credit pressure."),
        ("/advisor/inventory", "Inventory and Stock Check", "advisor",
         "Check fast-moving items, slow stock, reorder points, and supplier lead times."),
        ("/advisor/cashflow", "Cashflow Pressure Coach", "advisor",
         "Reason through cash pressure, credit requests, and record gaps."),
        ("/demo", "Demo Scenarios", "demo",
         "Ready-made SME operations scenarios you can run with one click."),
        ("/status", "Offline System Status", "status",
         "Model lock, retrieval index, runtime, and offline status."),
    ]
    card_html = "\n".join(
        f'<div class="card"><span class="card-tag">{_esc(tag)}</span>'
        f'<h2><a href="{href}">{_esc(name)}</a></h2>'
        f"<p>{_esc(desc)}</p></div>"
        for href, name, tag, desc in cards
    )
    body = (
        '<h2 style="margin-top:0">Mission Control</h2>\n'
        f'<div class="cards">\n{card_html}\n</div>\n'
        '<p class="meta">Choose a coach above to reason through a daily '
        "operations question. Answers are retrieval-grounded and local-only.</p>\n"
    )
    return _page("Mission Control", body, active="home")


def render_advisor_form(
    action: str,
    heading: str,
    description: str,
    default_question: str,
    placeholder: str = "",
    active: str = "",
) -> str:
    body = (
        f'<h2 style="margin-top:0">{_esc(heading)}</h2>\n'
        f"<p class=\"meta\">{_esc(description)}</p>\n"
        f'<form method="POST" action="{_esc(action)}">\n'
        f'<div class="label">Your operations question</div>\n'
        f'<textarea name="question" placeholder="{_esc(placeholder)}">'
        f"{_esc(default_question)}</textarea>\n"
        f"{_language_selector()}"
        '<button id="submitBtn" type="submit">Get operating guidance</button>\n'
        f'<div id="loadingMsg" class="meta" style="display:none;'
        f'margin-top:.8rem;">{_esc(LOADING_MESSAGE)}</div>\n'
        "</form>\n"
        f"{_loading_script()}"
    )
    return _page(heading, body, active=active)


def render_advisor_result(
    heading: str,
    question: str,
    answer: str,
    mode_label: str,
    runtime_notes: str = "",
    error: Optional[str] = None,
    active: str = "",
) -> str:
    parts = [f'<h2 style="margin-top:0">{_esc(heading)}</h2>\n']

    parts.append(f'<div class="warn">{_esc(WARNING_TEXT)}</div>\n')

    if error:
        parts.append(f'<div class="err">{_esc(error)}</div>\n')

    parts.append('<div class="label">Your question</div>\n')
    parts.append(f"<section class=\"result\">{_esc(question)}</section>\n")

    parts.append(
        f'<div class="label">Operating guidance ({_esc(mode_label)})</div>\n'
    )
    parts.append(f'<section class="result">{_esc(answer)}</section>\n')

    if runtime_notes:
        parts.append('<div class="label">Runtime summary</div>\n')
        parts.append(f'<section class="result">{_esc(runtime_notes)}</section>\n')

    parts.append(
        '<div class="result-nav">'
        '<a href="/">&#8592; Mission Control</a>'
        '<a href="/demo">Demo Scenarios</a>'
        '<a href="/status">Offline Status</a>'
        "</div>\n"
    )
    return _page(heading, "".join(parts), active=active)


def _pill(ok: bool, text: str) -> str:
    cls = "ok" if ok else "no"
    return f'<span class="pill {cls}">{_esc(text)}</span>'


def render_status(status: dict) -> str:
    rows = []
    for key, val in status.items():
        if isinstance(val, bool):
            val_html = _pill(val, "yes" if val else "no")
        else:
            val_html = f'<span class="v">{_esc(val)}</span>'
        rows.append(
            f'<div class="row"><span class="k">{_esc(key)}</span>{val_html}</div>'
        )
    body = (
        '<h2 style="margin-top:0">Offline System Status</h2>\n'
        f'<div class="status-grid">\n{"".join(rows)}\n</div>\n'
        '<div class="result-nav">'
        '<a href="/">&#8592; Mission Control</a>'
        '<a href="/demo">Demo Scenarios</a>'
        "</div>\n"
    )
    return _page("Offline System Status", body, active="status")


# --- Demo scenarios ---------------------------------------------------------

# Each scenario: (title, advisor_action, advisor_name, prompt)
DEMO_SCENARIOS = [
    (
        "Low sales, stockout, supplier delay",
        "/advisor/daily",
        "Daily Operations Advisor",
        "A small shop has lower sales than usual, two fast-moving items are "
        "out of stock, the supplier delivery is delayed, and more customers "
        "are asking for credit. Give a short operating checklist.",
    ),
    (
        "Expansion readiness",
        "/advisor/daily",
        "Daily Operations Advisor",
        "A market operator wants to expand from one location to two locations "
        "but has irregular cash records, one trusted staff member, seasonal "
        "customer demand, and limited working capital. What should they check "
        "before expanding?",
    ),
    (
        "Inventory pressure",
        "/advisor/inventory",
        "Inventory and Stock Check",
        "A small retailer has too much slow-moving stock, three fast-moving "
        "items are almost finished, and supplier lead times have become "
        "unreliable. What should the operator do this week?",
    ),
    (
        "Cash pressure and customer credit",
        "/advisor/cashflow",
        "Cashflow Pressure Coach",
        "A small business has cash pressure, more customers asking to buy on "
        "credit, unpaid balances from last month, and upcoming supplier "
        "payments. What should the owner review before accepting more credit "
        "sales?",
    ),
]


def render_demo() -> str:
    cards = []
    for i, (title, action, advisor, prompt) in enumerate(DEMO_SCENARIOS, 1):
        btn_id = f"demoBtn{i}"
        cards.append(
            f'<div class="card">'
            f'<span class="card-tag">Scenario {i}</span>'
            f"<h2>{_esc(title)}</h2>"
            f'<p><em>{_esc(advisor)}</em></p>'
            f'<p>{_esc(prompt)}</p>'
            f'<form method="POST" action="{_esc(action)}">'
            f'<textarea name="question" style="display:none;">{_esc(prompt)}</textarea>'
            f"{_language_selector()}"
            f'<button id="{btn_id}" type="submit">Run this scenario</button>'
            f'<div id="loadingMsg{i}" class="meta" style="display:none;'
            f'margin-top:.6rem;font-size:.8rem;">{_esc(LOADING_MESSAGE)}</div>'
            f"</form>"
            f"</div>"
        )
    # One small script that wires up every demo button by id.
    wire = "".join(
        f"  _wire('demoBtn{i}','loadingMsg{i}');\n"
        for i in range(1, len(DEMO_SCENARIOS) + 1)
    )
    script = (
        "<script>\n"
        "(function(){\n"
        "  function _wire(btnId, msgId){\n"
        "    var btn = document.getElementById(btnId);\n"
        "    if(!btn || !btn.form){ return; }\n"
        "    btn.form.addEventListener('submit', function(){\n"
        f"      btn.disabled = true;\n"
        f"      btn.textContent = {_esc(LOADING_BUTTON_TEXT)!r};\n"
        "      var msg = document.getElementById(msgId);\n"
        "      if(msg){ msg.style.display = 'block'; }\n"
        "    });\n"
        "  }\n"
        f"{wire}"
        "})();\n"
        "</script>\n"
    )
    body = (
        '<h2 style="margin-top:0">Demo Scenarios</h2>\n'
        '<p class="meta">Ready-made SME operations scenarios. Click '
        '"Run this scenario" to submit the prompt to the matching advisor. '
        "Answers are retrieval-grounded and local-only.</p>\n"
        f'<div class="cards">\n{"".join(cards)}\n</div>\n'
        f"{script}"
        '<div class="result-nav">'
        '<a href="/">&#8592; Mission Control</a>'
        '<a href="/status">Offline Status</a>'
        "</div>\n"
    )
    return _page("Demo Scenarios", body, active="demo")


def health_json(payload: dict) -> str:
    """Serialize a health dict to JSON (for the /health route)."""
    import json

    return json.dumps(payload, indent=2)


def _status_detail_panel(detail: dict) -> str:
    """Render the small status-detail panel used on job pages.

    Keys (all optional, booleans rendered as yes/no pills):
      model_path_exists, llama_binary, retrieval_index_exists,
      locked_candidate, mode
    """
    rows = []

    def _row(k: str, v) -> str:
        if isinstance(v, bool):
            v_html = _pill(v, "yes" if v else "no")
        else:
            v_html = f'<span class="v">{_esc(v)}</span>'
        return f'<div class="row"><span class="k">{_esc(k)}</span>{v_html}</div>'

    rows.append(_row("Model path exists",
                     detail.get("model_path_exists", "not available")))
    rows.append(_row("Llama binary",
                     detail.get("llama_binary", "not detected")))
    rows.append(_row("Retrieval index",
                     detail.get("retrieval_index_exists", "not available")))
    rows.append(_row("Locked candidate",
                     detail.get("locked_candidate", "unknown")))
    rows.append(_row("Retrieval-grounded",
                     detail.get("retrieval_grounded", True)))
    rows.append(_row("Direct-answer mode",
                     detail.get("direct_answer", True)))
    rows.append(_row("Local-only", detail.get("local_only", True)))
    return (
        '<section class="result" style="margin-top:1rem;">'
        '<div class="label">Runtime status</div>'
        f'<div class="status-grid">{"".join(rows)}</div>'
        "</section>\n"
    )


def render_job(
    job: dict,
    detail: Optional[dict] = None,
    active: str = "",
) -> str:
    """Render the job progress/result page.

    job keys:
      job_id, advisor, status ('queued'|'running'|'complete'|'failed'),
      step (1-based index into JOB_STEPS), question, answer, error,
      mode_label, runtime_notes, created_iso
    """
    status = job.get("status", "queued")
    step = int(job.get("step", 1))
    steps = JOB_STEPS
    # Clamp step index into range for display.
    disp_step = max(1, min(step, len(steps)))

    parts = [f'<h2 style="margin-top:0">{_esc(job.get("advisor", "Advisor"))}</h2>\n']

    # Status pill.
    status_pill = {
        "queued": _pill(True, "queued"),
        "running": _pill(True, "running"),
        "complete": _pill(True, "complete"),
        "failed": _pill(False, "failed"),
    }.get(status, _pill(False, status))
    parts.append(
        f'<div class="label">Job {job.get("job_id", "")} · {status_pill}</div>\n'
    )

    # Response language (if set on the job).
    lang_label = job.get("language_label")
    if lang_label:
        parts.append(
            f'<p class="meta">Response language: <strong>{_esc(lang_label)}</strong></p>\n'
        )

    # Step list with current highlighted.
    parts.append('<ol class="steps">\n')
    for i, label in enumerate(steps, 1):
        cls = "step-done" if i < disp_step else (
            "step-current" if i == disp_step else "step-todo"
        )
        parts.append(f'<li class="{cls}">{_esc(label)}</li>\n')
    parts.append("</ol>\n")

    # Runtime message while in progress.
    if status in ("queued", "running"):
        parts.append(
            '<div class="warn">Local inference may take 30 to 90 seconds on '
            "CPU-only hardware.</div>\n"
        )

    # The question (demo only; still escaped).
    q = job.get("question", "")
    if q:
        parts.append('<div class="label">Your question</div>\n')
        parts.append(f'<section class="result">{_esc(q)}</section>\n')

    # Answer or error.
    if status == "complete":
        parts.append('<div class="label">Operating Guidance</div>\n')
        answer = job.get("answer", "") or "(model produced no visible answer text)"
        parts.append(f'<section class="result">{_esc(answer)}</section>\n')
        # Prompt-echo note: if the echoed prompt was stripped, tell the user.
        if job.get("prompt_echo_stripped", False):
            parts.append(
                '<div class="meta" style="margin-top:.4rem;">Prompt echo removed '
                "from display.</div>\n"
            )
        # Extraction warning (if any) — shown only when the extractor flagged
        # something worth noting (e.g. an unclosed <think> block).
        warn = job.get("extraction_warning", "")
        if warn:
            parts.append(
                f'<div class="warn">{_esc(warn)}</div>\n'
            )
        parts.append('<div class="warn">{}</div>\n'.format(_esc(WARNING_TEXT)))
        notes = job.get("runtime_notes", "")
        if notes:
            parts.append('<div class="label">Runtime summary</div>\n')
            parts.append(f'<section class="result">{_esc(notes)}</section>\n')
    elif status == "failed":
        err = job.get("error", "Unknown error")
        parts.append(
            '<div class="err">AfrekaOS hit a local runtime error while running '
            "this job.</div>\n"
        )
        parts.append('<div class="label">Error summary</div>\n')
        parts.append(f'<section class="result">{_esc(err)}</section>\n')

    # Status detail panel.
    if detail:
        parts.append(_status_detail_panel(detail))

    parts.append(
        '<div class="result-nav">'
        '<a href="/">&#8592; Mission Control</a>'
        '<a href="/advisor/daily">Daily Advisor</a>'
        '<a href="/status">Offline Status</a>'
        "</div>\n"
    )

    # Auto-refresh while in progress.
    head_extra = ""
    if status in ("queued", "running"):
        head_extra = '<meta http-equiv="refresh" content="3">\n'

    return _page("Advisor result", "".join(parts), active=active,
                 head_extra=head_extra)


def render_error(
    summary: str,
    route: str = "",
    detail: Optional[dict] = None,
) -> str:
    """Browser-friendly error page. Does not expose long private tracebacks."""
    parts = ['<h2 style="margin-top:0">AfrekaOS hit a local runtime error.</h2>\n']
    parts.append(f'<div class="err">{_esc(summary)}</div>\n')
    if route:
        parts.append(
            f'<p class="meta">Current route: <code>{_esc(route)}</code></p>\n'
        )
    parts.append('<div class="label">Suggested checks</div>\n')
    parts.append(
        "<section class=\"result\">"
        "<ul>"
        "<li>Is <code>model/afrekaos.gguf</code> present?</li>"
        "<li>Is <code>llama-completion</code> available?</li>"
        "<li>Did the request time out?</li>"
        "<li>Check terminal logs for details.</li>"
        "</ul>"
        "</section>\n"
    )
    if detail:
        parts.append(_status_detail_panel(detail))
    parts.append(
        '<div class="result-nav">'
        '<a href="/">&#8592; Mission Control</a>'
        '<a href="/advisor/daily">Daily Advisor</a>'
        '<a href="/status">Offline Status</a>'
        "</div>\n"
    )
    return _page("Error", "".join(parts))


def render_job_missing(job_id: str) -> str:
    """Page shown when a job id is unknown (expired or invalid)."""
    parts = [
        '<h2 style="margin-top:0">Job not found</h2>\n',
        f'<div class="err">Job <code>{_esc(job_id)}</code> was not found. It may '
        "have expired (jobs are kept in memory only).</div>\n",
        '<div class="result-nav">'
        '<a href="/">&#8592; Mission Control</a>'
        '<a href="/advisor/daily">Daily Advisor</a>'
        '<a href="/status">Offline Status</a>'
        "</div>\n",
    ]
    return _page("Job not found", "".join(parts))


__all__ = [
    "WARNING_TEXT",
    "LOADING_MESSAGE",
    "LOADING_BUTTON_TEXT",
    "JOB_STEPS",
    "DEMO_SCENARIOS",
    "render_home",
    "render_advisor_form",
    "render_advisor_result",
    "render_status",
    "render_demo",
    "render_job",
    "render_error",
    "render_job_missing",
    "health_json",
]
