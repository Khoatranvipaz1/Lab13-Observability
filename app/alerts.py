from __future__ import annotations

import os
from typing import Any


def evaluate_alerts(metrics: dict[str, Any]) -> list[dict[str, Any]]:
    baseline_cost = float(os.getenv("HOURLY_COST_BASELINE_USD", "0.005"))
    checks = [
        {
            "name": "high_latency_p95",
            "severity": "P2",
            "active": metrics["latency_p95"] > 5000,
            "value": metrics["latency_p95"],
            "threshold": 5000,
            "unit": "ms",
            "runbook": "docs/alerts.md#1-high-latency-p95",
        },
        {
            "name": "high_error_rate",
            "severity": "P1",
            "active": metrics["error_rate_pct"] > 5,
            "value": metrics["error_rate_pct"],
            "threshold": 5,
            "unit": "percent",
            "runbook": "docs/alerts.md#2-high-error-rate",
        },
        {
            "name": "cost_budget_spike",
            "severity": "P2",
            "active": metrics["hourly_cost_usd"] > baseline_cost * 2,
            "value": metrics["hourly_cost_usd"],
            "threshold": baseline_cost * 2,
            "unit": "USD/hour",
            "runbook": "docs/alerts.md#3-cost-budget-spike",
        },
    ]
    return checks
