# Validation Report

Generated on June 15, 2026.

## Automated Tests

- Result: `15 passed`
- Test areas:
  - correlation ID propagation
  - response timing headers
  - structured log enrichment
  - recursive PII redaction
  - dashboard availability
  - percentile and error-rate metrics
  - Langfuse SDK v4 helpers and trace propagation
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

- Concurrency: `10`
- Successful requests: `10/10`
- HTTP status: all `200`
- Correlation IDs: unique per request
- Script termination: clean, without manual interruption
- Langfuse: one root trace per concurrent request

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
- Langfuse trace list: `docs/evidence/langfuse-trace-list.png`
- Langfuse waterfall: `docs/evidence/langfuse-waterfall.png`
