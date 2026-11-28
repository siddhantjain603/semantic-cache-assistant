"""UI v2 - "cache console" design system.

Dark, instrument-panel look: near-black surfaces, lime = cache HIT (free),
amber = cache MISS (paid LLM call). Call ``apply_theme()`` once per page,
right after ``st.set_page_config``. HTML snippets are built without blank
lines or deep indentation so Streamlit's markdown never turns them into code.
"""

import streamlit as st

UI_VERSION = "v2"
THRESHOLD_SCALE = 0.60  # matches the sidebar slider max

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,800&family=DM+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');
:root{
  --bg:#0B0D12; --panel:#11141B; --panel-2:#161A23; --line:#222733; --line-2:#2E3545;
  --ink:#E7EAF0; --dim:#8B93A7; --faint:#566074;
  --hit:#C6F135; --hit-soft:rgba(198,241,53,.12);
  --miss:#FFB020; --miss-soft:rgba(255,176,32,.12);
  --info:#6EA8FF;
  --head:'Bricolage Grotesque','DM Sans',sans-serif;
  --body:'DM Sans',system-ui,sans-serif;
  --mono:'IBM Plex Mono',ui-monospace,monospace;
}
/* ---------- base ---------- */
.stApp{background:var(--bg);}
.stApp, .stMarkdown, p, li, label, input, textarea, button{font-family:var(--body);-webkit-font-smoothing:antialiased;}
.stApp::before{content:"";position:fixed;inset:0;pointer-events:none;z-index:0;
  background:radial-gradient(900px 420px at 85% -10%,rgba(198,241,53,.07),transparent 60%),
             radial-gradient(700px 400px at -10% 10%,rgba(110,168,255,.06),transparent 60%);}
.block-container{max-width:1120px;padding-top:1.6rem;padding-bottom:4rem;position:relative;z-index:1;}
header[data-testid="stHeader"]{background:transparent;}
h1,h2,h3{font-family:var(--head)!important;letter-spacing:-.025em;color:var(--ink);}
code,.mono{font-family:var(--mono)!important;}
code{background:var(--panel-2)!important;border:1px solid var(--line);color:var(--hit)!important;border-radius:6px;padding:1px 6px!important;font-size:.88em!important;}
hr{border-color:var(--line)!important;}

/* ---------- top bar ---------- */
.topbar{display:flex;align-items:center;justify-content:space-between;margin-bottom:34px;}
.wordmark{font-family:var(--head);font-weight:800;font-size:19px;letter-spacing:-.03em;color:var(--ink);}
.wordmark b{color:var(--hit);}
.chip{display:inline-flex;align-items:center;gap:8px;font-family:var(--mono);font-size:12px;color:var(--dim);
  border:1px solid var(--line);background:var(--panel);padding:6px 12px;border-radius:999px;}
.chip i{width:7px;height:7px;border-radius:50%;background:var(--hit);box-shadow:0 0 10px var(--hit);}

/* ---------- hero ---------- */
.hero2{padding:8px 0 30px 0;}
.eyebrow{font-family:var(--mono);font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--hit);margin-bottom:16px;}
.hero2 h1{font-weight:800!important;font-size:clamp(38px,6.4vw,68px)!important;line-height:1.0!important;margin:0 0 18px 0!important;padding:0!important;max-width:820px;}
.hero2 h1 em{font-style:normal;color:var(--hit);}
.hero2 p{font-size:18px;line-height:1.6;color:var(--dim);max-width:600px;margin:0;}
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--line);border:1px solid var(--line);border-radius:16px;overflow:hidden;margin:30px 0 8px 0;}
.stat{background:var(--panel);padding:16px 18px;}
.stat .k{font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);}
.stat .v{font-family:var(--mono);font-size:22px;font-weight:600;color:var(--ink);margin-top:6px;}
.stat .v small{font-size:12px;color:var(--dim);font-weight:400;margin-left:4px;}

