# app.py - Streamlit entry point
import streamlit as st

st.set_page_config(page_title="Semantic Cache Assistant", layout="wide")

st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sora:wght@600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

/* --- FONT SYSTEM - shared with pages/1_Semantic_Cache.py --- */
html, body, p, div, span, label, input, button, [class*="css"] {
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
  -webkit-font-smoothing: antialiased;
}
h1, h2, h3, .hero h1, .card h3 {
  font-family: 'Sora', 'Inter', sans-serif !important;
  letter-spacing: -0.02em;
  font-weight: 700;
}
code {
  font-family: 'JetBrains Mono', monospace !important;
  letter-spacing: -0.01em;
}

/* --- HERO + CARDS --- */
.hero { background: linear-gradient(135deg, #0F172A 0%, #4F46E5 55%, #06B6D4 100%);
        padding: 36px 32px; border-radius: 20px; color: white; margin-bottom: 24px; }
.hero h1 { font-size: 40px !important; font-weight: 800 !important; line-height: 1.1; margin: 0 0 8px 0; color: white; }
.hero p { font-size: 17px !important; line-height: 1.6; opacity: 0.9; margin: 0; font-weight: 400; }
.pill { display: inline-block; background: rgba(255,255,255,0.18); padding: 5px 12px;
        border-radius: 999px; font-size: 13px; margin: 4px 6px 0 0; }
.card { background: white; border: 1px solid #E5E7EB; border-radius: 16px;
        padding: 20px; box-shadow: 0 4px 14px rgba(0,0,0,0.06); height: 100%; }
.card h3 { margin-top: 0; font-size: 19px !important; }
.card p { font-size: 15px !important; line-height: 1.6; color: #334155; }
.demo-box { background: #F0FDF4; border: 1px solid #BBF7D0; border-radius: 14px; padding: 18px; }
.demo-box code { background: #DCFCE7; padding: 2px 8px; border-radius: 6px; }
</style>
""",
    unsafe_allow_html=True,
)

st.markdown(
    """
<div class="hero">
  <h1>⚡ Semantic Cache Assistant</h1>
  <p>A customer-support AI that reuses answers for similar questions — instead of paying for the LLM every time.</p>
  <div style="margin-top:14px;">
    <span class="pill">Project 1 — Semantic Caching</span>
    <span class="pill">100% Free Stack</span>
    <span class="pill">Threshold 0.25 • F1 0.83</span>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

c1, c2, c3 = st.columns(3)
with c1:
    st.markdown('<div class="card"><h3>🧠 How it works</h3><p>Question → Embedding → Search cache by meaning, not keywords.<br><br>HIT = reuse answer ($0) • MISS = call Groq + store it.</p></div>', unsafe_allow_html=True)
with c2:
    st.markdown('<div class="card"><h3>▶ Try it</h3><p>1. Click <b>Semantic Cache</b> in sidebar<br>2. Ask in Playground<br>3. Watch Trace: HIT vs MISS, distance, latency</p></div>', unsafe_allow_html=True)
with c3:
    st.markdown('<div class="card"><h3>📊 Why it matters</h3><p>Same question asked 100 ways = 1 LLM call.<br><br>Lower cost, lower latency, same answer.</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    """
<div class="demo-box">
<b>Try this demo:</b><br>
<code>What is semantic caching?</code> → HIT &nbsp;•&nbsp;
<code>Explain semantic cache</code> → HIT (paraphrase) &nbsp;•&nbsp;
<code>How do I reset my username?</code> → MISS (hard negative)
</div>
""",
    unsafe_allow_html=True,
)

st.caption("Stack: Streamlit + Sentence Transformers (all-MiniLM-L6-v2) + Groq Free Tier + in-memory cache")