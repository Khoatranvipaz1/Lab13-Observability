# Individual Report - TVKhoa

## Identity

- Contributor: Khoatranvipaz1 (TVKhoa)
- Git email: `khoatranvippro@gmail.com`
- Branch: `TVKhoa`
- Repository: https://github.com/Khoatranvipaz1/Lab13-Observability
- Audited implementation commit:
  https://github.com/Khoatranvipaz1/Lab13-Observability/commit/7ce531d

## Individual Results

| Check | Result |
|---|---:|
| Automated tests | 14 passed |
| Log validator | 100/100 |
| JSON Schema failures | 0 |
| PII leaks | 0 |
| Quality/safety eval | 7/7 passed |
| Simulated eval cost | $0.002991 |
| Estimated cost reduction | 79.09% |
| Alert scenarios | 4/4 passed |

## Work Completed

### Correlation and Request Context

I implemented request-level correlation in `CorrelationIdMiddleware`.

- old context variables are cleared before each request
- an incoming `x-request-id` is preserved
- otherwise `req-<8 hex>` is generated
- the ID is bound to `structlog.contextvars`
- response headers include request ID and processing time

The `/chat` endpoint binds hashed user ID, session ID, feature, model, and
environment. Chat-specific context is removed in a `finally` block.

### Structured Logging and PII Protection

I completed the logging pipeline so records:

- follow the declared JSON Schema
- include correlation and enrichment fields
- are written as JSONL
- are recursively scrubbed before output
- write incident-control events to a separate audit log

PII patterns cover email, Vietnamese phone numbers, CCCD, credit cards,
passports, and labeled Vietnamese addresses. Additional tests cover plus-address
email syntax and nested payloads.

### Safe Tracing

I implemented Langfuse-compatible parent and child observations:

- `LabAgent.run`
- `retrieve`
- `fake_llm_generate`

Automatic input and output capture is disabled to prevent raw PII from being
sent to Langfuse. User and session identifiers are hashed. Query and answer
previews are sanitized before attachment.

Without credentials, the tracing layer becomes a no-op so local execution does
not emit authentication errors.

### Rolling Metrics and Dashboard

Metrics use timestamps rather than lifetime counters.

- traffic, latency, errors, tokens, cost, and quality use a rolling one-hour
  window
- cost budget uses a rolling 24-hour window
- P50, P95, and P99 expose tail latency
- error rate uses successful requests plus failed attempts as its denominator

The dashboard presents six panels, refreshes every 20 seconds, labels units,
and displays SLO thresholds.

### Alerts and Incident Security

I implemented executable alert checks for:

- latency P95 above 5000 ms
- error rate above 5%
- hourly cost above twice the configured baseline

`GET /alerts/status` exposes active state for the demo. A reproducible alert
script verifies normal, latency, error, and cost scenarios.

Incident endpoints are restricted to:

- development environment
- local callers
- requests with the configured admin token

### Quality and Cost Evaluation

I replaced the starter response with deterministic context-based behavior and
added a seven-case evaluation suite. Cases include:

- refund requirements
- observability workflow
- PII safety
- refund paraphrase
- tail-latency debugging
- alert design
- unsupported-question refusal

Results:

| Metric | Result |
|---|---:|
| Cases passed | 7/7 |
| Input tokens | 217 |
| Output tokens | 156 |
| Evaluated cost | $0.002991 |
| Baseline estimate | $0.014301 |
| Estimated reduction | 79.09% |

The estimate uses the lab assumption of $3 per million input tokens and $15 per
million output tokens. The baseline uses 130 output tokens, the midpoint of the
starter's original random 80-180 range. This is a simulation, not a provider
invoice.

### Independent Audit Fixes

An independent sub-agent review found and helped prioritize:

- unsafe default Langfuse capture
- missing child spans
- incorrect dashboard window claims
- static-only alerts
- incomplete schema and PII validation
- narrow eval coverage
- unauthenticated incident controls
- test state leakage

I implemented fixes for each local issue. The audit record is available at
`docs/evidence/agent-audit-report.md`.

## Incident Investigation

For the `tool_fail` drill:

1. Metrics showed the error-rate symptom.
2. `/alerts/status` activated `high_error_rate`.
3. Logs grouped failures as `RuntimeError`.
4. The sanitized detail identified `Vector store timeout`.
5. The authenticated incident script disabled the failure.
6. `/health` confirmed that all incident toggles were false.

The Langfuse trace stage is implemented but could not be demonstrated live
without credentials.

## Oral Review Notes

### Why clear context variables?

An async worker processes many requests. Without clearing context at request
start, fields from one request could appear in another request's logs.

### Why hash identifiers?

Hashing supports repeated-user or repeated-session correlation without storing
the raw identifier. It is pseudonymization, not full anonymization.

### Why use P95?

An average can hide a slow minority. P95 makes tail latency visible and is a
better operational SLI.

### Why scrub in the logging processor?

Endpoint-level sanitization can be forgotten. Pipeline-level recursive
scrubbing provides defense in depth for every caller and nested payload.

### Why Metrics -> Traces -> Logs?

Metrics identify the service symptom. Traces localize the failing or slow
operation. Logs explain detailed context and root cause.

### How is error rate calculated?

`failed attempts / (successful requests + failed attempts) * 100`

### Is the cost result real billing?

No. It is a reproducible local simulation based on estimated tokens and an
explicit pricing assumption.

## Evidence

- `CONTRIBUTORS.md`
- `docs/evidence/validation-report.md`
- `docs/evidence/agent-audit-report.md`
- `docs/evidence/eval-cost-report.md`
- `docs/evidence/alert-evaluation-report.md`
- `docs/evidence/dashboard.png`
- `docs/evidence/technical-evidence.png`

## Remaining External Requirement

The rubric requires at least 10 live Langfuse traces plus trace-list and
waterfall screenshots. These cannot be truthfully produced until valid
Langfuse credentials are added to `.env`.