/* ---------- sections ---------- */
.sec{display:flex;align-items:baseline;gap:12px;margin:38px 0 14px 0;}
.sec .n{font-family:var(--mono);font-size:12px;color:var(--hit);}
.sec h2{font-size:24px!important;margin:0!important;padding:0!important;}
.sec .hint{margin-left:auto;font-size:13px;color:var(--faint);}

/* ---------- how-it-works steps ---------- */
.steps3{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;}
.step{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:22px;transition:border-color .2s,transform .2s;}
.step:hover{border-color:var(--hit);transform:translateY(-2px);}
.step .num{font-family:var(--mono);font-size:12px;color:var(--hit);margin-bottom:14px;}
.step h3{font-size:19px!important;margin:0 0 8px 0!important;}
.step p{color:var(--dim);font-size:14.5px;line-height:1.6;margin:0;}
.demo-table{width:100%;border:1px solid var(--line);border-radius:16px;overflow:hidden;background:var(--panel);}
.demo-row{display:flex;align-items:center;gap:14px;padding:14px 18px;border-top:1px solid var(--line);flex-wrap:wrap;}
.demo-row:first-child{border-top:none;}
.demo-row .q{font-family:var(--mono);font-size:14px;color:var(--ink);flex:1;min-width:220px;}
.demo-row .why{font-size:13px;color:var(--dim);}

/* ---------- badges ---------- */
.badge{font-family:var(--mono);font-size:12px;font-weight:600;padding:5px 11px;border-radius:999px;letter-spacing:.04em;white-space:nowrap;}
.badge.hit{color:var(--hit);background:var(--hit-soft);border:1px solid rgba(198,241,53,.35);}
.badge.miss{color:var(--miss);background:var(--miss-soft);border:1px solid rgba(255,176,32,.35);}

/* ---------- inputs ---------- */
.stTextInput label{color:var(--dim)!important;font-size:13px!important;}
.stTextInput>div>div>input{background:var(--panel)!important;border:1px solid var(--line-2)!important;border-radius:14px!important;
  height:52px;font-size:16px;color:var(--ink)!important;padding:0 18px!important;transition:border-color .15s,box-shadow .15s;}
.stTextInput>div>div>input:focus{border-color:var(--hit)!important;box-shadow:0 0 0 4px var(--hit-soft)!important;}
.stTextInput>div>div{background:transparent!important;border:none!important;}
.stButton>button{height:52px;border-radius:14px;font-weight:600;font-size:15px;border:1px solid var(--line-2);
  background:var(--panel);color:var(--ink);transition:transform .12s,border-color .15s,box-shadow .15s;}
