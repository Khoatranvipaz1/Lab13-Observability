# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- [GROUP_NAME]: TVKhoa
- [REPO_URL]: https://github.com/Khoatranvipaz1/Lab13-Observability
- [MEMBERS]:
  - Member A: Khoatranvipaz1 (TVKhoa) | Role: Full-stack observability implementation, testing, dashboard, incident response, evidence, and report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 0 (Langfuse credentials are not configured in `.env`)
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: docs/evidence/technical-evidence.png
- [EVIDENCE_PII_REDACTION_SCREENSHOT]: docs/evidence/technical-evidence.png
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: Not available until Langfuse credentials are configured
- [TRACE_WATERFALL_EXPLANATION]: The instrumented `LabAgent.run` observation records retrieval/LLM execution metadata, sanitized query preview, document count, token usage, hashed user ID, session ID, feature, and model tags. A live waterfall requires valid Langfuse credentials.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: docs/evidence/dashboard.png
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 150ms |
| Error Rate | < 2% | 28d | 0% (clean run) |
| Cost Budget | < $2.5/day | 1d | $0.0230 demo total |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: docs/evidence/technical-evidence.png
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#1-high-latency-p95

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: tool_fail
- [SYMPTOMS_OBSERVED]: 10 chat requests returned HTTP 500; error rate increased to 50%.
- [ROOT_CAUSE_PROVED_BY]: `request_failed` logs show `RuntimeError` with `Vector store timeout`.
- [FIX_ACTION]: Disabled the `tool_fail` incident toggle and verified health returned all toggles false.
- [PREVENTIVE_MEASURE]: Alert on error rate and group logs by `error_type`; use a retrieval fallback or circuit breaker.

---

## 5. Individual Contributions & Evidence

### Khoatranvipaz1 (TVKhoa)
- [TASKS_COMPLETED]: Implemented correlation ID propagation, structured log enrichment, recursive PII redaction, Langfuse-compatible tracing, error-rate metrics, separate audit logs, integration tests, the six-panel dashboard, and reproducible technical evidence.
- [EVIDENCE_LINK]: https://github.com/Khoatranvipaz1/Lab13-Observability/commit/29fe1ae05177c64c3b0fb4ffb8caf6f9e4538fda
- [INDIVIDUAL_REPORT]: docs/individual-report-TVKhoa.md

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: Token and cost telemetry are exposed per request and on the dashboard, providing a measurable baseline for future prompt/model optimization.
- [BONUS_AUDIT_LOGS]: Incident control actions are written separately to `data/audit.jsonl`.
- [BONUS_CUSTOM_METRIC]: Dashboard includes heuristic quality score and error breakdown.
