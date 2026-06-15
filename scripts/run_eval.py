from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.agent import LabAgent

DATASET_PATH = Path("data/expected_answers.jsonl")
JSON_OUTPUT = Path("docs/evidence/eval-cost-report.json")
MARKDOWN_OUTPUT = Path("docs/evidence/eval-cost-report.md")
STARTER_OUTPUT_TOKEN_MIDPOINT = 130


def load_dataset() -> list[dict]:
    return [
        json.loads(line)
        for line in DATASET_PATH.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def main() -> None:
    agent = LabAgent()
    cases = []

    for index, item in enumerate(load_dataset(), start=1):
        result = agent.run(
            user_id=f"eval-user-{index}",
            feature="qa",
            session_id=f"eval-session-{index}",
            message=item["question"],
        )
        answer_lower = result.answer.lower()
        matches = {
            phrase: phrase.lower() in answer_lower
            for phrase in item["must_include"]
        }
        negative_matches = {
            phrase: phrase.lower() not in answer_lower
            for phrase in item.get("must_not_include", [])
        }
        starter_cost = agent._estimate_cost(
            result.tokens_in, STARTER_OUTPUT_TOKEN_MIDPOINT
        )
        cases.append(
            {
                "question": item["question"],
                "answer": result.answer,
                "must_include": item["must_include"],
                "matches": matches,
                "negative_matches": negative_matches,
                "passed": all(matches.values()) and all(negative_matches.values()),
                "latency_ms": result.latency_ms,
                "tokens_in": result.tokens_in,
                "tokens_out": result.tokens_out,
                "cost_usd": result.cost_usd,
                "starter_estimated_cost_usd": starter_cost,
            }
        )

    passed = sum(case["passed"] for case in cases)
    total_cost = round(sum(case["cost_usd"] for case in cases), 6)
    starter_cost = round(
        sum(case["starter_estimated_cost_usd"] for case in cases), 6
    )
    savings_pct = (
        round((1 - total_cost / starter_cost) * 100, 2)
        if starter_cost
        else 0.0
    )
    summary = {
        "dataset": str(DATASET_PATH),
        "model": agent.model,
        "pricing_assumption": {
            "input_usd_per_million_tokens": 3,
            "output_usd_per_million_tokens": 15,
        },
        "cases_total": len(cases),
        "cases_passed": passed,
        "pass_rate_pct": round(passed / len(cases) * 100, 2) if cases else 0.0,
        "tokens_in_total": sum(case["tokens_in"] for case in cases),
        "tokens_out_total": sum(case["tokens_out"] for case in cases),
        "evaluated_cost_usd": total_cost,
        "starter_estimated_cost_usd": starter_cost,
        "estimated_cost_reduction_pct": savings_pct,
        "starter_baseline_note": (
            "The original FakeLLM sampled 80-180 output tokens. "
            "The midpoint, 130 tokens, is used as the reproducible baseline."
        ),
        "cases": cases,
    }

    JSON_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    JSON_OUTPUT.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    rows = "\n".join(
        f"| {index} | {'PASS' if case['passed'] else 'FAIL'} | "
        f"{case['tokens_in']} | {case['tokens_out']} | "
        f"${case['cost_usd']:.6f} |"
        for index, case in enumerate(cases, start=1)
    )
    MARKDOWN_OUTPUT.write_text(
        f"""# Quality Eval and Cost Report

## Summary

- Dataset: `{DATASET_PATH}`
- Model label: `{agent.model}` (deterministic local fake)
- Cases passed: `{passed}/{len(cases)}`
- Pass rate: `{summary['pass_rate_pct']:.2f}%`
- Input tokens: `{summary['tokens_in_total']}`
- Output tokens: `{summary['tokens_out_total']}`
- Evaluated cost: `${total_cost:.6f}`
- Starter estimated cost: `${starter_cost:.6f}`
- Estimated cost reduction: `{savings_pct:.2f}%`

Pricing assumption: $3 per million input tokens and $15 per million output
tokens. The starter baseline uses 130 output tokens per case, the midpoint of
the original random 80-180 token range. These are simulated estimates, not a
provider invoice.

## Cases

| # | Result | Input tokens | Output tokens | Cost |
|---:|---|---:|---:|---:|
{rows}

Full answers and phrase-level checks are available in
`docs/evidence/eval-cost-report.json`.
""",
        encoding="utf-8",
    )

    print(json.dumps({key: value for key, value in summary.items() if key != "cases"}, indent=2))
    if passed != len(cases):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
