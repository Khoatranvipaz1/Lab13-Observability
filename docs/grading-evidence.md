# Evidence Collection Sheet

## Required screenshots
- [ ] Langfuse trace list with >= 10 traces (blocked: credentials are empty in `.env`)
- [ ] One full trace waterfall (blocked: credentials are empty in `.env`)
- [x] JSON logs showing correlation_id: `docs/evidence/technical-evidence.png`
- [x] Log line with PII redaction: `docs/evidence/technical-evidence.png`
- [x] Dashboard with 6 panels: `docs/evidence/dashboard.png`
- [x] Alert rules with runbook link: `docs/evidence/technical-evidence.png`
- [x] Automated validation report: `docs/evidence/validation-report.md`

## Optional screenshots
- [x] Incident diagnosis: `docs/evidence/technical-evidence.png`
- [x] Cost telemetry baseline: `docs/evidence/dashboard.png`
- [x] Instrumentation proof: `app/agent.py` and `app/tracing.py`
- [x] Separate audit log: `data/audit.jsonl`
