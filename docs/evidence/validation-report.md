# Validation Report

Generated on June 15, 2026.

## Automated Tests

- Result: `14 passed`
- Test areas:
  - correlation ID propagation
  - response timing headers
  - structured log enrichment
  - recursive PII redaction
  - dashboard availability
  - percentile and error-rate metrics
  - Langfuse v3 adapter compatibility
  - expected-answer quality cases

## Quality and Cost Eval

- Dataset: `data/expected_answers.jsonl`
- Cases passed: `7/7`
- Pass rate: `100%`
- Input tokens: `217`
- Output tokens: `156`
- Evaluated simulated cost: `$0.002991`
- Starter estimated cost: `$0.014301`
- Estimated reduction: `79.09%`
- Detailed report: `docs/evidence/eval-cost-report.md`

## Log Validator

- Total valid log records: `158`
- Records failing JSON Schema: `0`
- Records missing enrichment: `0`
- Unique correlation IDs: `75`
- Potential PII leaks: `0`
- Estimated score: `100/100`

## Clean 10-Request Load Run

- Successful requests: `10`
- Latency P50/P95/P99: `150/150/150 ms`
- Input tokens: `340`
- Output tokens: `241`
- Total simulated cost: `$0.004635`
- Average simulated cost per request: `$0.000463`
- Error rate: `0%`
- Average quality proxy: `0.89`

## Incident Drill

- Scenario: `tool_fail`
- Failed requests: `10`
- Observed error rate: `50%`
- Error type: `RuntimeError`
- Root-cause detail: `Vector store timeout`
- Recovery: incident disabled and health state returned all toggles as false
- Alert threshold evaluation: `docs/evidence/alert-evaluation-report.md`

## Evidence

- Six-panel dashboard: `docs/evidence/dashboard.png`
- Correlation, PII, error, and alert evidence:
  `docs/evidence/technical-evidence.png`
- Separate audit trail: `data/audit.jsonl`

## External Blocker

Langfuse keys are empty in the local `.env`, so the required 10 live cloud
traces and trace-waterfall screenshot cannot be generated yet.
