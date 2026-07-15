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
.langswitch { display:inline-block; margin-left:auto; }
.langswitch-label { font-size:.78rem; color:var(--muted); }
.langswitch select { width:auto; display:inline-block; font-size:.8rem;
                     padding:.25rem .5rem; margin-top:0; }
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


def _language_selector(selected: str = "en",
                       label_text: str = "Response language") -> str:
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
        f'<div class="label">{_esc(label_text)}</div>\n'
        '<select name="language">\n'
        + "\n".join(options) + "\n"
        "</select>\n"
    )


def _global_lang_selector(language: str = "en") -> str:
    """A compact language switcher that appears in the header on every page.

    Uses a small <form> with GET so it works without JavaScript; the browser
    auto-submits via the onchange inline handler if JS is on. Links elsewhere
    preserve ?lang= via _url_with_lang.
    """
    from app import language_mode as lm
    langs = lm.get_supported_languages()
    options = []
    for code in sorted(langs):
        v = langs[code]
        sel = " selected" if code == language else ""
        options.append(f'<option value="{code}"{sel}>{_esc(v["label"])}</option>')
    label = lm.get_ui_text("select_language", language)
    return (
        '<form class="langswitch" method="get" action="/" style="margin:0;">'
        f'<label class="langswitch-label">{_esc(label)}: </label>'
        '<select name="lang" onchange="this.form.submit()">'
        + "\n".join(options) +
        "</select></form>"
    )


def _esc(s: object) -> str:
    """HTML-escape a value."""
    return html.escape(str(s), quote=True)


def _url_with_lang(path: str, language: str = "en") -> str:
    """Append ?lang=<code> to a path if the language is not English."""
    from app import language_mode as lm
    code = lm.normalize_language_code(language)
    if code == "en":
        return path
    sep = "&" if "?" in path else "?"
    return f"{path}{sep}lang={code}"


def _topnav(active: str = "", language: str = "en") -> str:
    """Render the top navigation bar (localized, lang preserved in links)."""
    from app import language_mode as lm
    L = lm.get_ui_bundle(language)
    links = [
        ("/", L["mission_control"], "home"),
        ("/demo", L["demo_scenarios"], "demo"),
        ("/advisor/daily", L["daily_advisor"], "daily"),
        ("/status", L["offline_status"], "status"),
    ]
    items = []
    for href, label, key in links:
        cls = ' style="color:var(--accent);font-weight:600;"' if key == active else ""
        href_l = _url_with_lang(href, language)
        items.append(f'<a href="{href_l}"{cls}>{_esc(label)}</a>')
    return '<nav class="topnav">' + "\n".join(items) + "</nav>\n"


def _banner(language: str = "en") -> str:
    """Render the offline status banner (localized).

    The marker is explicit text in the HTML (\u2713 = checkmark), not a CSS
    pseudo-element, so it never renders as a stray "13" if a renderer mishandles
    a CSS Unicode escape.
    """
    from app import language_mode as lm
    L = lm.get_ui_bundle(language)
    mark = "\u2713"  # U+2713 CHECK MARK
    items = [L["offline_mode"], L["local_model"], L["sqlite_retrieval"],
             L["no_cloud_dependency"]]
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
          head_extra: str = "", language: str = "en") -> str:
    """Wrap body in a full HTML document with embedded CSS (localized chrome)."""
    from app import language_mode as lm
    L = lm.get_ui_bundle(language)
    code = lm.normalize_language_code(language)
    return (
        "<!DOCTYPE html>\n"
        f'<html lang="{code}">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
        f"{head_extra}"
        f"<title>{_esc(title)}</title>\n"
        f"<style>{_CSS}</style>\n"
        "</head>\n<body>\n"
        '<div class="container">\n'
        f"<header><h1>{_esc(L['product'])}</h1>"
        f'<div class="tagline">{_esc(L["tagline"])}</div>'
        f"{_global_lang_selector(language)}</header>\n"
        f"{_banner(language)}"
        f"{_topnav(active, language)}"
        f"{body}\n"
        f"<footer>{_esc(L['footer'])}</footer>\n"
        "</div>\n</body>\n</html>\n"
    )


# --- Page renderers ---------------------------------------------------------

