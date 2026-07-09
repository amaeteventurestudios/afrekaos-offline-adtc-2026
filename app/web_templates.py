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
        --muted:#9ca3af; --warn:#fbbf24; --err:#f87171; --border:#2d3139; }
* { box-sizing:border-box; }
body { margin:0; font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,
       Helvetica,Arial,sans-serif; background:var(--bg); color:var(--text);
       line-height:1.6; }
.container { max-width:860px; margin:0 auto; padding:1.5rem 1rem 4rem; }
header { border-bottom:1px solid var(--border); padding-bottom:1rem; margin-bottom:1.5rem; }
header h1 { margin:0; font-size:1.5rem; }
header .tagline { color:var(--muted); font-size:.9rem; }
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }
.cards { display:grid; gap:.9rem; grid-template-columns:1fr; }
@media(min-width:600px){ .cards{ grid-template-columns:1fr 1fr; } }
.card { background:var(--card); border:1px solid var(--border); border-radius:10px;
        padding:1.2rem; transition:border-color .15s; }
.card:hover { border-color:var(--accent); }
.card h2 { margin:0 0 .3rem; font-size:1.15rem; }
.card p { margin:0; color:var(--muted); font-size:.9rem; }
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
                 border-radius:10px; padding:1.2rem; margin-bottom:1.5rem;
                 white-space:pre-wrap; word-wrap:break-word; }
.label { color:var(--muted); font-size:.8rem; text-transform:uppercase;
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
.status-grid .row .v { font-family:monospace; }
.pill { display:inline-block; padding:.1rem .5rem; border-radius:99px; font-size:.75rem; }
.pill.ok { background:rgba(74,222,128,.15); color:var(--accent); }
.pill.no { background:rgba(248,113,113,.15); color:var(--err); }
footer { margin-top:2rem; color:var(--muted); font-size:.8rem;
         border-top:1px solid var(--border); padding-top:1rem; }
"""


def _esc(s: object) -> str:
    """HTML-escape a value."""
    return html.escape(str(s), quote=True)


def _page(title: str, body: str) -> str:
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
        f"{body}\n"
        "<footer>AfrekaOS Offline — local-only. No cloud. "
        "Operational guidance, not accounting/banking/payroll/tax/ERP software."
        "</footer>\n"
        "</div>\n</body>\n</html>\n"
    )


# --- Page renderers ---------------------------------------------------------

def render_home() -> str:
    cards = [
        ("/advisor/daily", "Daily Operations Advisor",
         "Triage low sales, stockouts, supplier delays, and credit pressure."),
        ("/advisor/inventory", "Inventory and Stock Check",
         "Check fast-moving items, slow stock, reorder points, and supplier lead times."),
        ("/advisor/cashflow", "Cashflow Pressure Coach",
         "Reason through cash pressure, credit requests, and record gaps."),
        ("/status", "Offline System Status",
         "Model lock, retrieval index, runtime, and offline status."),
    ]
    card_html = "\n".join(
        f'<div class="card"><h2><a href="{href}">{_esc(name)}</a></h2>'
        f"<p>{_esc(desc)}</p></div>"
        for href, name, desc in cards
    )
    body = (
        '<h2 style="margin-top:0">Mission Control</h2>\n'
        f'<div class="cards">\n{card_html}\n</div>\n'
        '<p class="meta">Choose a coach above to reason through a daily '
        "operations question. Answers are retrieval-grounded and local-only.</p>\n"
    )
    return _page("Mission Control", body)


def render_advisor_form(
    action: str,
    heading: str,
    description: str,
    default_question: str,
    placeholder: str = "",
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
    return _page(heading, body)


def render_advisor_result(
    heading: str,
    question: str,
    answer: str,
    mode_label: str,
    runtime_notes: str = "",
    error: Optional[str] = None,
) -> str:
    parts = [f'<h2 style="margin-top:0">{_esc(heading)}</h2>\n']

    warn = (
        '<div class="warn">This is operational guidance, not accounting, '
        "banking, payroll, tax, or ERP software. Verify your own records "
        "before acting.</div>\n"
    )
    parts.append(warn)

    if error:
        parts.append(f'<div class="err">{_esc(error)}</div>\n')

    parts.append('<div class="label">Your question</div>\n')
    parts.append(f"<section class=\"result\">{_esc(question)}</section>\n")

    parts.append(
        f'<div class="label">Operating guidance ({_esc(mode_label)})</div>\n'
    )
    parts.append(f'<section class="result">{_esc(answer)}</section>\n')

    if runtime_notes:
        parts.append('<div class="label">Runtime notes</div>\n')
        parts.append(f'<section class="result">{_esc(runtime_notes)}</section>\n')

    parts.append(f'<p><a href="/">&#8592; Back to Mission Control</a></p>\n')
    return _page(heading, "".join(parts))


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
        '<p><a href="/">&#8592; Back to Mission Control</a></p>\n'
    )
    return _page("Offline System Status", body)


def health_json(payload: dict) -> str:
    """Serialize a health dict to JSON (for the /health route)."""
    import json

    return json.dumps(payload, indent=2)


__all__ = [
    "render_home",
    "render_advisor_form",
    "render_advisor_result",
    "render_status",
    "health_json",
]
