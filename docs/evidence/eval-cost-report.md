# Quality Eval and Cost Report

## Summary

- Dataset: `data\expected_answers.jsonl`
- Model label: `claude-sonnet-4-5` (deterministic local fake)
- Cases passed: `7/7`
- Pass rate: `100.00%`
- Input tokens: `217`
- Output tokens: `156`
- Evaluated cost: `$0.002991`
- Starter estimated cost: `$0.014301`
- Estimated cost reduction: `79.09%`

Pricing assumption: $3 per million input tokens and $15 per million output
tokens. The starter baseline uses 130 output tokens per case, the midpoint of
the original random 80-180 token range. These are simulated estimates, not a
provider invoice.

## Cases

| # | Result | Input tokens | Output tokens | Cost |
|---:|---|---:|---:|---:|
| 1 | PASS | 29 | 14 | $0.000297 |
| 2 | PASS | 33 | 24 | $0.000459 |
| 3 | PASS | 30 | 24 | $0.000450 |
| 4 | PASS | 38 | 14 | $0.000324 |
| 5 | PASS | 30 | 26 | $0.000480 |
| 6 | PASS | 29 | 27 | $0.000492 |
| 7 | PASS | 28 | 27 | $0.000489 |

Full answers and phrase-level checks are available in
`docs/evidence/eval-cost-report.json`.
