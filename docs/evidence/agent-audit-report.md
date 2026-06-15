# Independent Agent Audit Report

Audit date: June 15, 2026.

An independent sub-agent reviewed the repository against all Markdown
requirements and the instructor rubric. The main findings and resolutions are
recorded below.

## Resolved Findings

### Trace PII capture

- Disabled automatic trace input/output capture.
- Hashes user and session identifiers before sending trace metadata.
- Sanitizes feature tags and query/answer previews.
- Added a test proving explicit trace metadata does not contain raw email,
  user ID, session ID, or message.

### Missing trace waterfall structure

- Added child observations for retrieval and fake LLM generation.
- Parent observation remains `LabAgent.run`.

### Incorrect dashboard time-window claim

- Metrics now store timestamps.
- Traffic, latency, errors, tokens, quality, and hourly cost use a rolling
  one-hour window.
- Daily cost uses a rolling 24-hour window.

### Alerts were static only

- Added `GET /alerts/status`.
- Added immediate lab evaluation for latency, error-rate, and cost thresholds.
- Production `for` durations remain documented in YAML/runbooks.
- Added tests showing all three thresholds can become active.

### Validator did not enforce the schema

- Validator now uses JSON Schema Draft 2020-12.
- PII detection reuses all application PII patterns.
- Added nested payload and plus-address tests.

### Eval was too narrow

- Expanded from 3 to 7 canonical cases.
- Added paraphrase, tail-latency, alert-design, unsupported-question, and
  negative hallucination checks.
- Tests and evaluator load the same dataset.

### Incident controls were unauthenticated

- Incident endpoints are restricted to development mode and local callers.
- `x-admin-token` must match `INCIDENT_ADMIN_TOKEN` from `.env`.
- The incident script loads the token automatically.

### Test state leakage

- Added an automatic fixture that resets metrics and incident state.
- Test logs and audit logs are redirected to temporary paths.

## Verified Results

- Automated tests: `14 passed`
- Quality/safety eval: `7/7 passed`
- Log validator: `100/100`
- JSON Schema failures: `0`
- PII leaks: `0`
- Dashboard: six panels with rolling windows
- Alert evaluator: latency, error, and cost checks implemented
- Contributor record: `CONTRIBUTORS.md`
- Cost report: `docs/evidence/eval-cost-report.md`

## Remaining External Blocker

The instructor rubric requires at least 10 live Langfuse traces and a waterfall
screenshot. The local `.env` still has empty Langfuse keys. This cannot be
truthfully completed without valid external credentials.
