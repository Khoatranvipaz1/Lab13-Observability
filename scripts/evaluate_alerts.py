from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.alerts import evaluate_alerts

OUTPUT_JSON = Path("docs/evidence/alert-evaluation-report.json")
OUTPUT_MD = Path("docs/evidence/alert-evaluation-report.md")


def metrics(**overrides):
    value = {
        "latency_p95": 150,
        "error_rate_pct": 0,
        "hourly_cost_usd": 0.004,
    }
    value.update(overrides)
    return value


def main() -> None:
    scenarios = {
        "normal": metrics(),
        "latency_breach": metrics(latency_p95=6001),
        "error_breach": metrics(error_rate_pct=10),
        "cost_breach": metrics(hourly_cost_usd=0.011),
    }
    results = {}
    for name, snapshot in scenarios.items():
        alerts = evaluate_alerts(snapshot)
        results[name] = {
            "metrics": snapshot,
            "active_alerts": [
                alert["name"] for alert in alerts if alert["active"]
            ],
            "alerts": alerts,
        }

    expected = {
        "normal": [],
        "latency_breach": ["high_latency_p95"],
        "error_breach": ["high_error_rate"],
        "cost_breach": ["cost_budget_spike"],
    }
    passed = all(
        results[name]["active_alerts"] == active
        for name, active in expected.items()
    )
    report = {"passed": passed, "scenarios": results}
    OUTPUT_JSON.write_text(json.dumps(report, indent=2), encoding="utf-8")

    rows = "\n".join(
        f"| {name} | {', '.join(result['active_alerts']) or 'none'} |"
        for name, result in results.items()
    )
    OUTPUT_MD.write_text(
        f"""# Alert Evaluation Report

- Result: `{'PASS' if passed else 'FAIL'}`
- Evaluator: `app/alerts.py`
- Endpoint: `GET /alerts/status`

| Scenario | Active alerts |
|---|---|
{rows}

Production alert-manager durations remain defined in
`config/alert_rules.yaml`; this lab evaluator checks threshold state
immediately.
""",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2))
    if not passed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
