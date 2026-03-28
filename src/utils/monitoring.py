from __future__ import annotations

import time
from contextlib import contextmanager
from typing import Iterator

from src.utils.lineage import record_lineage


@contextmanager
def track_latency(stage: str) -> Iterator[dict[str, float]]:
    start = time.perf_counter()
    state: dict[str, float] = {}
    try:
        yield state
    finally:
        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        record_lineage(stage, {'latency_ms': duration_ms, **state})
