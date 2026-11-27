# core/llm.py - Groq wrapper for portfolio (Free Tier)
import os

from groq import Groq


def ask_groq(question: str) -> str:
    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        return "Demo answer (no GROQ_API_KEY set): Semantic caching reuses answers for similar questions."
    client = Groq(api_key=api_key)
    resp = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
        messages=[
            {"role": "system", "content": "You are a helpful customer-support assistant. Answer concisely."},
            {"role": "user", "content": question},
        ],
        temperature=0.2,
    )
    return resp.choices[0].message.content or ""
