"""HTML rendering helpers for the AfrekaOS Offline local web UI.

Standard library only. No external CSS, JS, fonts, CDNs, or images. All user
content is escaped. Plain CSS is embedded in each page.
"""

from __future__ import annotations

import html
from typing import Optional

# --- Embedded CSS -----------------------------------------------------------

_CSS = """
:root { --bg:#030607; --card:rgba(11,16,17,.88); --accent:#e1ad3d; --text:#f4f1e9;
        --gold:#e1ad3d; --bright-gold:#f5c453; --forest:#070b0c; --critical:#c75b52;
        --muted:#9ca3af; --warn:#fbbf24; --err:#f87171; --border:#2d3139;
        --banner:#15201a; }
* { box-sizing:border-box; } html { background:var(--bg); scroll-behavior:smooth; }
body { margin:0; font-family:Inter,"Helvetica Neue",Helvetica,Arial,sans-serif; background:radial-gradient(circle at 70% 30%,rgba(141,100,28,.16) 0,transparent 26%),linear-gradient(115deg,#030607 10%,#070b0c 55%,#111718); color:var(--text);
       line-height:1.6; min-height:100vh; }
body:before { content:""; pointer-events:none; position:fixed; inset:0; opacity:.12; z-index:5; background-image:linear-gradient(90deg,transparent 24.9%,rgba(225,173,61,.18) 25%,transparent 25.1%,transparent 49.9%,rgba(225,173,61,.12) 50%,transparent 50.1%,transparent 74.9%,rgba(225,173,61,.18) 75%,transparent 75.1%); background-size:100% 100%; }
.container { max-width:1240px; margin:0 auto; padding:1.25rem clamp(1rem,4vw,4rem) 4rem; position:relative; }
header { display:flex; align-items:center; gap:1rem; border-bottom:1px solid rgba(243,239,229,.15); padding-bottom:1rem; margin-bottom:1rem; position:relative; z-index:6; }
header h1 { margin:0; font-size:1.02rem; letter-spacing:.08em; text-transform:uppercase; }
header .tagline { color:var(--muted); font-size:.9rem; }
.banner { background:rgba(11,16,17,.8); border:1px solid rgba(225,173,61,.34);
          border-radius:999px; padding:.35rem .75rem; margin-bottom:1.2rem;
          display:flex; flex-wrap:wrap; gap:.5rem; align-items:center; width:max-content; }
.banner .b-item { font-size:.78rem; color:#55d784; }
.banner .b-mark { font-weight:700; margin-right:.2rem; }
.banner .b-sep { color:var(--muted); font-size:.78rem; }
nav.topnav { display:flex; flex-wrap:wrap; gap:1.15rem; margin:0 0 1.5rem; font-size:.78rem; letter-spacing:.06em; text-transform:uppercase; position:relative; z-index:6; }
nav.topnav a { color:rgba(243,239,229,.68); }
nav.topnav a:hover { color:var(--accent); }
.langswitch { display:inline-block; margin-left:auto; }
.langswitch-label { font-size:.78rem; color:var(--muted); }
.langswitch select { width:auto; display:inline-block; font-size:.8rem;
                     padding:.25rem .5rem; margin-top:0; }
a { color:var(--accent); text-decoration:none; }
a:hover { text-decoration:underline; }
.cards { display:grid; gap:.9rem; grid-template-columns:1fr; }
@media(min-width:600px){ .cards{ grid-template-columns:1fr 1fr; } }
.card,form,section.result { background:linear-gradient(135deg,rgba(255,255,255,.055),rgba(255,255,255,.015)); border:1px solid rgba(243,239,229,.14); border-radius:14px; backdrop-filter:blur(8px); box-shadow:inset 0 1px 1px rgba(255,255,255,.08),0 24px 50px rgba(0,0,0,.15); }
.card { padding:1.2rem; transition:border-color .15s,transform .15s; }
.card:hover { border-color:var(--accent); transform:translateY(-2px); }
.card h2 { margin:0 0 .3rem; font-size:1.1rem; }
.card h2 a { color:var(--text); }
.card p { margin:0; color:var(--muted); font-size:.88rem; }
.card .card-tag { display:inline-block; font-size:.7rem; color:var(--accent);
                  border:1px solid var(--accent); border-radius:99px;
                  padding:.05rem .5rem; margin-bottom:.5rem; }
form { padding:1.2rem; margin-bottom:1.5rem; }
textarea { width:100%; min-height:160px; background:rgba(5,8,7,.72); color:var(--text);
           border:1px solid var(--border); border-radius:8px; padding:.7rem;
           font-size:.95rem; resize:vertical; }
textarea:focus { outline:none; border-color:var(--accent); }
select { width:100%; background:#0b0d11; color:var(--text); border:1px solid var(--border);
         border-radius:8px; padding:.55rem; font-size:.95rem; margin-top:.3rem; }
select:focus { outline:none; border-color:var(--accent); }
button { background:var(--accent); color:#06120c; border:none; border-radius:999px;
         padding:.75rem 1.3rem; font-size:.78rem; letter-spacing:.08em; text-transform:uppercase; font-weight:800; cursor:pointer;
         margin-top:.7rem; }
button:hover { filter:brightness(1.1); }
section.result { padding:1.2rem; margin-bottom:1.2rem;
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
.hero { min-height:calc(100vh - 135px); display:grid; grid-template-columns:minmax(0,1fr) minmax(360px,.95fr); gap:3rem; align-items:center; padding:clamp(2rem,7vh,6rem) 0 4rem; position:relative; }
.eyebrow { color:var(--gold); font-size:.7rem; font-weight:800; letter-spacing:.17em; } .eyebrow:before { content:""; display:inline-block; width:7px; height:7px; background:var(--gold); border-radius:50%; box-shadow:0 0 12px var(--gold); margin-right:.55rem; }.trust-list i {content:"";display:inline-block;width:5px;height:5px;background:#55d784;border-radius:50%;box-shadow:0 0 8px #55d784;margin-right:.55rem}
.hero h2 { font-size:clamp(2.7rem,7vw,5.3rem); line-height:.93; letter-spacing:-.07em; max-width:800px; margin:.8rem 0 1.25rem; text-transform:uppercase; } .hero h2 em { font-style:normal;color:var(--gold); }
.hero-copy { max-width:560px; color:rgba(243,239,229,.75); font-size:1rem; } .hero-actions {display:flex;gap:.75rem;flex-wrap:wrap;margin-top:1.7rem}.secondary {border:1px solid rgba(243,239,229,.36);color:var(--text);padding:.7rem 1.15rem;border-radius:999px;font-size:.78rem;letter-spacing:.08em;text-transform:uppercase;font-weight:700}
.core { min-height:540px; position:relative; perspective:1000px; } .core:before {content:"";position:absolute;left:10%;right:5%;bottom:0;height:150px;background:repeating-radial-gradient(ellipse at center,rgba(225,173,61,.9) 0 1px,transparent 2px 22px),radial-gradient(ellipse,rgba(225,173,61,.35),transparent 64%);border-radius:50%;transform:perspective(500px) rotateX(62deg);filter:drop-shadow(0 0 14px rgba(225,173,61,.6));}
.core-main,.module,.trust-card { position:absolute; background:linear-gradient(135deg,rgba(255,255,255,.09),rgba(5,8,7,.65)); border:1px solid rgba(243,239,229,.17); box-shadow:inset 0 1px 1px rgba(255,255,255,.12),0 30px 80px rgba(0,0,0,.35); backdrop-filter:blur(8px); }
.core-main { inset:12% 12% 18% 12%; padding:1.7rem; transform:rotateY(-12deg) rotateX(6deg); border-radius:8px; border-color:rgba(225,173,61,.55); } .core-main:after{content:"";position:absolute;inset:12px;border:1px solid rgba(225,173,61,.2);border-radius:3px;pointer-events:none}.core-label{color:var(--gold);font-size:.68rem;letter-spacing:.15em;font-weight:800}.input-preview{margin-top:1.3rem;color:var(--text);font-size:1.05rem;line-height:1.45}.diagnostics{display:flex;flex-wrap:wrap;gap:.45rem;margin:1rem 0}.diagnostics span{font-size:.65rem;border:1px solid rgba(225,173,61,.45);color:var(--gold);border-radius:4px;padding:.22rem .55rem}.first-action{border-top:1px solid rgba(243,239,229,.13);padding-top:.8rem;font-size:.82rem;color:rgba(243,239,229,.8)}
.module{padding:.45rem .65rem;border-radius:8px;font-size:.66rem;letter-spacing:.08em;text-transform:uppercase;color:rgba(243,239,229,.82)}.m1{top:7%;right:0}.m2{top:26%;left:0}.m3{right:0;bottom:25%}.m4{bottom:6%;left:10%}.m5{top:2%;left:35%}.m6{right:15%;bottom:4%}.m7{top:48%;right:4%}.trust-card{right:4%;top:8%;width:220px;padding:1.1rem;border-radius:14px;z-index:2}.trust-card strong{display:block;font-size:1.1rem;line-height:1.15;margin:.5rem 0 1rem}.trust-list{list-style:none;padding:0;margin:0}.trust-list li{font-size:.7rem;margin:.45rem 0;color:rgba(243,239,229,.75)}.trust-list i{width:5px;height:5px}
.pressure-section,.operator-section{padding:2rem;margin:1rem 0 2rem;border:1px solid rgba(255,255,255,.12);background:linear-gradient(135deg,rgba(17,23,24,.76),rgba(3,6,7,.7));border-radius:8px}.pressure-section h2{font-size:clamp(1.7rem,3vw,3rem);letter-spacing:-.04em;max-width:620px}.pressure-flow{display:flex;flex-wrap:wrap;gap:.65rem;margin-top:1.5rem;align-items:center}.pressure-flow div{padding:1rem;border:1px solid rgba(225,173,61,.38);background:rgba(11,16,17,.9);border-radius:6px;font-size:.75rem;flex:1;min-width:130px}.pressure-flow b{color:var(--gold)}.operator-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:.65rem;margin-top:1rem}.operator-grid .card{min-height:150px}.runtime-bar{display:flex;gap:.6rem;flex-wrap:wrap;margin-top:1rem}.runtime-bar span{padding:.65rem;border:1px solid rgba(255,255,255,.12);font-size:.67rem;letter-spacing:.08em}.runtime-bar strong{color:#55d784;display:block}.runtime-note{color:var(--gold)!important;border-color:rgba(225,173,61,.5)!important}
@media(max-width:720px){.container{padding:1rem 1.1rem 3rem}header .tagline,.banner{display:none}.topnav{gap:.75rem;font-size:.65rem}.hero{grid-template-columns:1fr;min-height:auto;padding-top:3rem;gap:1rem}.hero h2{font-size:clamp(2.6rem,13vw,4rem)}.core{min-height:460px}.trust-card{width:180px;right:0}.core-main{inset:18% 2% 10% 4%}.module{font-size:.55rem}.m2,.m5{display:none}.pressure-section{padding:1.2rem}.operator-grid{grid-template-columns:1fr}.pressure-flow{flex-direction:column;align-items:stretch}.pressure-flow b{text-align:center}}
@media(prefers-reduced-motion:no-preference){.core-main{animation:float 9s ease-in-out infinite}.module{animation:float 11s ease-in-out infinite}.m3,.m6{animation-delay:-4s}@keyframes float{50%{transform:translateY(-8px) rotateY(-10deg)}}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;scroll-behavior:auto!important}}
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


def _loading_script(button_id: str = "submitBtn", language: str = "en") -> str:
    """Inline JS that disables the submit button and shows a loading message.

    No external files or dependencies. If JavaScript is disabled, the form
    submits normally as a plain POST. The script is intentionally tiny.
    """
    from app import language_mode as lm
    return (
        "<script>\n"
        "(function(){\n"
        f"  var btn = document.getElementById({button_id!r});\n"
        "  if(!btn || !btn.form){ return; }\n"
        "  btn.form.addEventListener('submit', function(){\n"
        f"    btn.disabled = true;\n"
        f"    btn.textContent = {_esc(lm.get_ui_text('running_local_model', language))!r};\n"
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
    advisor = _url_with_lang("/advisor/daily", language)
    status = _url_with_lang("/status", language)
    body = (
        '<main class="hero">'
        f'<section><div class="eyebrow">{_esc(L["hero_eyebrow"])}</div>'
        f'<h2>{_esc(L["hero_title"])}<em>.</em></h2>'
        f'<p class="hero-copy">{_esc(L["hero_copy"])}</p>'
        '<div class="hero-actions">'
        f'<a class="secondary" style="background:var(--accent);color:#050807;border-color:var(--accent)" href="{advisor}">{_esc(L["open_daily"])} &#8594;</a>'
        f'<a class="secondary" href="{status}">{_esc(L["view_status"])}</a></div></section>'
        '<section class="core" aria-label="AfrekaOS operations preview">'
        f'<div class="trust-card"><span class="core-label">{_esc(L["local_only"])}</span><strong>{_esc(L["operational_guidance_only"])}</strong><ul class="trust-list"><li><i></i>{_esc(L["local_model"])}</li><li><i></i>{_esc(L["retrieval_index"])}</li><li><i></i>{_esc(L["no_cloud_dependency"])}</li><li><i></i>{_esc(L["local_only"])}</li></ul></div>'
        f'<div class="core-main"><span class="core-label">{_esc(L["daily_advisor"])} · {_esc(L["your_operations_question"])}</span><p class="input-preview">{_esc(lm.get_default_prompt("daily", language))}</p><div class="diagnostics"><span>{_esc(L["inventory_advisor"])}</span><span>{_esc(L["retrieval_grounded"])}</span><span>{_esc(L["daily_advisor"])}</span><span>{_esc(L["cashflow_advisor"])}</span></div><div class="first-action"><span class="core-label">{_esc(L["operating_guidance"])}</span><br>{_esc(L["choose_advisor"])}</div></div>'
        f'<a class="module m1" href="{_url_with_lang("/advisor/inventory", language)}">Inventory</a><span class="module m2">Suppliers</span><span class="module m3">Customer Credit</span><a class="module m4" href="{_url_with_lang("/advisor/cashflow", language)}">Cashflow</a><span class="module m5">Staffing</span><span class="module m6">Records</span><span class="module m7">Expansion</span></section></main>'
        '<section class="pressure-section"><div class="eyebrow">CONNECTED PRESSURES</div><h2>ONE PROBLEM. MULTIPLE CONNECTED PRESSURES.</h2><p class="meta">Problems in one area create pressure in others.</p><div class="pressure-flow"><div><span class="core-label">SUPPLIER DELAY</span><br>Late deliveries or stockouts</div><b>&#8594;</b><div><span class="core-label">INVENTORY PRESSURE</span><br>Stock missing or unavailable</div><b>&#8594;</b><div><span class="core-label">LOST SALES</span><br>Customers go elsewhere</div><b>&#8594;</b><div><span class="core-label">CUSTOMER CREDIT</span><br>More credit requests</div><b>&#8594;</b><div><span class="core-label">CASHFLOW PRESSURE</span><br>Less cash for operations</div></div><p class="meta" style="text-align:center">AfrekaOS shows what is connected and what to do first.</p></section>'
        '<section class="operator-section"><div class="eyebrow">BUILT FOR BUSINESS OPERATORS</div><div class="operator-grid"><div class="card"><span class="core-label">UNDERSTAND FAST</span><p>Clear insights from real business situations.</p></div><div class="card"><span class="core-label">STAY IN CONTROL</span><p>Make better decisions with confidence.</p></div><div class="card"><span class="core-label">100% PRIVATE</span><p>Runs locally. Your data stays on this device.</p></div><div class="card"><span class="core-label">IMPROVE RESULTS</span><p>Take action that improves cash, stock, and growth.</p></div><div class="card"><span class="core-label">ALWAYS AVAILABLE</span><p>No internet needed. Works when you need it.</p></div></div><div class="runtime-bar"><span>LOCAL MODEL<strong>Ready</strong></span><span>LOCAL KNOWLEDGE<strong>Ready</strong></span><span>INTERNET REQUIRED<strong>No</strong></span><span>CLOUD SYNC<strong>None</strong></span><span class="runtime-note">THIS SYSTEM IS RUNNING ENTIRELY ON THIS COMPUTER.</span></div></section>'
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
        '<section class="advisor-shell">'
        f'<div class="eyebrow">LOCAL OPERATING BRIEF</div><h2 style="margin:.5rem 0">{_esc(heading)}</h2>\n'
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
        f"{_loading_script(language=language)}</section>"
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
            f'<span class="card-tag">{_esc(L["scenario"])} {i}</span>'
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
