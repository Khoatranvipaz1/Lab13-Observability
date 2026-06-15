# Alert Evaluation Report

- Result: `PASS`
- Evaluator: `app/alerts.py`
- Endpoint: `GET /alerts/status`

| Scenario | Active alerts |
|---|---|
| normal | none |
| latency_breach | high_latency_p95 |
| error_breach | high_error_rate |
| cost_breach | cost_budget_spike |

Production alert-manager durations remain defined in
`config/alert_rules.yaml`; this lab evaluator checks threshold state
immediately.