def render_home(language: str = "en") -> str:
    from app import language_mode as lm
    L = lm.get_ui_bundle(language)
    cards = [
        ("/advisor/daily", L["daily_operations_advisor"], "advisor",
         "Triage low sales, stockouts, supplier delays, and credit pressure."),
        ("/advisor/inventory", L["inventory_and_stock_check"], "advisor",
         "Check fast-moving items, slow stock, reorder points, and supplier lead times."),
        ("/advisor/cashflow", L["cashflow_pressure_coach"], "advisor",
         "Reason through cash pressure, credit requests, and record gaps."),
        ("/demo", L["demo_scenarios"], "demo",
         L["demo_intro"]),
        ("/status", L["offline_system_status"], "status",
         "Model lock, retrieval index, runtime, and offline status."),
    ]
    card_html = "\n".join(
        f'<div class="card"><span class="card-tag">{_esc(tag)}</span>'
        f'<h2><a href="{_url_with_lang(href, language)}">{_esc(name)}</a></h2>'
        f"<p>{_esc(desc)}</p></div>"
        for href, name, tag, desc in cards
    )
    body = (
        f'<h2 style="margin-top:0">{_esc(L["mission_control"])}</h2>\n'
        f'<div class="cards">\n{card_html}\n</div>\n'
        f'<p class="meta">{_esc(L["choose_advisor"])}</p>\n'
    )
    return _page(L["mission_control"], body, active="home", language=language)


def render_advisor_form(
    action: str,
    heading: str,
    description: str,
    default_question: str,
    placeholder: str = "",
    active: str = "",
    language: str = "en",
) -> str:
    from app import language_mode as lm
    L = lm.get_ui_bundle(language)
    body = (
        f'<h2 style="margin-top:0">{_esc(heading)}</h2>\n'
        f"<p class=\"meta\">{_esc(description)}</p>\n"
        # POST goes to the plain action (no ?lang=); language is carried in
        # the hidden/selector field and stored on the job.
        f'<form method="POST" action="{_esc(action)}">\n'
        f'<div class="label">{_esc(L["your_operations_question"])}</div>\n'
        f'<textarea name="question" placeholder="{_esc(placeholder)}">'
        f"{_esc(default_question)}</textarea>\n"
        f"{_language_selector(language, L['response_language'])}"
        f'<button id="submitBtn" type="submit">{_esc(L["get_operating_guidance"])}</button>\n'
        f'<div id="loadingMsg" class="meta" style="display:none;'
        f'margin-top:.8rem;">{_esc(L["loading_message"])}</div>\n'
        "</form>\n"
        f"{_loading_script()}"
    )
    return _page(heading, body, active=active, language=language)


def render_advisor_result(
    heading: str,
    question: str,
    answer: str,
    mode_label: str,
    runtime_notes: str = "",
    error: Optional[str] = None,
    active: str = "",
    language: str = "en",
) -> str:
    from app import language_mode as lm
    L = lm.get_ui_bundle(language)
    parts = [f'<h2 style="margin-top:0">{_esc(heading)}</h2>\n']

    parts.append(f'<div class="warn">{_esc(L["boundary_warning"])}</div>\n')

    if error:
        parts.append(f'<div class="err">{_esc(error)}</div>\n')

    parts.append(f'<div class="label">{_esc(L["your_question"])}</div>\n')
    parts.append(f"<section class=\"result\">{_esc(question)}</section>\n")

    parts.append(
        f'<div class="label">{_esc(L["operating_guidance"])}</div>\n'
    )
    parts.append(f'<section class="result">{_esc(answer)}</section>\n')

    if runtime_notes:
        parts.append(f'<div class="label">{_esc(L["runtime_summary"])}</div>\n')
        parts.append(f'<section class="result">{_esc(runtime_notes)}</section>\n')

    parts.append(
        '<div class="result-nav">'
        f'<a href="{_url_with_lang("/", language)}">&#8592; {_esc(L["mission_control"])}</a>'
        f'<a href="{_url_with_lang("/demo", language)}">{_esc(L["demo_scenarios"])}</a>'
        f'<a href="{_url_with_lang("/status", language)}">{_esc(L["offline_status"])}</a>'
        "</div>\n"
    )
    return _page(heading, "".join(parts), active=active, language=language)


