import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.cache import PortfolioSemanticCache

# 10 real support topics x 10 phrasings = 100 cached entries
TOPICS = [
    ("password reset", "Go to Settings > Security > Reset Password, then follow the email link."),
    ("refund policy", "You can request a refund within 30 days of purchase from Settings > Billing."),
    ("semantic caching", "Semantic caching stores responses for similar queries and reuses them instead of calling the LLM again."),
    ("change email", "Go to Settings > Profile > Email to update your email address."),
    ("cancel subscription", "Go to Settings > Billing > Cancel Subscription. You keep access until the period ends."),
    ("update payment", "Go to Settings > Billing > Payment Method to update your card."),
    ("delete account", "Go to Settings > Account > Delete Account. This is permanent."),
    ("two factor auth", "Go to Settings > Security > Two-Factor Auth to turn on 2FA."),
    ("download invoice", "Go to Settings > Billing > Invoices to download any invoice as PDF."),
    ("contact support", "Email support@example.com or use the Help chat in the app."),
]

TEMPLATES = [
    "How do I {t}?",
    "How can I {t}?",
    "I need help with {t}.",
    "Can you help me with {t}?",
    "What is the process for {t}?",
    "Explain {t}.",
    "Tell me about {t}.",
    "Where do I find {t}?",
    "How to do {t}?",
    "I forgot how to do {t}, help?",
]

# HIT queries: new paraphrases NOT stored verbatim, same meaning
HIT_QUERIES = [
    "How do I reset my password?",
    "Can I get a refund?",
    "What does semantic caching mean?",
    "How do I change my email address?",
    "How to cancel my plan?",
    "How do I update my card?",
    "How do I delete my account?",
    "How to enable two factor?",
    "Where is my invoice?",
    "How do I reach support?",
    "I forgot my password, what now?",
    "Refund rules please",
    "Explain semantic cache",
    "Update my email please",
    "Stop my subscription",
    "Change payment method",
    "Remove my account",
    "Turn on 2FA",
    "Get my invoice PDF",
    "Talk to support team",
]

# MISS queries: unrelated, should NOT match
MISS_QUERIES = [
    "How do I cook pasta?",
    "What is the weather today?",
    "How to train a dog?",
    "What is quantum physics?",
    "Best movies of 2024?",
    "How to fix a bicycle tire?",
    "What is the capital of Japan?",
    "How to grow tomatoes?",
    "Explain black holes",
    "How to play guitar?",
    "What is my username?",
    "How to bake bread?",
    "What is photosynthesis?",
    "How to learn Spanish?",
    "Best laptop for coding?",
    "How to change a tire?",
    "What is blockchain?",
    "How to meditate?",
    "How to write a resume?",
    "What is the stock price today?",
]


def build_entries(n):
    entries = []
    for topic, answer in TOPICS:
        for tmpl in TEMPLATES:
            q = tmpl.format(t=topic)
            entries.append((q, answer))
            if len(entries) >= n:
                return entries
    return entries


def measure(cache, queries):
    latencies = []
    hits = 0
    for q in queries:
        t0 = time.time()
        _ans, _matched, _dist, hit = cache.lookup(q)
        latencies.append((time.time() - t0) * 1000)
        if hit:
            hits += 1
    avg = sum(latencies) / len(latencies) if latencies else 0
    return avg, hits, len(queries)


def run():
    print("\nM4 Benchmark: HIT vs MISS latency with 100+ entries")
    print("Cache: PortfolioSemanticCache (in-memory), threshold 0.25")
    print(f"{'Entries':<10} | {'Avg HIT':<12} {'HIT rate':<10} | {'Avg MISS':<12} {'MISS rate':<10}")
    print("-" * 72)

    rows = []
    for n in [10, 50, 100]:
        cache = PortfolioSemanticCache(threshold=0.25)
        for q, a in build_entries(n):
            cache.store(q, a)

        hit_avg, hit_n, hit_total = measure(cache, HIT_QUERIES)
        miss_avg, miss_n, miss_total = measure(cache, MISS_QUERIES)
        # For MISS queries, hit_n should be ~0. MISS rate = 1 - hit_n/total
        miss_rate = 1 - (miss_n / miss_total) if miss_total else 0
        hit_rate = hit_n / hit_total if hit_total else 0

        print(f"{n:<10} | {hit_avg:<12.1f} {hit_rate*100:<10.1f}% | {miss_avg:<12.1f} {miss_rate*100:<10.1f}%")
        rows.append((n, round(hit_avg, 1), round(hit_rate * 100, 1), round(miss_avg, 1), round(miss_rate * 100, 1)))

    # Save CSV for README / report
    out_dir = Path(__file__).resolve().parent.parent / "results"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "benchmark_latency.csv"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write("entries,avg_hit_ms,hit_rate_pct,avg_miss_ms,miss_rate_pct\n")
        f.writelines(f"{r[0]},{r[1]},{r[2]},{r[3]},{r[4]}\n" for r in rows)

    print(f"\nSaved: {out_path}")
    print("Note: HIT and MISS lookup latency are similar (both are vector search).")
    print("The saving is NOT in lookup time - it is in avoiding the LLM call (seconds + $).")
    print("Next M4 pointers will quantify LLM calls avoided + cost savings.")


if __name__ == "__main__":
    run()