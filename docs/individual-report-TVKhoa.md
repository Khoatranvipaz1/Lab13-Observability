# Individual Report - TVKhoa

## Identity and Evidence

- Git identity: `Khoatranvipaz1`
- Branch: `TVKhoa`
- Main implementation commit:
  [29fe1ae](https://github.com/Khoatranvipaz1/Lab13-Observability/commit/29fe1ae05177c64c3b0fb4ffb8caf6f9e4538fda)
- Repository: [Lab13-Observability](https://github.com/Khoatranvipaz1/Lab13-Observability)
- Validation result: `100/100`
- Automated tests: `14 passed`
- Expected-answer and safety eval: `7/7 passed` (`100%`)
- Evaluated simulated cost: `$0.002991`
- Estimated starter baseline cost: `$0.014301`
- Estimated cost reduction: `79.09%`

## Work Completed

### Correlation ID

I completed `CorrelationIdMiddleware` so each request:

1. Clears old `structlog` context variables to prevent cross-request leakage.
2. Reuses the incoming `x-request-id`, or generates `req-<8 hex chars>`.
3. Binds the ID to the logging context.
4. Returns `x-request-id` and `x-response-time-ms` headers.

This lets logs from the same request be searched using one stable identifier.

### Structured Logging and Enrichment

For `/chat`, I bind:

- hashed user ID
- session ID
- feature
- model
- environment
- correlation ID

The raw user ID is not logged. SHA-256 is used to create a stable 12-character
pseudonymous identifier. This supports grouping events by user without exposing
the original identifier.

### PII Protection

I added patterns for:

- email
- Vietnamese phone number
- CCCD
- credit card
- passport
- Vietnamese address labels

The logging processor scrubs strings recursively inside dictionaries, lists,
tuples, event names, payloads, and exception details. Scrubbing at the logging
pipeline is defense in depth: application code also logs sanitized previews,
but the processor protects against future callers forgetting to sanitize.

### Metrics and Dashboard

The metrics snapshot exposes:

- request traffic
- latency P50/P95/P99
- total and average cost
- input/output token totals
- total errors and error breakdown
- error rate
- average quality score

The dashboard at `/dashboard` contains exactly six main panels, uses a one-hour
view, refreshes every 20 seconds, displays units, and shows SLO thresholds.

### Quality and Cost Evaluation

I added a reproducible evaluation against `data/expected_answers.jsonl`.
The evaluator checks required answer phrases rather than relying only on the
application's heuristic quality score.

Results:

- 7/7 cases passed
- 100% pass rate
- 217 simulated input tokens
- 156 simulated output tokens
- $0.002991 evaluated cost
- $0.014301 estimated starter cost
- 79.09% estimated cost reduction

The estimate uses $3 per million input tokens and $15 per million output tokens.
The starter comparison uses 130 output tokens, the midpoint of its original
random 80-180 range. This is a deterministic local estimate, not a provider
invoice.

### Tracing

The agent method is wrapped with Langfuse `observe`. When credentials exist,
the trace receives:

- hashed user ID
- session ID
- feature and model tags
- document count
- sanitized query preview
- input/output token usage

When credentials are absent, tracing becomes a no-op so local development still
works without authentication errors.

### Alerting, Incident Debugging, and Audit

I verified the `tool_fail` scenario:

- 10 requests returned HTTP 500.
- Error rate increased to 50%.
- Logs identified `RuntimeError`.
- The payload identified `Vector store timeout` as the cause.
- Disabling the incident restored the service state.

Incident enable/disable actions are also written to `data/audit.jsonl`, separate
from normal application logs.

## Technical Explanations for Oral Review

### Why clear context variables?

Workers process many requests over time. Without clearing context at the start
of middleware, fields from a previous request could appear in a later request's
logs. Clearing first and then binding the current correlation ID prevents this
context leakage.

### How is P95 calculated?

Recorded latencies are sorted, and the nearest-rank position for percentile
`p` is selected. P95 represents a tail-latency boundary: approximately 95% of
requests are at or below that value. It is more useful than an average for
detecting a smaller set of very slow requests.

### Why hash instead of redact user ID?

Full redaction protects privacy but removes the ability to correlate activity
for the same user. A one-way hash preserves grouping while avoiding storage of
the raw identifier. It is pseudonymization, not complete anonymization, so
access controls and retention policies are still required.

### Why use Metrics, then Traces, then Logs?

Metrics reveal that a service-level symptom exists. Traces narrow the symptom
to a slow or failed operation. Logs then provide detailed context such as the
error type, incident state, and sanitized request metadata. This ordering keeps
debugging efficient.

### Why is the error-rate denominator requests plus errors?

Successful requests are recorded after the agent completes, while failed
attempts call `record_error`. Therefore, total attempts are successful requests
plus failed attempts. Error rate is:

`errors / (successful requests + errors) * 100`

## Verification Evidence

- Dashboard: `docs/evidence/dashboard.png`
- Logging, PII, error and alerts: `docs/evidence/technical-evidence.png`
- Audit log: `data/audit.jsonl`
- Tests: `tests/test_app.py`, `tests/test_pii.py`, `tests/test_metrics.py`
- Validator: `scripts/validate_logs.py`
- Quality and cost eval: `docs/evidence/eval-cost-report.md`
- Contributor ownership: `CONTRIBUTORS.md`

## Remaining Group Work

All local implementation, testing, dashboard, incident response, and reporting
work is complete. The only external requirement still blocked is live Langfuse
evidence: valid credentials are required to publish at least 10 traces and
capture the trace-list and waterfall screenshots.
