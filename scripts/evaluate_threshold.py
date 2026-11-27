# scripts/evaluate_threshold.py
# Usage: uv run python scripts/evaluate_threshold.py
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from redis.exceptions import RedisError

from backend.app.dependencies.resources import resources
from backend.app.services.semantic_cache import SemanticCacheService

# 1. Seed questions - ground truth
SEED = [
    ("What is semantic caching?", "Semantic caching reuses LLM responses for similar queries."),
    ("How do I reset my password?", "Go to Settings > Security > Reset Password."),
    ("What is your refund policy?", "30-day refund, no questions asked."),
]

# 2. Test set: (query, should_hit)
TESTS = [
    # Should HIT - true paraphrases
    ("What is semantic caching?", True),
    ("Explain semantic caching", True),
    ("What does semantic cache mean?", True),
    ("How can I change my password?", True),
    ("Tell me about refunds", True),
    ("How do I get my money back?", True),  # paraphrase of refund

    # Should MISS - hard negatives (similar words, different meaning)
    ("How do I reset my username?", False),  # similar to password, but different!
    ("What is semantic search?", False),  # sounds like semantic caching, but different
    ("What is my password?", False),  # asks for password, not reset
    ("What is your return policy?", False),  # return != refund in your data
    ("How do I change my email?", False),  # similar structure to password change

    # Should MISS - easy negatives
    ("What is the weather today?", False),
    ("How do I cook pasta?", False),
]

def run(thresholds=(0.15, 0.25, 0.30, 0.40, 0.50)):
    # FIX: Init resources FIRST - loads Redis + embedding model
    # FastAPI does this in lifespan, script must do it manually
    resources.initialize()

    svc = SemanticCacheService()
    svc.initialize()

    print(f"\n{'Threshold':<10} | {'TP':<3} {'FP':<3} {'FN':<3} {'TN':<3} | {'Precision':<9} {'Recall':<6} | Avg Lookup")
    print("-" * 85)

    for thresh in thresholds:
        # Clear before each threshold run
        try:
            svc.clear()
        except (RedisError, RuntimeError) as e:
            print(f"Clear skipped (cache may be empty): {e}")

        for q, a in SEED:
            svc.store(q, a)

        tp = fp = fn = tn = 0
        latencies = []

        for query, should_hit in TESTS:
            t0 = time.time()
            res = svc.search(query, threshold=thresh)
            latencies.append((time.time() - t0) * 1000)
            hit = len(res) > 0

            if hit and should_hit:
                tp += 1
            elif hit and not should_hit:
                fp += 1
            elif not hit and should_hit:
                fn += 1
            else:
                tn += 1

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        avg_lat = sum(latencies) / len(latencies) if latencies else 0

        print(
            f"{thresh:<10.2f} | {tp:<3} {fp:<3} {fn:<3} {tn:<3} | "
            f"{precision:<9.2f} {recall:<6.2f} | {avg_lat:.1f}ms"
        )

    # Cleanup
    resources.close()
    print("\nDone. Best threshold = high Precision + high Recall.")

if __name__ == "__main__":
    run()