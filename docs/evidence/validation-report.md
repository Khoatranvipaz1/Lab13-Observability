# Validation Report

Generated on June 15, 2026.

## Automated Tests

- Result: `7 passed`
- Test areas:
  - correlation ID propagation
  - response timing headers
  - structured log enrichment
  - recursive PII redaction
  - dashboard availability
  - percentile and error-rate metrics
  - Langfuse v3 adapter compatibility

## Log Validator

- Total valid log records: `66`
- Records missing required fields: `0`
- Records missing enrichment: `0`
- Unique correlation IDs: `33`
- Potential PII leaks: `0`
- Estimated score: `100/100`

## Incident Drill

- Scenario: `tool_fail`
- Failed requests: `10`
- Observed error rate: `50%`
- Error type: `RuntimeError`
- Root-cause detail: `Vector store timeout`
- Recovery: incident disabled and health state returned all toggles as false

## Evidence

- Six-panel dashboard: `docs/evidence/dashboard.png`
- Correlation, PII, error, and alert evidence:
  `docs/evidence/technical-evidence.png`
- Separate audit trail: `data/audit.jsonl`

## External Blocker

Langfuse keys are empty in the local `.env`, so the required 10 live cloud
traces and trace-waterfall screenshot cannot be generated yet.
