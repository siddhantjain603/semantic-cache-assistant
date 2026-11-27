import csv
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "results" / "benchmark_latency.csv"
OUT_PATH = ROOT / "results" / "benchmark_latency.png"


def run():
    entries, hit_rate, hit_ms, miss_ms = [], [], [], []
    with open(CSV_PATH, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            entries.append(int(row["entries"]))
            hit_rate.append(float(row["hit_rate_pct"]))
            hit_ms.append(float(row["avg_hit_ms"]))
            miss_ms.append(float(row["avg_miss_ms"]))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    # Chart 1: HIT rate grows with cache size
    bars = ax1.bar([str(e) for e in entries], hit_rate, color="#4F46E5")
    ax1.set_title("HIT rate vs Cache Size", fontweight="bold")
    ax1.set_xlabel("Cached entries")
    ax1.set_ylabel("HIT rate (%)")
    ax1.set_ylim(0, 100)
    for bar, v in zip(bars, hit_rate):
        ax1.text(bar.get_x() + bar.get_width() / 2, v + 2, f"{v:.0f}%", ha="center", fontweight="bold")

    # Chart 2: Latency stays flat
    ax2.plot(entries, hit_ms, marker="o", label="Avg HIT", color="#16A34A")
    ax2.plot(entries, miss_ms, marker="s", label="Avg MISS", color="#DC2626")
    ax2.set_title("Lookup Latency vs Cache Size", fontweight="bold")
    ax2.set_xlabel("Cached entries")
    ax2.set_ylabel("Latency (ms)")
    ax2.legend()
    ax2.grid(alpha=0.3)

    fig.suptitle("Semantic Cache Benchmark - Threshold 0.25", fontweight="bold")
    fig.tight_layout()
    fig.savefig(OUT_PATH, dpi=200)
    print(f"Saved: {OUT_PATH}")
    print(f"Data: entries={entries}, hit_rate={hit_rate}%, hit_ms={hit_ms}, miss_ms={miss_ms}")


if __name__ == "__main__":
    run()