def _pill(ok: bool, text: str) -> str:
    cls = "ok" if ok else "no"
    return f'<span class="pill {cls}">{_esc(text)}</span>'


def render_status(status: dict, language: str = "en") -> str:
    from app import language_mode as lm
    L = lm.get_ui_bundle(language)
    # Translate known status keys via the UI bundle; technical values unchanged.
    key_map = {
        "product": L["product"],
        "model_lock": L["locked_candidate"],
        "model_path_exists": L["model_path_exists"],
        "llama_binary_detected": L["llama_binary"],
        "retrieval_index_exists": L["retrieval_index"],
        "sqlite_fts_status": L["retrieval_index"],
        "cloud_dependency": L["no_cloud_dependency"],
        "retrieval_grounded": L["retrieval_grounded"],
        "direct_answer": L["direct_answer_mode"],
        "local_only": L["local_only"],
        "response_language": L["response_language"],
    }
    rows = []
    for key, val in status.items():
        disp_key = key_map.get(key, key)
        if isinstance(val, bool):
            val_html = _pill(val, L["yes"] if val else L["no"])
        else:
            val_html = f'<span class="v">{_esc(val)}</span>'
        rows.append(
            f'<div class="row"><span class="k">{_esc(disp_key)}</span>{val_html}</div>'
        )
    body = (
        f'<h2 style="margin-top:0">{_esc(L["offline_system_status"])}</h2>\n'
        f'<div class="status-grid">\n{"".join(rows)}\n</div>\n'
        '<div class="result-nav">'
        f'<a href="{_url_with_lang("/", language)}">&#8592; {_esc(L["mission_control"])}</a>'
        f'<a href="{_url_with_lang("/demo", language)}">{_esc(L["demo_scenarios"])}</a>'
        "</div>\n"
    )
    return _page(L["offline_system_status"], body, active="status", language=language)


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


def render_demo(language: str = "en") -> str:
    from app import language_mode as lm
    L = lm.get_ui_bundle(language)
    scenarios = lm.get_demo_scenarios(language)
    cards = []
    for i, (title, action, advisor, prompt) in enumerate(scenarios, 1):
        btn_id = f"demoBtn{i}"
        cards.append(
            f'<div class="card">'
            f'<span class="card-tag">Scenario {i}</span>'
            f"<h2>{_esc(title)}</h2>"
            f'<p><em>{_esc(advisor)}</em></p>'
            f'<p>{_esc(prompt)}</p>'
            f'<form method="POST" action="{_esc(action)}">'
            f'<textarea name="question" style="display:none;">{_esc(prompt)}</textarea>'
            f"{_language_selector(language, L['response_language'])}"
            f'<button id="{btn_id}" type="submit">{_esc(L["run_this_scenario"])}</button>'
            f'<div id="loadingMsg{i}" class="meta" style="display:none;'
            f'margin-top:.6rem;font-size:.8rem;">{_esc(L["loading_message"])}</div>'
            f"</form>"
            f"</div>"
        )
    # One small script that wires up every demo button by id.
    wire = "".join(
        f"  _wire('demoBtn{i}','loadingMsg{i}');\n"
        for i in range(1, len(scenarios) + 1)
    )
    script = (
        "<script>\n"
        "(function(){\n"
        "  function _wire(btnId, msgId){\n"
        "    var btn = document.getElementById(btnId);\n"
        "    if(!btn || !btn.form){ return; }\n"
        "    btn.form.addEventListener('submit', function(){\n"
        f"      btn.disabled = true;\n"
        f"      btn.textContent = {_esc(L['running_local_model'])!r};\n"
        "      var msg = document.getElementById(msgId);\n"
        "      if(msg){ msg.style.display = 'block'; }\n"
        "    });\n"
        "  }\n"
        f"{wire}"
        "})();\n"
        "</script>\n"
    )
    body = (
        f'<h2 style="margin-top:0">{_esc(L["demo_scenarios"])}</h2>\n'
        f'<p class="meta">{_esc(L["demo_intro"])}</p>\n'
        f'<div class="cards">\n{"".join(cards)}\n</div>\n'
        f"{script}"
        '<div class="result-nav">'
        f'<a href="{_url_with_lang("/", language)}">&#8592; {_esc(L["mission_control"])}</a>'
        f'<a href="{_url_with_lang("/status", language)}">{_esc(L["offline_status"])}</a>'
        "</div>\n"
    )
    return _page(L["demo_scenarios"], body, active="demo", language=language)


