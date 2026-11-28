# app.py - Streamlit entry point (UI v2)
import streamlit as st

from ui.theme import apply_theme, demo_table, footer, hero, section, sidebar_nav, sidebar_status, steps, topbar

st.set_page_config(page_title="Semantic Cache Assistant", page_icon="⚡", layout="wide")
apply_theme()
sidebar_nav("overview")
sidebar_status()

topbar()
hero(
    "Semantic caching for LLM apps",
    "Ask once.<br><em>Pay once.</em>",
    "A customer-support assistant that recognises questions it has already answered, by meaning rather than keywords, "
    "and serves the saved reply instead of calling the LLM again.",
    [("Threshold", "0.25", "cosine"), ("F1 score", "0.83", "eval"), ("Embedding", "384", "dims"), ("Stack cost", "$0", "free tier")],
)

section("01", "How it works")
steps([
    ("STEP 1", "Embed", "Every question becomes a 384-dimension vector using a local sentence-transformer. No API call, no cost."),
    ("STEP 2", "Search", "The vector is compared with every cached question. If one is within the distance threshold, it's a match."),
    ("STEP 3", "Serve or call", "HIT: reuse the stored answer for free. MISS: call Groq once, then store the answer for next time."),
])

section("02", "Try it", "open Semantic Cache in the sidebar")
demo_table([
    ("What is semantic caching?", "hit", "exact seed question"),
    ("Explain semantic cache", "hit", "paraphrase, same meaning"),
    ("How do I reset my username?", "miss", "hard negative, must not match the password question"),
])
footer()