.stButton>button:hover{border-color:var(--hit);color:var(--hit);transform:translateY(-1px);}
.stButton>button[kind="primary"]{background:var(--hit);color:#0B0D12;border:none;box-shadow:0 8px 24px rgba(198,241,53,.22);}
.stButton>button[kind="primary"]:hover{color:#0B0D12;box-shadow:0 10px 30px rgba(198,241,53,.38);}
.stButton>button[kind="primary"] p{color:#0B0D12;font-weight:700;}

/* ---------- trace ---------- */
.trace{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:22px;}
.pipe{display:flex;align-items:center;gap:0;margin-bottom:22px;flex-wrap:wrap;row-gap:10px;}
.node{display:flex;align-items:center;gap:9px;font-family:var(--mono);font-size:12.5px;color:var(--ink);
  background:var(--panel-2);border:1px solid var(--line-2);padding:9px 13px;border-radius:10px;}
.node i{width:8px;height:8px;border-radius:50%;background:var(--hit);}
.node.miss i{background:var(--miss);}
.node.skip{color:var(--faint);border-style:dashed;}
.node.skip i{background:var(--faint);}
.link{width:26px;height:1px;background:var(--line-2);}
.gauge{position:relative;height:10px;border-radius:999px;background:var(--panel-2);border:1px solid var(--line);margin:34px 0 10px 0;}
.gauge .zone{position:absolute;left:0;top:0;bottom:0;border-radius:999px 0 0 999px;background:linear-gradient(90deg,rgba(198,241,53,.05),rgba(198,241,53,.28));}
.gauge .pin{position:absolute;top:-7px;width:2px;height:22px;border-radius:2px;}
.gauge .pin span{position:absolute;bottom:26px;left:50%;transform:translateX(-50%);font-family:var(--mono);font-size:11px;white-space:nowrap;}
.gauge .pin.edge-r span{left:auto;right:-4px;transform:none;}
.gauge .pin.edge-l span{left:-4px;transform:none;}
.gauge .pin.below span{bottom:auto;top:26px;}
.gauge .pin.thr{background:var(--ink);}
.gauge .pin.thr span{color:var(--dim);}
.gauge .pin.dist.hit{background:var(--hit);box-shadow:0 0 12px var(--hit);}
.gauge .pin.dist.hit span{color:var(--hit);}
.gauge .pin.dist.miss{background:var(--miss);box-shadow:0 0 12px var(--miss);}
.gauge .pin.dist.miss span{color:var(--miss);}
.gauge-scale{display:flex;justify-content:space-between;font-family:var(--mono);font-size:11px;color:var(--faint);}
.kv{display:flex;gap:28px;flex-wrap:wrap;margin-top:20px;padding-top:18px;border-top:1px solid var(--line);}
.kv div{font-size:12px;color:var(--faint);font-family:var(--mono);text-transform:uppercase;letter-spacing:.08em;}
.kv b{display:block;font-size:20px;color:var(--ink);font-weight:600;margin-top:4px;text-transform:none;letter-spacing:0;}
.answer{margin-top:14px;background:var(--panel);border:1px solid var(--line);border-left:3px solid var(--hit);border-radius:14px;padding:18px 22px;}
.answer.miss{border-left-color:var(--miss);}
.answer .lab{font-family:var(--mono);font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--dim);margin-bottom:8px;}
.answer .txt{color:var(--ink);line-height:1.7;font-size:16px;}
.matched{font-family:var(--mono);font-size:13px;color:var(--dim);margin-top:12px;}
.matched b{color:var(--ink);font-weight:500;}

/* ---------- metrics ---------- */
.tiles{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;}
.tile{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px 20px;}
.tile .k{font-family:var(--mono);font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);}
.tile .v{font-family:var(--mono);font-size:32px;font-weight:600;color:var(--ink);margin-top:8px;}
.tile.accent .v{color:var(--hit);}
.tile .bar{height:4px;border-radius:4px;background:var(--panel-2);margin-top:12px;overflow:hidden;}
.tile .bar i{display:block;height:100%;background:var(--hit);border-radius:4px;transition:width .4s;}

/* ---------- expanders ---------- */
[data-testid="stExpander"]{background:var(--panel);border:1px solid var(--line)!important;border-radius:14px;}
[data-testid="stExpander"] summary:hover{color:var(--hit);}
.evaltable{width:100%;border-collapse:collapse;font-family:var(--mono);font-size:13px;margin-top:6px;}
.evaltable td,.evaltable th{padding:8px 10px;border-bottom:1px solid var(--line);text-align:left;color:var(--dim);}
.evaltable th{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--faint);font-weight:500;}
.evaltable tr.best td{color:var(--hit);font-weight:600;}
.footer{margin-top:56px;padding-top:18px;border-top:1px solid var(--line);font-family:var(--mono);font-size:12px;color:var(--faint);display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;}