def health_json(payload: dict) -> str:
    """Serialize a health dict to JSON (for the /health route)."""
    import json

    return json.dumps(payload, indent=2)


def _status_detail_panel(detail: dict, language: str = "en") -> str:
    """Render the small status-detail panel used on job pages.

    Keys (all optional, booleans rendered as yes/no pills):
      model_path_exists, llama_binary, retrieval_index_exists,
      locked_candidate, retrieval_grounded, direct_answer, local_only
    """
    from app import language_mode as lm
    L = lm.get_ui_bundle(language)
    rows = []

    def _row(k: str, v) -> str:
        if isinstance(v, bool):
            v_html = _pill(v, L["yes"] if v else L["no"])
        else:
            v_html = f'<span class="v">{_esc(v)}</span>'
        return f'<div class="row"><span class="k">{_esc(k)}</span>{v_html}</div>'

    rows.append(_row(L["model_path_exists"],
                     detail.get("model_path_exists", "not available")))
    rows.append(_row(L["llama_binary"],
                     detail.get("llama_binary", "not detected")))
    rows.append(_row(L["retrieval_index"],
                     detail.get("retrieval_index_exists", "not available")))
    rows.append(_row(L["locked_candidate"],
                     detail.get("locked_candidate", "unknown")))
    rows.append(_row(L["retrieval_grounded"],
                     detail.get("retrieval_grounded", True)))
    rows.append(_row(L["direct_answer_mode"],
                     detail.get("direct_answer", True)))
    rows.append(_row(L["local_only"], detail.get("local_only", True)))
    return (
        '<section class="result" style="margin-top:1rem;">'
        f'<div class="label">{_esc(L["runtime_status"])}</div>'
        f'<div class="status-grid">{"".join(rows)}</div>'
        "</section>\n"
    )


def render_job(
    job: dict,
    detail: Optional[dict] = None,
    active: str = "",
    language: str = "",
) -> str:
    """Render the job progress/result page (localized).

    The job's own language_code is preferred; the `language` arg is a fallback
    (used when rendering outside a job, e.g. a test).
    """
    from app import language_mode as lm
    job_lang = job.get("language_code") or language or "en"
    L = lm.get_ui_bundle(job_lang)
    status = job.get("status", "queued")
    step = int(job.get("step", 1))
    steps = lm.get_progress_steps(job_lang)
    # Clamp step index into range for display.
    disp_step = max(1, min(step, len(steps)))

    parts = [f'<h2 style="margin-top:0">{_esc(job.get("advisor", "Advisor"))}</h2>\n']

    # Status pill.
    status_pill = {
        "queued": _pill(True, L["queued"]),
        "running": _pill(True, L["running"]),
        "complete": _pill(True, L["complete"]),
        "failed": _pill(False, L["failed"]),
    }.get(status, _pill(False, status))
    parts.append(
        f'<div class="label">Job {job.get("job_id", "")} · {status_pill}</div>\n'
    )

    # Response language (if set on the job).
    lang_label = job.get("language_label")
    if lang_label:
        parts.append(
            f'<p class="meta">{_esc(L["response_language"])}: <strong>{_esc(lang_label)}</strong></p>\n'
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
            f'<div class="warn">{_esc(L["inference_time_warning"])}</div>\n'
        )

    # The question (demo only; still escaped).
    q = job.get("question", "")
    if q:
        parts.append(f'<div class="label">{_esc(L["your_question"])}</div>\n')
        parts.append(f'<section class="result">{_esc(q)}</section>\n')

    # Answer or error.
    if status == "complete":
        parts.append(f'<div class="label">{_esc(L["operating_guidance"])}</div>\n')
        answer = job.get("answer", "") or L["empty_answer"]
        parts.append(f'<section class="result">{_esc(answer)}</section>\n')
        # Prompt-echo note: if the echoed prompt was stripped, tell the user.
        if job.get("prompt_echo_stripped", False):
            parts.append(
                f'<div class="meta" style="margin-top:.4rem;">{_esc(L["prompt_echo_removed"])}</div>\n'
            )
        # Extraction warning (if any).
        warn = job.get("extraction_warning", "")
        if warn:
            parts.append(
                f'<div class="warn">{_esc(warn)}</div>\n'
            )
        parts.append(f'<div class="warn">{_esc(L["boundary_warning"])}</div>\n')
        notes = job.get("runtime_notes", "")
        if notes:
            parts.append(f'<div class="label">{_esc(L["runtime_summary"])}</div>\n')
            parts.append(f'<section class="result">{_esc(notes)}</section>\n')
    elif status == "failed":
        err = job.get("error", "Unknown error")
        parts.append(
            f'<div class="err">{_esc(L["error_title"])}</div>\n'
        )
        parts.append(f'<div class="label">{_esc(L["error_summary"])}</div>\n')
        parts.append(f'<section class="result">{_esc(err)}</section>\n')

    # Status detail panel.
    if detail:
        parts.append(_status_detail_panel(detail, job_lang))

    parts.append(
        '<div class="result-nav">'
        f'<a href="{_url_with_lang("/", job_lang)}">&#8592; {_esc(L["mission_control"])}</a>'
        f'<a href="{_url_with_lang("/advisor/daily", job_lang)}">{_esc(L["daily_advisor"])}</a>'
        f'<a href="{_url_with_lang("/status", job_lang)}">{_esc(L["offline_status"])}</a>'
        "</div>\n"
    )

    # Auto-refresh while in progress.
    head_extra = ""
    if status in ("queued", "running"):
        head_extra = '<meta http-equiv="refresh" content="3">\n'

    return _page(L["operating_guidance"], "".join(parts), active=active,
                 head_extra=head_extra, language=job_lang)


