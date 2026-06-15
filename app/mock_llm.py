from __future__ import annotations

import time
from dataclasses import dataclass

from .incidents import STATE
from .pii import summarize_text
from .tracing import observe, update_current_generation


@dataclass
class FakeUsage:
    input_tokens: int
    output_tokens: int


@dataclass
class FakeResponse:
    text: str
    usage: FakeUsage
    model: str


class FakeLLM:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model

    @observe(
        name="fake-llm-generation",
        as_type="generation",
        capture_input=False,
        capture_output=False,
    )
    def generate(self, prompt: str) -> FakeResponse:
        update_current_generation(
            model=self.model,
            input={"prompt_preview": summarize_text(prompt)},
        )
        time.sleep(0.15)
        input_tokens = max(20, len(prompt) // 4)
        lowered = prompt.lower()
        if "refund" in lowered or "money back" in lowered:
            answer = "Refunds are available within 7 days with proof of purchase."
        elif all(term in lowered for term in ("metrics", "traces", "logs")):
            answer = (
                "Metrics detect incidents, traces localize the failing operation, "
                "and logs explain the root cause."
            )
        elif "pii" in lowered or "should not appear" in lowered:
            answer = (
                "PII and other sensitive data should not appear in application logs. "
                "Log only sanitized summaries."
            )
        elif "tail latency" in lowered:
            answer = (
                "Use P95 and P99 metrics to detect tail latency, then inspect the "
                "slowest traces and their correlated logs."
            )
        elif "alert" in lowered:
            answer = (
                "Alerts should be symptom-based, tied to an SLO threshold, assigned "
                "an owner, and linked to a tested runbook."
            )
        elif "no domain document matched" in lowered:
            answer = (
                "There is not enough domain context to answer this question safely. "
                "Please provide an approved knowledge source."
            )
        else:
            answer = (
                "Use metrics to detect service symptoms, traces to localize slow or "
                "failed operations, and sanitized logs to explain the root cause."
            )
        output_tokens = max(8, len(answer) // 4)
        if STATE["cost_spike"]:
            output_tokens *= 4
        update_current_generation(
            model=self.model,
            output={"answer_preview": summarize_text(answer)},
            usage_details={
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
            },
        )
        return FakeResponse(text=answer, usage=FakeUsage(input_tokens, output_tokens), model=self.model)