/* ---------- sidebar (custom nav) ---------- */
[data-testid="stSidebar"]{background:var(--panel)!important;border-right:1px solid var(--line);}
[data-testid="stSidebarContent"]{padding-top:.4rem;}
[data-testid="stSidebarHeader"]{display:none;}
.side-brand{display:flex;align-items:center;gap:12px;padding:4px 2px 18px 2px;border-bottom:1px solid var(--line);margin-bottom:6px;}
.side-logo{width:38px;height:38px;border-radius:11px;background:var(--hit);color:#0B0D12;display:grid;place-items:center;font-size:19px;box-shadow:0 6px 18px rgba(198,241,53,.25);}
.side-name{font-family:var(--head);font-weight:800;font-size:17px;line-height:1.1;letter-spacing:-.02em;color:var(--ink);}
.side-tag{font-family:var(--mono);font-size:11px;color:var(--faint);margin-top:4px;}
.side-label{font-family:var(--mono);font-size:11px;letter-spacing:.14em;text-transform:uppercase;color:var(--faint);margin:20px 4px 8px 4px;}
[data-testid="stSidebar"] [data-testid="stPageLink"] a{border-radius:10px;padding:10px 12px;border:1px solid transparent;color:var(--dim);transition:background .15s,color .15s,border-color .15s;}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover{background:var(--panel-2);color:var(--ink);}
[data-testid="stSidebar"] [data-testid="stPageLink"] a p{font-weight:500;font-size:14.5px;}
[data-testid="stSidebar"] [class*="st-key-nav-"][class*="-active"] a{background:var(--hit-soft)!important;border-color:rgba(198,241,53,.32)!important;box-shadow:inset 3px 0 0 var(--hit);}
[data-testid="stSidebar"] [class*="st-key-nav-"][class*="-active"] a p,
[data-testid="stSidebar"] [class*="st-key-nav-"][class*="-active"] a span{color:var(--hit)!important;font-weight:600;}
.side-card{background:var(--panel-2);border:1px solid var(--line);border-radius:12px;padding:14px;margin-top:22px;font-family:var(--mono);font-size:12px;color:var(--dim);line-height:1.9;}
.side-card b{color:var(--ink);font-weight:500;}
.side-card .row{display:flex;justify-content:space-between;gap:10px;}
.side-card i{display:inline-block;width:7px;height:7px;border-radius:50%;background:var(--hit);box-shadow:0 0 8px var(--hit);margin-right:7px;}
[data-testid="stSidebar"] .stSlider label p{font-size:13px;color:var(--dim);}
[data-testid="stSidebar"] .stButton>button{height:42px;font-size:14px;width:100%;}

/* ---------- boot loader (see ui/loader.py) ---------- */
.boot{background:var(--panel);border:1px solid var(--line);border-radius:18px;padding:24px;margin:6px 0 10px 0;}
.boot-head{display:flex;justify-content:space-between;align-items:flex-end;gap:16px;margin-bottom:16px;}
.boot-title{font-family:var(--head);font-weight:800;font-size:22px;letter-spacing:-.02em;color:var(--ink);}
.boot-sub{font-size:13px;color:var(--dim);margin-top:4px;}
.boot-pct{font-family:var(--mono);font-size:38px;font-weight:600;color:var(--hit);line-height:1;}
.boot-bar{height:16px;border-radius:4px;background:var(--panel-2);overflow:hidden;
  -webkit-mask-image:repeating-linear-gradient(90deg,#000 0 7px,transparent 7px 10px);
  mask-image:repeating-linear-gradient(90deg,#000 0 7px,transparent 7px 10px);}
.boot-bar i{display:block;height:100%;background:linear-gradient(90deg,#7FA31A,var(--hit));transition:width .25s ease;}
.boot.done .boot-pct{color:var(--hit);}
.boot-phases{display:flex;gap:8px;margin:16px 0;flex-wrap:wrap;}
.phase{font-family:var(--mono);font-size:12px;color:var(--faint);padding:6px 11px;border-radius:8px;border:1px solid var(--line);}
.phase.on{color:var(--ink);border-color:var(--hit);background:var(--hit-soft);}
.phase.ok{color:var(--hit);}
.phase.on::before{content:"";display:inline-block;width:6px;height:6px;border-radius:50%;background:var(--hit);margin-right:8px;animation:pulse 1s ease-in-out infinite;}
.phase.ok::before{content:"✓ ";}
.boot-log{background:#080A0F;border:1px solid var(--line);border-radius:10px;padding:12px 14px;font-family:var(--mono);font-size:12.5px;line-height:1.75;color:var(--dim);min-height:104px;}
.boot-log .ok{color:var(--hit);} .boot-log .cur{color:var(--ink);}
.boot-log .cur::after{content:"▍";color:var(--hit);animation:blink 1s steps(1) infinite;margin-left:3px;}
@keyframes pulse{50%{opacity:.3}} @keyframes blink{50%{opacity:0}}
@media(prefers-reduced-motion:reduce){.phase.on::before,.boot-log .cur::after{animation:none}.step,.stButton>button{transition:none}}

/* ---------- responsive ---------- */
@media(max-width:820px){
  .stats,.tiles{grid-template-columns:repeat(2,1fr);} .steps3{grid-template-columns:1fr;}
  .hero2 p{font-size:16px;} .boot-pct{font-size:28px;}
}
</style>
"""


def apply_theme() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def topbar(status: str = "in-memory cache") -> None:
    st.markdown(
        f'<div class="topbar"><div class="wordmark">semantic<b>·</b>cache</div>'
        f'<div class="chip"><i></i>{status}</div></div>',
        unsafe_allow_html=True,
    )


def hero(eyebrow: str, headline_html: str, sub: str, stats: list[tuple[str, str, str]]) -> None:
    cells = "".join(
        f'<div class="stat"><div class="k">{k}</div><div class="v">{v}<small>{u}</small></div></div>'
        for k, v, u in stats
    )
    st.markdown(
        f'<div class="hero2"><div class="eyebrow">{eyebrow}</div><h1>{headline_html}</h1><p>{sub}</p>'
        f'<div class="stats">{cells}</div></div>',
        unsafe_allow_html=True,
    )


def section(num: str, title: str, hint: str = "") -> None:
    h = f'<span class="hint">{hint}</span>' if hint else ""
    st.markdown(f'<div class="sec"><span class="n">{num}</span><h2>{title}</h2>{h}</div>', unsafe_allow_html=True)


def steps(items: list[tuple[str, str, str]]) -> None:
    html = "".join(f'<div class="step"><div class="num">{n}</div><h3>{t}</h3><p>{b}</p></div>' for n, t, b in items)
    st.markdown(f'<div class="steps3">{html}</div>', unsafe_allow_html=True)


def demo_table(rows: list[tuple[str, str, str]]) -> None:
    """rows: (question, 'hit'|'miss', explanation)"""
    html = ""
    for q, kind, why in rows:
        label = "HIT" if kind == "hit" else "MISS"
        html += f'<div class="demo-row"><span class="q">{q}</span><span class="badge {kind}">{label}</span><span class="why">{why}</span></div>'
    st.markdown(f'<div class="demo-table">{html}</div>', unsafe_allow_html=True)


def trace(hit: bool, latency_ms: float, distance, threshold: float, matched, answer: str) -> None:
    kind = "hit" if hit else "miss"
    badge = '<span class="badge hit">HIT · $0 LLM COST</span>' if hit else '<span class="badge miss">MISS · CALLED GROQ</span>'
    last_node = "serve cached answer" if hit else "call Groq + store"
    skip = "" if hit else " skip"
    pipe = (
        '<div class="node"><i></i>embed query</div><div class="link"></div>'
        '<div class="node"><i></i>search cache</div><div class="link"></div>'
        f'<div class="node {kind}"><i></i>distance &le; threshold?</div><div class="link"></div>'
        f'<div class="node {kind}"><i></i>{last_node}</div>'
    )
    gauge = ""
    if distance is not None:
        dpos = max(0.0, min(distance / THRESHOLD_SCALE, 1.0)) * 100
        tpos = max(0.0, min(threshold / THRESHOLD_SCALE, 1.0)) * 100
        d_edge = " edge-r" if dpos > 82 else (" edge-l" if dpos < 8 else "")
        t_edge = " edge-r" if tpos > 82 else (" edge-l" if tpos < 8 else "")
        if abs(dpos - tpos) < 18:
            t_edge += " below"
        gauge = (
            f'<div class="gauge"><div class="zone" style="width:{tpos:.1f}%"></div>'
            f'<div class="pin thr{t_edge}" style="left:{tpos:.1f}%"><span>threshold {threshold}</span></div>'
            f'<div class="pin dist {kind}{d_edge}" style="left:{dpos:.1f}%"><span>distance {distance:.3f}</span></div></div>'
            f'<div class="gauge-scale"><span>0.00 identical</span><span>{THRESHOLD_SCALE:.2f}</span></div>'
        )
    dist_txt = f"{distance:.4f}" if distance is not None else "n/a"
    kv = (
        f'<div class="kv"><div>latency<b>{latency_ms:.1f} ms</b></div>'
        f'<div>distance<b>{dist_txt}</b></div><div>threshold<b>{threshold}</b></div>'
        f'<div>result<b>{badge}</b></div></div>'
    )
    st.markdown(f'<div class="trace"><div class="pipe">{pipe}</div>{gauge}{kv}</div>', unsafe_allow_html=True)
    src = "from cache" if hit else "from Groq LLM"
    matched_html = f'<div class="matched">matched &rarr; <b>{matched}</b></div>' if hit and matched else ""
    st.markdown(
        f'<div class="answer {kind}"><div class="lab">Response · {src}</div><div class="txt">{answer}</div>{matched_html}</div>',
        unsafe_allow_html=True,
    )


def tiles(stats: dict) -> None:
    rate = float(stats["hit_rate"])
    html = (
        f'<div class="tile"><div class="k">Total requests</div><div class="v">{stats["total_requests"]}</div></div>'
        f'<div class="tile accent"><div class="k">Hit rate</div><div class="v">{rate}%</div>'
        f'<div class="bar"><i style="width:{rate}%"></i></div></div>'
        f'<div class="tile"><div class="k">LLM calls saved</div><div class="v">{stats["cache_hits"]}</div></div>'
        f'<div class="tile"><div class="k">Cache entries</div><div class="v">{stats["entries"]}</div></div>'
    )
    st.markdown(f'<div class="tiles">{html}</div>', unsafe_allow_html=True)


def eval_table() -> None:
    rows = [("0.15", "0.80", ""), ("0.25", "0.83", "best"), ("0.30", "0.71", "")]
    body = "".join(f'<tr class="{c}"><td>{t}</td><td>{f}</td></tr>' for t, f, c in rows)
    st.markdown(f'<table class="evaltable"><tr><th>Threshold</th><th>F1</th></tr>{body}</table>', unsafe_allow_html=True)


def footer() -> None:
    st.markdown(
        f'<div class="footer"><span>Streamlit · all-MiniLM-L6-v2 · Groq free tier</span><span>UI {UI_VERSION}</span></div>',
        unsafe_allow_html=True,
    )


def sidebar_nav(active: str) -> None:
    """Brand + page links. ``active`` is "overview" or "playground".

    Call first inside the page, before other sidebar widgets. Each link sits in
    a keyed container so the active one can be styled (Streamlit exposes no
    stable active-link attribute).
    """
    with st.sidebar:
        st.markdown(
            '<div class="side-brand"><div class="side-logo"><svg width="20" height="20" viewBox="0 0 24 24" fill="#0B0D12"><path d="M13 2 4 14h7l-1 8 9-12h-7z"/></svg></div><div>'
            '<div class="side-name">Semantic Cache</div><div class="side-tag">support assistant</div></div></div>'
            '<div class="side-label">Navigate</div>',
            unsafe_allow_html=True,
        )
        with st.container(key="nav-overview" + ("-active" if active == "overview" else "")):
            st.page_link("app.py", label="Overview", icon=":material/home:")
        with st.container(key="nav-playground" + ("-active" if active == "playground" else "")):
            st.page_link("pages/1_Semantic_Cache.py", label="Playground", icon=":material/bolt:")


def sidebar_section(label: str) -> None:
    with st.sidebar:
        st.markdown(f'<div class="side-label">{label}</div>', unsafe_allow_html=True)


def sidebar_status() -> None:
    with st.sidebar:
        st.markdown(
            '<div class="side-card">'
            '<div class="row"><span><i></i>cache</span><b>in-memory</b></div>'
            '<div class="row"><span>model</span><b>MiniLM-L6</b></div>'
            '<div class="row"><span>llm</span><b>Groq</b></div>'
            f'<div class="row"><span>ui</span><b>{UI_VERSION}</b></div></div>',
            unsafe_allow_html=True,
        )
