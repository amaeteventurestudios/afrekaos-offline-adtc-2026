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
.banner .b-item::before { content:"\2713 "; }
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
footer { margin-top:2rem; color:var(--muted); font-size:.8rem;
         border-top:1px solid var(--border); padding-top:1rem; }
"""

# The unified boundary warning text used on every advisor result.
WARNING_TEXT = (
    "AfrekaOS provides operational guidance only. It is not accounting, "
    "banking, payroll, tax, lending, or ERP software."
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
    """Render the offline status banner."""
    items = [
        ("Offline mode",),
        ("Local model",),
        ("SQLite retrieval",),
        ("No cloud dependency",),
    ]
    parts = []
    for i, (label,) in enumerate(items):
        if i > 0:
            parts.append('<span class="b-sep">\u00b7</span>')
        parts.append(f'<span class="b-item">{_esc(label)}</span>')
    return '<div class="banner">' + "".join(parts) + "</div>\n"


def _page(title: str, body: str, active: str = "") -> str:
    """Wrap body in a full HTML document with embedded CSS."""
    return (
        "<!DOCTYPE html>\n"
        '<html lang="en">\n<head>\n'
        '<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
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
        "<button type=\"submit\">Get operating guidance</button>\n"
        "</form>\n"
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
        cards.append(
            f'<div class="card">'
            f'<span class="card-tag">Scenario {i}</span>'
            f"<h2>{_esc(title)}</h2>"
            f'<p><em>{_esc(advisor)}</em></p>'
            f'<p>{_esc(prompt)}</p>'
            f'<form method="POST" action="{_esc(action)}">'
            f'<textarea name="question" style="display:none;">{_esc(prompt)}</textarea>'
            f'<button type="submit">Run this scenario</button>'
            f"</form>"
            f"</div>"
        )
    body = (
        '<h2 style="margin-top:0">Demo Scenarios</h2>\n'
        '<p class="meta">Ready-made SME operations scenarios. Click '
        '"Run this scenario" to submit the prompt to the matching advisor. '
        "Answers are retrieval-grounded and local-only.</p>\n"
        f'<div class="cards">\n{"".join(cards)}\n</div>\n'
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


__all__ = [
    "WARNING_TEXT",
    "DEMO_SCENARIOS",
    "render_home",
    "render_advisor_form",
    "render_advisor_result",
    "render_status",
    "render_demo",
    "health_json",
]
