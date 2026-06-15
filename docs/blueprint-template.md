# Day 13 Observability Lab Report

> Automated grading tags are intentionally preserved.

## 1. Team Metadata

- [GROUP_NAME]: TVKhoa
- [REPO_URL]: https://github.com/Khoatranvipaz1/Lab13-Observability
- [MEMBERS]:
  - Khoatranvipaz1 (TVKhoa) | Full implementation owner

The repository was completed as a one-member submission. Ownership and commit
evidence are recorded in `CONTRIBUTORS.md`.

## 2. Verified Results

- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 0
- [PII_LEAKS_FOUND]: 0
- [QUALITY_EVAL_PASS_RATE]: 100% (7/7)
- [EVAL_COST_USD]: $0.002991 (simulated)
- [AUTOMATED_TESTS]: 14 passed
- [ALERT_EVALUATION]: PASS (4/4 scenarios)

The trace count is zero because `LANGFUSE_PUBLIC_KEY` and
`LANGFUSE_SECRET_KEY` are not configured. No trace evidence is claimed without
live credentials.

## 3. Technical Implementation

### 3.1 Logging and Correlation

Every request receives an incoming or generated `req-<8 hex>` correlation ID.
The middleware clears previous context, binds the current ID, and returns both
`x-request-id` and `x-response-time-ms`.

Chat logs include:

- hashed user ID
- session ID
- feature
- model
- environment
- correlation ID
- latency, tokens, cost, and sanitized payload previews

Logs are checked against `config/logging_schema.json` using JSON Schema Draft
2020-12.

- [EVIDENCE_CORRELATION_ID_SCREENSHOT]:
  `docs/evidence/technical-evidence.png`

### 3.2 PII and Audit Safety

The logging pipeline recursively redacts sensitive strings inside nested
dictionaries, lists, tuples, events, payloads, and error details. Covered
patterns include email, Vietnamese phone numbers, CCCD, credit cards,
passports, and labeled Vietnamese addresses.

Incident-control events are duplicated to `data/audit.jsonl`.

- [EVIDENCE_PII_REDACTION_SCREENSHOT]:
  `docs/evidence/technical-evidence.png`
- [PII_LEAKS_FOUND]: 0

### 3.3 Tracing

The intended Langfuse waterfall contains:

1. `LabAgent.run` parent observation
2. `retrieve` child observation
3. `fake_llm_generate` child observation

Automatic raw input/output capture is disabled. User and session identifiers
are hashed, while query and answer previews are sanitized.

- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]:
  Not available because Langfuse credentials are empty
- [TRACE_WATERFALL_EXPLANATION]:
  The parent observation represents the full agent request. Child observations
  separate retrieval from generation so latency or failures can be localized.
  Explicit metadata includes document count, sanitized previews, and token
  usage without transmitting the raw request.

### 3.4 Dashboard, Metrics, and SLOs

The dashboard contains exactly six panels:

1. latency P50/P95/P99
2. rolling one-hour traffic
3. error rate and breakdown
4. rolling 24-hour cost budget
5. input/output tokens
6. quality proxy

It refreshes every 20 seconds and displays units and thresholds.

- [DASHBOARD_6_PANELS_SCREENSHOT]: `docs/evidence/dashboard.png`

- [SLO_TABLE]:

| SLI | Target | Window | Verified demo value |
|---|---:|---|---:|
| Latency P95 | < 3000 ms | rolling 1h | 150 ms |
| Error Rate | < 2% | rolling 1h | 0% clean run |
| Cost Budget | < $2.50 | rolling 24h | $0.004635 |
| Quality Score | >= 0.75 | rolling 1h | 0.89 |

### 3.5 Alerts and Runbooks

Three rules are defined and evaluated:

| Alert | Threshold | Verification |
|---|---|---|
| High latency | P95 > 5000 ms | PASS |
| High error rate | error rate > 5% | PASS |
| Cost spike | hourly cost > 2x baseline | PASS |

`GET /alerts/status` evaluates current threshold state. Production-style `for`
durations remain in `config/alert_rules.yaml`.

- [ALERT_RULES_SCREENSHOT]: `docs/evidence/technical-evidence.png`
- [SAMPLE_RUNBOOK_LINK]: `docs/alerts.md#1-high-latency-p95`
- [ALERT_EVALUATION_REPORT]:
  `docs/evidence/alert-evaluation-report.md`

## 4. Quality and Cost Evaluation

Seven cases were evaluated from `data/expected_answers.jsonl`. The dataset
contains exact requirements, a paraphrase, an unsupported-question safety
check, and observability scenarios.

| Metric | Result |
|---|---:|
| Cases passed | 7/7 |
| Pass rate | 100% |
| Input tokens | 217 |
| Output tokens | 156 |
| Evaluated cost | $0.002991 |
| Starter baseline estimate | $0.014301 |
| Estimated reduction | 79.09% |

Pricing and token counts are local simulations, not a provider invoice.

Evidence: `docs/evidence/eval-cost-report.md`.

## 5. Incident Response

- [SCENARIO_NAME]: tool_fail
- [SYMPTOMS_OBSERVED]:
  Chat requests returned HTTP 500 and the rolling error rate increased to 50%.
- [ROOT_CAUSE_PROVED_BY]:
  `request_failed` records contained `RuntimeError` and the sanitized detail
  `Vector store timeout`.
- [FIX_ACTION]:
  Disabled `tool_fail` with the authenticated local incident script and
  verified that `/health` returned all incident toggles as false.
- [PREVENTIVE_MEASURE]:
  Alert on error rate, group logs by `error_type`, protect incident controls,
  and add retrieval fallback or circuit-breaker behavior.

The debug sequence was Metrics -> Logs, with the trace stage prepared but not
available live because Langfuse credentials are absent.

## 6. Individual Contribution

### Khoatranvipaz1 (TVKhoa)

- [TASKS_COMPLETED]:
  Correlation middleware, structured logging, PII protection, safe tracing,
  rolling metrics, dashboard, alerts, incident security, quality/cost eval,
  tests, evidence, and reports.
- [EVIDENCE_LINK]:
  https://github.com/Khoatranvipaz1/Lab13-Observability/commit/7ce531d
- [INDIVIDUAL_REPORT]: `docs/individual-report-TVKhoa.md`
- [CONTRIBUTOR_RECORD]: `CONTRIBUTORS.md`

## 7. Bonus Evidence

- [BONUS_COST_OPTIMIZATION]:
  Simulated eval cost decreased from $0.014301 to $0.002991, an estimated
  79.09% reduction across seven cases.
- [BONUS_AUDIT_LOGS]:
  Incident controls write to a separate audit stream.
- [BONUS_CUSTOM_METRIC]:
  Quality score, error breakdown, rolling hourly cost, and daily cost budget.
- [BONUS_AUTOMATION]:
  Reproducible scripts generate eval, alert, validation, and screenshot-ready
  evidence.

## 8. Submission Status

Completed:

- local implementation
- 14 automated tests
- validator score 100/100
- zero detected PII leaks
- six-panel dashboard
- alert evaluation
- incident drill
- individual and group reports
- Git contribution evidence

External blocker:

- minimum 10 live Langfuse traces
- trace-list screenshot
- full waterfall screenshot

These three items require valid Langfuse credentials in `.env`.
