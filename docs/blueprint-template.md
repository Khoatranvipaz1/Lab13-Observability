# Day 13 Observability Lab - Individual Submission Report

> Automated grading tags are intentionally preserved.

## 1. Student Metadata

- [GROUP_NAME]: Individual submission - Trần Văn Khoa
- [REPO_URL]: https://github.com/Khoatranvipaz1/Lab13-Observability
- [MEMBERS]:
  - Trần Văn Khoa | MSV: 2A202600827 | GitHub: Khoatranvipaz1 |
    Full implementation owner

This is an individual submission. Trần Văn Khoa designed, implemented,
tested, documented, and demonstrated the complete lab. Ownership and commit
evidence are recorded in `CONTRIBUTORS.md`.

## 2. Verified Results

- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 34 root traces / 124 observations
- [PII_LEAKS_FOUND]: 0
- [QUALITY_EVAL_PASS_RATE]: 100% (7/7)
- [EVAL_COST_USD]: $0.002991 (simulated)
- [AUTOMATED_TESTS]: 19 passed
- [ALERT_EVALUATION]: PASS (4/4 scenarios)

The final Langfuse evidence shows 34 root traces and 124 observations,
including a clean batch of 10 concurrent requests.

## 3. Technical Implementation

### 3.1 Logging and Correlation

Every request receives an incoming or generated `req-<8 hex>` correlation ID.
The middleware clears previous context, binds the current ID, and returns both
`x-request-id` and `x-response-time-ms`.

Chat logs include:

- hashed user ID
- hashed session ID
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

The verified Langfuse waterfall contains:

1. `chat-response` root observation
2. `knowledge-retrieval` child span
3. `fake-llm-generation` child generation

Automatic raw input/output capture is disabled. User and session identifiers
are hashed, while query and answer previews are sanitized.

- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]:
  `docs/evidence/langfuse-waterfall.png`
- [EVIDENCE_TRACE_LIST_SCREENSHOT]:
  `docs/evidence/langfuse-trace-list.png`
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

The completed workflow supports Metrics -> Traces -> Logs. Langfuse localizes
the retrieval and generation stages, while scrubbed logs provide request-level
diagnostic detail.

## 6. Individual Ownership

### Trần Văn Khoa - 2A202600827

- [GITHUB_ACCOUNT]: `Khoatranvipaz1`
- [BRANCH]: `TVKhoa`

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
- 19 automated tests
- validator score 100/100
- zero detected PII leaks
- six-panel dashboard
- alert evaluation
- incident drill
- individual submission report
- Git contribution evidence

- 34 live Langfuse root traces
- trace-list evidence
- full trace waterfall evidence
