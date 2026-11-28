# pages/1_Semantic_Cache.py - Portfolio page for Project 1
# Pattern for all 4 projects: Playground (top) + Trace (middle) + Analytics (bottom)
# 100% Free: Groq Free Tier + local embeddings + in-memory cache (no Redis on HF Spaces)

import time

import streamlit as st

from ui.loader import load_with_progress
from ui.theme import (
    apply_theme, eval_table, footer, hero, section, sidebar_nav, sidebar_section,
    sidebar_status, tiles, topbar, trace,
)

st.set_page_config(page_title="Semantic Cache - Portfolio", page_icon="⚡", layout="wide")
apply_theme()
sidebar_nav("playground")

topbar()
hero(
    "Playground",
    "Watch the cache<br><em>decide.</em>",
    "Ask a question. The trace shows whether it matched something already cached, how close it was, and what it cost.",
    [("Threshold", f"{st.session_state.get('threshold', 0.25)}", "cosine"), ("Embedding", "384", "dims"), ("Mode", "RAM", "in-memory"), ("LLM", "Groq", "on MISS")],
)

# --- Session state ---
SEEDS = [
    ("What is semantic caching?", "Semantic caching stores responses for similar queries and reuses them instead of calling the LLM again."),
    ("How do I reset my password?", "Go to Settings > Security > Reset Password, then follow the email link."),
    ("What is your refund policy?", "You can request a refund within 30 days of purchase from Settings > Billing."),
]


def _seed(cache):
    """Store the demo examples, yielding after each so the loader can show progress."""
    for q, a in SEEDS:
        cache.store(q, a)
        yield


def _build():
    # Imported here, not at the top of the file, so the page renders before
    # PyTorch / sentence-transformers start importing.
    from core.cache import PortfolioSemanticCache

    return PortfolioSemanticCache(threshold=0.25)


if "cache" not in st.session_state:
    st.session_state.cache = load_with_progress(
        build=_build,
        seed=_seed,
        n_seeds=len(SEEDS),
    )
    st.session_state.history = []

if "threshold" not in st.session_state:
    st.session_state.threshold = 0.25

# --- Sidebar ---
sidebar_section("Controls")
with st.sidebar:
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
    st.caption("Threshold eval (from README)")
    eval_table()
sidebar_status()

# --- 1. Playground ---
section("01", "Playground")
col1, col2 = st.columns([5, 1], vertical_alignment="bottom")
with col1:
    question = st.text_input("Ask a customer-support question", placeholder="e.g. How can I change my password?")
with col2:
    ask = st.button("Ask", type="primary", use_container_width=True)

if ask and question.strip():
    start = time.time()
    answer, matched, distance, hit = st.session_state.cache.lookup(question)
    if not hit:
        # MISS -> call Groq (Free Tier)
        from core.llm import ask_groq  # lazy: keeps first paint fast

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
    section("02", "Trace", "last request")
    last = st.session_state.history[-1]
    trace(last["hit"], last["latency"], last["distance"], st.session_state.threshold, last["matched"], last["a"])

    section("03", "History", f"{len(st.session_state.history)} requests")
    for h in reversed(st.session_state.history):
        icon = "🟢" if h["hit"] else "🟠"
        with st.expander(f"{icon} {h['q']}"):
            st.write(h["a"])

# --- 3. Analytics ---
section("04" if st.session_state.history else "02", "Analytics")
tiles(st.session_state.cache.stats)
footer()