def render_error(
    summary: str,
    route: str = "",
    detail: Optional[dict] = None,
    language: str = "en",
) -> str:
    """Browser-friendly error page. Does not expose long private tracebacks."""
    from app import language_mode as lm
    L = lm.get_ui_bundle(language)
    parts = [f'<h2 style="margin-top:0">{_esc(L["error_title"])}</h2>\n']
    parts.append(f'<div class="err">{_esc(summary)}</div>\n')
    if route:
        parts.append(
            f'<p class="meta">{_esc(L["current_route"])}: <code>{_esc(route)}</code></p>\n'
        )
    parts.append(f'<div class="label">{_esc(L["suggested_checks"])}</div>\n')
    parts.append(
        "<section class=\"result\">"
        "<ul>"
        f"<li>{_esc(L['check_model_present'])}</li>"
        f"<li>{_esc(L['check_llama_available'])}</li>"
        f"<li>{_esc(L['check_timeout'])}</li>"
        f"<li>{_esc(L['check_terminal_logs'])}</li>"
        "</ul>"
        "</section>\n"
    )
    if detail:
        parts.append(_status_detail_panel(detail, language))
    parts.append(
        '<div class="result-nav">'
        f'<a href="{_url_with_lang("/", language)}">&#8592; {_esc(L["mission_control"])}</a>'
        f'<a href="{_url_with_lang("/advisor/daily", language)}">{_esc(L["daily_advisor"])}</a>'
        f'<a href="{_url_with_lang("/status", language)}">{_esc(L["offline_status"])}</a>'
        "</div>\n"
    )
    return _page(L["error_title"], "".join(parts), language=language)


def render_job_missing(job_id: str, language: str = "en") -> str:
    """Page shown when a job id is unknown (expired or invalid)."""
    from app import language_mode as lm
    L = lm.get_ui_bundle(language)
    parts = [
        f'<h2 style="margin-top:0">{_esc(L["job_not_found"])}</h2>\n',
        f'<div class="err">Job <code>{_esc(job_id)}</code> {_esc(L["job_not_found_detail"])}</div>\n',
        '<div class="result-nav">'
        f'<a href="{_url_with_lang("/", language)}">&#8592; {_esc(L["mission_control"])}</a>'
        f'<a href="{_url_with_lang("/advisor/daily", language)}">{_esc(L["daily_advisor"])}</a>'
        f'<a href="{_url_with_lang("/status", language)}">{_esc(L["offline_status"])}</a>'
        "</div>\n",
    ]
    return _page(L["job_not_found"], "".join(parts), language=language)


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
