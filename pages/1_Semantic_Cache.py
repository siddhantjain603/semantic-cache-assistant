# pages/1_Semantic_Cache.py - Portfolio page for Project 1
# Pattern for all 4 projects: Playground (top) + Trace (middle) + Analytics (bottom)
# 100% Free: Groq Free Tier + local embeddings + in-memory cache (no Redis on HF Spaces)

import time

import streamlit as st

from core.cache import PortfolioSemanticCache
from core.llm import ask_groq  # your Groq wrapper - GROQ_API_KEY from HF Secrets

st.set_page_config(page_title="Semantic Cache - Portfolio", layout="wide")
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sora:wght@600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');

/* --- FONT SYSTEM --- */
html, body, p, div, span, label, input, button, [class*="css"] {
  font-family: 'Inter', system-ui, -apple-system, sans-serif !important;
  -webkit-font-smoothing: antialiased;
}

/* Headings = Sora - bolder, tighter, more premium */
h1, h2, h3, .hero h1, .card h3, [data-testid="stMetricLabel"] {
  font-family: 'Sora', 'Inter', sans-serif !important;
  letter-spacing: -0.02em;
  font-weight: 700;
}

.hero h1 {
  font-size: 40px !important;
  font-weight: 800 !important;
  line-height: 1.1;
}

.hero p {
  font-family: 'Inter', sans-serif !important;
  font-size: 17px !important;
  line-height: 1.6;
  font-weight: 400;
}

.card h3 { font-size: 19px !important; }
.card p { font-size: 15px !important; line-height: 1.6; color: #334155; }

/* Numbers / latency / distance = mono, looks like a dev tool */
code, [data-testid="stMetricValue"], .trace-card b {
  font-family: 'JetBrains Mono', monospace !important;
  letter-spacing: -0.01em;
}

/* Bigger, rounder primary button */
.stButton > button[kind="primary"] { background: #4F46E5; border-radius: 12px; height: 48px; font-size: 16px; }
/* Metric cards */
[data-testid="stMetric"] { background: white; border: 1px solid #E5E7EB; border-radius: 14px; padding: 14px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
/* Trace card */
.trace-card { background: #F8FAFC; border: 1px solid #E2E8F0; border-left: 5px solid #4F46E5; border-radius: 12px; padding: 16px 18px; }
.badge-hit { background: #DCFCE7; color: #166534; padding: 4px 10px; border-radius: 999px; font-weight: 700; }
.badge-miss { background: #FEE2E2; color: #991B1B; padding: 4px 10px; border-radius: 999px; font-weight: 700; }
.stTextInput > div > div > input { border-radius: 12px; height: 48px; font-size: 16px; }
</style>
""",
    unsafe_allow_html=True,
)
st.title("1_Semantic_Cache Assistant")
st.caption("Same logic as production (FastAPI + Redis). Portfolio mode uses in-memory cache so it runs on HF Spaces Free.")

# --- Session state ---
if "cache" not in st.session_state:
    # This shows IMMEDIATELY, before the heavy model loads
    with st.status("Warming up the assistant...", expanded=True) as status:
        st.write("Step 1/3: Loading embedding model (all-MiniLM-L6-v2, 90MB, free, local)...")
        st.write("First time only: downloading once. After that it's instant.")
        progress = st.progress(10, text="Loading model...")

        st.session_state.cache = PortfolioSemanticCache(threshold=0.25)

        progress.progress(70, text="Step 2/3: Seeding demo examples...")
        # Seed with 3 examples so first demo shows a HIT
        seeds = [
            ("What is semantic caching?", "Semantic caching stores responses for similar queries and reuses them instead of calling the LLM again."),
            ("How do I reset my password?", "Go to Settings > Security > Reset Password, then follow the email link."),
            ("What is your refund policy?", "You can request a refund within 30 days of purchase from Settings > Billing."),
        ]
        for q, a in seeds:
            st.session_state.cache.store(q, a)

        progress.progress(100, text="Ready!")
        st.write("Step 3/3: Ready!")
        status.update(label="Ready! Ask a question below.", state="complete", expanded=False)

    st.session_state.history = []

if "threshold" not in st.session_state:
    st.session_state.threshold = 0.25

# --- Sidebar ---
with st.sidebar:
    st.header("Controls")
    st.session_state.threshold = st.slider(
        "Distance Threshold", 0.05, 0.60, st.session_state.threshold, 0.05,
        help="0.25 chosen by eval (F1 0.83). Lower = stricter, Higher = looser.",
    )
    st.session_state.cache.threshold = st.session_state.threshold
    if st.button("Clear Cache"):
        st.session_state.cache.clear()
        st.session_state.history = []
        st.rerun()
    st.divider()
    st.markdown("**Eval (from README)**")
    st.markdown("| Threshold | F1 |\n|---|---|\n| 0.15 | 0.80 |\n| **0.25** | **0.83** |\n| 0.30 | 0.71 |")

# --- 1. Playground ---
st.subheader("Playground")
col1, col2 = st.columns([3, 1])
with col1:
    question = st.text_input("Ask a customer-support question", placeholder="e.g. How can I change my password?")
with col2:
    ask = st.button("Ask", type="primary", use_container_width=True)

if ask and question.strip():
    start = time.time()
    answer, matched, distance, hit = st.session_state.cache.lookup(question)
    if not hit:
        # MISS -> call Groq (Free Tier)
        answer = ask_groq(question)
        st.session_state.cache.store(question, answer)
        st.session_state.cache.llm_calls += 1
        # lookup() already counted miss, don't double count
    latency = (time.time() - start) * 1000
    st.session_state.history.append({
        "q": question, "a": answer, "hit": hit,
        "matched": matched, "distance": distance, "latency": latency,
    })

# --- 2. Trace ---
if st.session_state.history:
    st.subheader("Trace - Last Request")
    last = st.session_state.history[-1]
    badge_html = '<span class="badge-hit">🟢 HIT • $0 LLM cost</span>' if last["hit"] else '<span class="badge-miss">🔴 MISS • Called Groq LLM</span>'
    st.markdown(f'<div class="trace-card">{badge_html} &nbsp;|&nbsp; Latency: <b>{last["latency"]:.1f} ms</b></div>', unsafe_allow_html=True)
    if last["hit"]:
        st.markdown(f"**Matched:** `{last['matched']}`")
        st.markdown(f"**Distance:** `{last['distance']:.4f}`  (threshold `{st.session_state.threshold}`)")
    else:
        st.markdown(f"**Closest distance:** `{last['distance']:.4f}`" if last["distance"] is not None else "Cache was empty")
        st.markdown("No match under threshold, so we called the LLM and stored the answer.")
    st.markdown(f"**Answer:** {last['a']}")

    st.subheader("Chat History")
    for h in reversed(st.session_state.history):
        icon = "🟢" if h["hit"] else "🔴"
        with st.expander(f"{icon} {h['q']}"):
            st.write(h["a"])

# --- 3. Analytics ---
st.subheader("Analytics")
s = st.session_state.cache.stats
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Requests", s["total_requests"])
c2.metric("Hit Rate", f"{s['hit_rate']}%")
c3.metric("LLM Calls Saved", s["cache_hits"])
c4.metric("Cache Entries", s["entries"])

st.info("Try this demo: 1) Ask 'What is semantic caching?' (HIT)  2) Ask 'Explain semantic cache' (HIT - paraphrase)  3) Ask 'How do I reset my username?' (MISS - hard negative, should NOT match password)")