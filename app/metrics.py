from __future__ import annotations

from collections import Counter
from statistics import mean
from time import time

REQUEST_LATENCIES: list[int] = []
REQUEST_COSTS: list[float] = []
REQUEST_TOKENS_IN: list[int] = []
REQUEST_TOKENS_OUT: list[int] = []
REQUEST_TIMESTAMPS: list[float] = []
ERRORS: Counter[str] = Counter()
ERROR_EVENTS: list[tuple[float, str]] = []
TRAFFIC: int = 0
QUALITY_SCORES: list[float] = []


def record_request(latency_ms: int, cost_usd: float, tokens_in: int, tokens_out: int, quality_score: float) -> None:
    global TRAFFIC
    TRAFFIC += 1
    REQUEST_LATENCIES.append(latency_ms)
    REQUEST_COSTS.append(cost_usd)
    REQUEST_TOKENS_IN.append(tokens_in)
    REQUEST_TOKENS_OUT.append(tokens_out)
    QUALITY_SCORES.append(quality_score)
    REQUEST_TIMESTAMPS.append(time())



def record_error(error_type: str) -> None:
    ERRORS[error_type] += 1
    ERROR_EVENTS.append((time(), error_type))



def percentile(values: list[int], p: int) -> float:
    if not values:
        return 0.0
    items = sorted(values)
    idx = max(0, min(len(items) - 1, round((p / 100) * len(items) + 0.5) - 1))
    return float(items[idx])



def snapshot() -> dict:
    now = time()
    hour_cutoff = now - 3600
    day_cutoff = now - 86400
    if REQUEST_TIMESTAMPS:
        hour_indexes = [
            index
            for index, timestamp in enumerate(REQUEST_TIMESTAMPS)
            if timestamp >= hour_cutoff
        ]
        day_indexes = [
            index
            for index, timestamp in enumerate(REQUEST_TIMESTAMPS)
            if timestamp >= day_cutoff
        ]
    else:
        hour_indexes = list(range(len(REQUEST_LATENCIES)))
        day_indexes = hour_indexes

    latencies = [REQUEST_LATENCIES[index] for index in hour_indexes]
    costs = [REQUEST_COSTS[index] for index in hour_indexes]
    tokens_in = [REQUEST_TOKENS_IN[index] for index in hour_indexes]
    tokens_out = [REQUEST_TOKENS_OUT[index] for index in hour_indexes]
    quality_scores = [QUALITY_SCORES[index] for index in hour_indexes]
    daily_costs = [REQUEST_COSTS[index] for index in day_indexes]

    if ERROR_EVENTS:
        error_breakdown = Counter(
            error_type
            for timestamp, error_type in ERROR_EVENTS
            if timestamp >= hour_cutoff
        )
    else:
        error_breakdown = ERRORS.copy()

    errors_total = sum(error_breakdown.values())
    traffic = len(hour_indexes) if REQUEST_TIMESTAMPS else TRAFFIC
    attempts = traffic + errors_total
    return {
        "window": "1h",
        "traffic": traffic,
        "latency_p50": percentile(latencies, 50),
        "latency_p95": percentile(latencies, 95),
        "latency_p99": percentile(latencies, 99),
        "avg_cost_usd": round(mean(costs), 6) if costs else 0.0,
        "hourly_cost_usd": round(sum(costs), 6),
        "daily_cost_usd": round(sum(daily_costs), 6),
        "total_cost_usd": round(sum(costs), 6),
        "tokens_in_total": sum(tokens_in),
        "tokens_out_total": sum(tokens_out),
        "errors_total": errors_total,
        "error_rate_pct": round((errors_total / attempts) * 100, 2) if attempts else 0.0,
        "error_breakdown": dict(error_breakdown),
        "quality_avg": round(mean(quality_scores), 4) if quality_scores else 0.0,
    }


def reset() -> None:
    global TRAFFIC
    TRAFFIC = 0
    REQUEST_LATENCIES.clear()
    REQUEST_COSTS.clear()
    REQUEST_TOKENS_IN.clear()
    REQUEST_TOKENS_OUT.clear()
    REQUEST_TIMESTAMPS.clear()
    ERRORS.clear()
    ERROR_EVENTS.clear()
    QUALITY_SCORES.clear()
