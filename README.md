# Day 13 Observability Lab

Completed FastAPI observability lab covering structured logging, PII safety,
metrics, tracing, alerts, incident response, quality evaluation, and cost
analysis.

## Current Results

| Check | Result |
|---|---:|
| Automated tests | 14 passed |
| Log validator | 100/100 |
| JSON Schema failures | 0 |
| PII leaks detected | 0 |
| Quality and safety eval | 7/7 passed |
| Simulated eval cost | $0.002991 |
| Estimated cost reduction | 79.09% |
| Alert scenarios | 4/4 passed |
| Dashboard panels | 6/6 |
| Live Langfuse traces | 0, credentials required |

The local implementation is complete. The only unmet external rubric item is
the requirement for at least 10 live Langfuse traces and a waterfall
screenshot. The local `.env` currently has empty Langfuse keys.

## Features

- JSONL structured logging with correlation IDs
- request context enrichment for user, session, feature, model, and environment
- recursive PII redaction for email, phone, CCCD, card, passport, and address
- separate audit log for incident-control actions
- rolling one-hour latency, traffic, error, token, cost, and quality metrics
- rolling 24-hour cost budget
- six-panel dashboard with SLO thresholds and 20-second refresh
- executable latency, error-rate, and cost alert evaluation
- secured local development incident controls
- Langfuse parent and child observations with automatic raw capture disabled
- deterministic quality/safety evaluation and simulated cost comparison
- JSON Schema-based log validation

## Architecture

```text
HTTP request
  -> CorrelationIdMiddleware
  -> /chat context enrichment
  -> LabAgent.run observation
       -> retrieve child observation
       -> FakeLLM.generate child observation
  -> rolling metrics
  -> scrubbed JSONL logs
  -> response with request ID and latency headers
```

The tracing path hashes user and session identifiers and sends only sanitized
query/answer previews. Raw trace input and output capture is disabled.

## Setup

Python 3.14 is supported by the pinned dependencies in this repository.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

The application reads configuration only from `.env`. Required local values:

```dotenv
APP_ENV=dev
APP_NAME=day13-observability-lab
LOG_LEVEL=INFO
LOG_PATH=data/logs.jsonl
AUDIT_LOG_PATH=data/audit.jsonl
LANGFUSE_PUBLIC_KEY=
LANGFUSE_SECRET_KEY=
LANGFUSE_HOST=https://cloud.langfuse.com
INCIDENT_ADMIN_TOKEN=replace-with-a-private-local-token
HOURLY_COST_BASELINE_USD=0.005
```

`.env` is intentionally ignored by Git.

## Run

```powershell
python -m uvicorn app.main:app --reload
```

Useful endpoints:

| Endpoint | Purpose |
|---|---|
| `GET /health` | service, tracing, and incident state |
| `POST /chat` | instrumented agent request |
| `GET /metrics` | rolling metrics snapshot |
| `GET /dashboard` | six-panel observability dashboard |
| `GET /alerts/status` | evaluated alert state |

## Verification

Run the complete local verification set:

```powershell
python -m pytest -q --basetemp=.pytest-tmp
python scripts/run_eval.py
python scripts/evaluate_alerts.py
python scripts/validate_logs.py
python scripts/export_evidence.py
```

Expected results:

- tests: `14 passed`
- eval: `7/7`, `100%`
- alert evaluation: `PASS`
- log validation: `100/100`
- PII leaks: `0`

## Load and Incident Demo

Generate ten requests:

```powershell
python scripts/load_test.py --concurrency 5
```

Inject and recover from incidents:

```powershell
python scripts/inject_incident.py --scenario tool_fail
python scripts/load_test.py --concurrency 2
python scripts/inject_incident.py --scenario tool_fail --disable
```

Incident endpoints are available only in development, only to local callers,
and require `INCIDENT_ADMIN_TOKEN`.

## Quality and Cost Evaluation

`scripts/run_eval.py` evaluates seven canonical cases from
`data/expected_answers.jsonl`, including:

- required answer content
- a refund-policy paraphrase
- observability workflow
- tail-latency debugging
- alert design
- PII safety
- an unsupported-question negative check

Cost uses the lab assumption of $3 per million input tokens and $15 per million
output tokens. Token counts and prices are simulated and are not a provider
invoice.

| Metric | Result |
|---|---:|
| Cases passed | 7/7 |
| Input tokens | 217 |
| Output tokens | 156 |
| Evaluated cost | $0.002991 |
| Starter baseline estimate | $0.014301 |
| Estimated reduction | 79.09% |

## Evidence

- [Group report](docs/blueprint-template.md)
- [Individual report](docs/individual-report-TVKhoa.md)
- [Contributor record](CONTRIBUTORS.md)
- [Validation report](docs/evidence/validation-report.md)
- [Independent agent audit](docs/evidence/agent-audit-report.md)
- [Quality and cost report](docs/evidence/eval-cost-report.md)
- [Alert evaluation report](docs/evidence/alert-evaluation-report.md)
- [Dashboard screenshot](docs/evidence/dashboard.png)
- [Logging and alert screenshot](docs/evidence/technical-evidence.png)
- [Demo and oral review](docs/demo-and-oral-qa.md)

## Repository Map

```text
app/
  agent.py              agent pipeline and parent tracing observation
  alerts.py             executable alert evaluation
  logging_config.py     scrubbed JSONL and audit logging
  main.py               FastAPI routes and incident authorization
  metrics.py            rolling one-hour and daily metrics
  middleware.py         correlation ID propagation
  mock_llm.py           deterministic local response generator
  mock_rag.py           retrieval and incident simulation
  pii.py                PII detection, redaction, and hashing
  tracing.py            Langfuse v3 adapter and safe fallback
config/
  alert_rules.yaml      production-style alert definitions
  logging_schema.json   JSON Schema for logs
  slo.yaml              SLO targets
scripts/
  evaluate_alerts.py    alert scenario verification
  export_evidence.py    reproducible evidence page
  inject_incident.py    authenticated incident control
  load_test.py          concurrent request generation
  run_eval.py           quality and cost evaluation
  validate_logs.py      schema, enrichment, correlation, and PII checks
docs/
  blueprint-template.md group submission report
  individual-report-TVKhoa.md
  demo-and-oral-qa.md
  evidence/
```

## Submission Status

- [x] implementation TODOs completed
- [x] validation score at least 80/100
- [x] dashboard contains all six panels
- [x] three alert rules have runbooks and executable threshold checks
- [x] individual contribution and Git evidence documented
- [x] quality, token, and cost evaluation documented
- [ ] at least 10 live Langfuse traces
- [ ] Langfuse trace-list and waterfall screenshots
