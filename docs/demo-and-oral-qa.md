# Demo Script and Oral Review

## Five-Minute Demo

1. Start the app with `python -m uvicorn app.main:app --reload`.
2. Open `/health` and show incident state plus tracing status.
3. Run `python scripts/load_test.py --concurrency 5`.
4. Open `/dashboard` and explain the six panels and SLO thresholds.
5. Open `data/logs.jsonl` and filter one `correlation_id`.
6. Show `[REDACTED_EMAIL]` and `[REDACTED_CREDIT_CARD]` in log previews.
7. Enable `tool_fail`, send requests, and show the error-rate increase.
8. Use the `request_failed` log to prove `Vector store timeout`.
9. Disable the incident and verify `/health`.
10. Run `python scripts/validate_logs.py` and show `100/100`.

## Architecture Explanation

The middleware creates or propagates the request ID and binds it to
`structlog.contextvars`. The chat endpoint adds user, session, feature, model,
and environment context. The logging pipeline timestamps the event, recursively
scrubs PII, optionally writes audit events, writes JSONL, and renders JSON to
the console.

The agent records latency, tokens, cost, and quality. These values feed the
dashboard and are also attached to Langfuse observations when credentials are
configured.

## Likely Questions

### Why is correlation ID middleware-level?

Middleware covers every endpoint and both successful and failed request paths.
It also makes the ID available before endpoint logging begins.

### What prevents request context leakage?

`clear_contextvars()` runs at the start of each request. Request-specific fields
are bound after that, and chat enrichment fields are unbound in a `finally`
block.

### Why scrub recursively?

PII may appear in nested payloads or exception details. Scrubbing only the top
level would leave those values exposed.

### Is hashing a user ID anonymous?

No. It is pseudonymous because repeated values produce the same hash. It lowers
exposure while preserving correlation, but still requires access and retention
controls.

### Why use P95 rather than average latency?

An average can hide a slow tail. P95 shows the experience of nearly the slowest
5% of requests and is therefore better for latency SLOs.

### How is error rate calculated?

`errors / (successful requests + errors) * 100`. Successful requests and failed
attempts are tracked separately.

### How did you diagnose `tool_fail`?

Metrics showed a high error rate. Failed request logs grouped under
`RuntimeError`. The sanitized error detail identified `Vector store timeout`,
which maps to the injected retrieval failure.

### What happens without Langfuse credentials?

The tracing wrapper becomes a no-op. The app, logs, tests, metrics, dashboard,
and incident workflow remain functional without emitting authentication errors.

### What changes when credentials are added?

`LabAgent.run` is observed and publishes trace metadata, tags, sanitized query
preview, document count, and token usage to the configured Langfuse host.
