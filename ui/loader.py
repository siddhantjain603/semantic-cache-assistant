"""UI v2 boot loader shown while the embedding model loads.

Design notes
- The card renders immediately; heavy imports (PyTorch / sentence-transformers)
  happen in a background thread, so the page is never blank.
- The load job lives in ``st.session_state`` and runs on a module-level
  executor. Navigating to another page mid-load does NOT block (the old
  ``with ThreadPoolExecutor`` joined the thread) and coming back resumes the
  same job instead of starting over.
- During a first-run download the bar tracks the real bytes written to the
  Hugging Face cache; if the model is already on disk it skips that stage.
- core/ and backend/ are untouched.
"""

import math
import os
import time
from collections.abc import Callable, Iterable
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

import streamlit as st

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
MODEL_REPO_DIR = "models--sentence-transformers--all-MiniLM-L6-v2"
MODEL_BYTES = 91_000_000  # ~90 MB of weights + tokenizer files
_BOOT_KEY = "_boot_job"

# Module-level and never joined, so a script rerun can't be blocked by it.
_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="model-load")


def _hub_cache_dir() -> Path:
    if os.getenv("HF_HUB_CACHE"):
        return Path(os.environ["HF_HUB_CACHE"])
    if os.getenv("HF_HOME"):
        return Path(os.environ["HF_HOME"]) / "hub"
    return Path.home() / ".cache" / "huggingface" / "hub"


def _downloaded_bytes() -> int:
    """Bytes of the model on disk, including partial (.incomplete) downloads."""
    blobs = _hub_cache_dir() / MODEL_REPO_DIR / "blobs"
    if not blobs.is_dir():
        return 0
    total = 0
    for entry in blobs.iterdir():
        try:
            total += entry.stat().st_size
        except OSError:
            pass
    return total


def _mb(n: float) -> str:
    return f"{n / 1_000_000:.0f} MB"


def _worker(flag: dict, build: Callable[[], Any]):
    flag["stage"] = "import"
    import sentence_transformers  # noqa: F401  (the slow import: torch & friends)

    flag["stage"] = "model"
    return build()


def _render(slot, pct: float, title: str, sub: str, phase: int, log: list[str], current: str, done: bool = False):
    pct = max(0.0, min(100.0, pct))
    phases = ""
    for i, label in enumerate(("1 libraries", "2 model", "3 seed")):
        cls = "ok" if (i < phase or done) else ("on" if i == phase else "")
        phases += f'<span class="phase {cls}">{label}</span>'
    lines = "".join(f'<div class="ok">✓ {line}</div>' for line in log[-3:])
    if current:
        lines += f'<div class="cur">{current}</div>'
    slot.markdown(
        f'<div class="boot {"done" if done else ""}">'
        f'<div class="boot-head"><div><div class="boot-title">{title}</div><div class="boot-sub">{sub}</div></div>'
        f'<div class="boot-pct">{pct:.0f}%</div></div>'
        f'<div class="boot-bar"><i style="width:{pct:.1f}%"></i></div>'
        f'<div class="boot-phases">{phases}</div>'
        f'<div class="boot-log">{lines}</div></div>',
        unsafe_allow_html=True,
    )


def load_with_progress(build: Callable[[], Any], seed: Callable[[Any], Iterable[Any]], n_seeds: int):
    """Build the cache in the background while animating the boot card.

    ``build`` creates the cache object (this is where the model loads).
    ``seed`` receives the cache and yields once after storing each seed example.
    """
    slot = st.empty()

    job = st.session_state.get(_BOOT_KEY)
    if job is None:
        needs_download = _downloaded_bytes() < MODEL_BYTES * 0.97
        flag = {"stage": "import"}
        job = {
            "flag": flag,
            "future": _EXECUTOR.submit(_worker, flag, build),
            "t0": time.time(),
            "needs_download": needs_download,
            "load_t0": None,
            "log": [] if needs_download else ["model found in local cache, skipping download"],
            "stage_logged": set(),
        }
        st.session_state[_BOOT_KEY] = job

    flag, future, t0 = job["flag"], job["future"], job["t0"]
    needs_download, log = job["needs_download"], job["log"]
    import_hi = 18 if needs_download else 45

    # paint immediately, before any waiting
    _render(slot, 1, "Starting up", "Preparing the embedding engine", 0, log, "importing PyTorch & sentence-transformers …")

    while not future.done():
        now = time.time()
        if flag["stage"] == "import":
            pct = import_hi * (1 - math.exp(-(now - t0) / 6.0))
            _render(
                slot, pct, "Importing libraries",
                "PyTorch and sentence-transformers. Slowest part of a cold start.", 0, log,
                f"importing PyTorch & sentence-transformers … {now - t0:.0f}s",
            )
            time.sleep(0.15)
            continue

        if "import" not in job["stage_logged"]:
            job["stage_logged"].add("import")
            log.append("libraries imported")

        if needs_download:
            got = _downloaded_bytes()
            frac = min(got / MODEL_BYTES, 1.0)
            if frac < 0.99:
                _render(
                    slot, import_hi + (75 - import_hi) * frac, "Downloading embedding model",
                    f"First visit only · {MODEL_NAME}", 1, log,
                    f"fetching weights … {_mb(got)} / {_mb(MODEL_BYTES)} · {now - t0:.0f}s",
                )
                time.sleep(0.2)
                continue
            if job["load_t0"] is None:
                job["load_t0"] = now
                log.append(f"downloaded {_mb(MODEL_BYTES)}")
        elif job["load_t0"] is None:
            job["load_t0"] = now

        lo = 75 if needs_download else import_hi
        pct = lo + (92 - lo) * (1 - math.exp(-(now - job["load_t0"]) / 3.0))
        _render(
            slot, pct, "Loading model into memory",
            "384-dim embeddings · runs locally, no API key", 1, log,
            f"initialising encoder … {now - t0:.0f}s",
        )
        time.sleep(0.15)

    try:
        cache = future.result()
    except Exception:
        st.session_state.pop(_BOOT_KEY, None)  # allow a clean retry on next run
        raise

    log.append("encoder ready")
    seed_start = 92
    _render(slot, seed_start, "Seeding demo examples", "So your first question can be a cache HIT", 2, log, "embedding seed questions …")
    for i, _ in enumerate(seed(cache), start=1):
        _render(
            slot, seed_start + (100 - seed_start) * i / n_seeds,
            "Seeding demo examples", "So your first question can be a cache HIT", 2, log,
            f"embedded seed {i}/{n_seeds}",
        )

    log.append(f"seeded {n_seeds} examples")
    log.append(f"ready in {time.time() - t0:.1f}s")
    _render(slot, 100, "Ready", "Ask a question below", 3, log, "", done=True)
    time.sleep(0.9)
    slot.empty()
    st.session_state.pop(_BOOT_KEY, None)
    return cache
