# Dashboard Spec

Required Layer-2 panels:
1. [x] Latency P50/P95/P99
2. [x] Traffic (request count)
3. [x] Error rate with breakdown
4. [x] Cost over time
5. [x] Tokens in/out
6. [x] Quality proxy (heuristic average)

Quality bar:
- default time range = 1 hour
- auto refresh every 15-30 seconds
- visible threshold/SLO line
- units clearly labeled
- no more than 6-8 panels on the main layer

Implementation: `http://127.0.0.1:8000/dashboard`

Evidence: `docs/evidence/dashboard.png`
