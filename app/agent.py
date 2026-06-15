from __future__ import annotations

import time
from dataclasses import dataclass

from . import metrics
from .mock_llm import FakeLLM
from .mock_rag import retrieve
from .pii import hash_user_id, scrub_text, summarize_text
from .tracing import observe, trace_attributes, update_current_span


@dataclass
class AgentResult:
    answer: str
    latency_ms: int
    tokens_in: int
    tokens_out: int
    cost_usd: float
    quality_score: float


class LabAgent:
    def __init__(self, model: str = "claude-sonnet-4-5") -> None:
        self.model = model
        self.llm = FakeLLM(model=model)

    @observe(name="chat-response", capture_input=False, capture_output=False)
    def run(self, user_id: str, feature: str, session_id: str, message: str) -> AgentResult:
        started = time.perf_counter()
        safe_feature = scrub_text(feature)[:64]
        update_current_span(
            input={"query_preview": summarize_text(message), "feature": safe_feature},
        )
        with trace_attributes(
            trace_name="chat-response",
            user_id=hash_user_id(user_id),
            session_id=hash_user_id(session_id),
            tags=["lab", safe_feature, self.model],
            metadata={"feature": safe_feature, "model": self.model},
        ):
            docs = retrieve(message)
            prompt = f"Feature={feature}\nDocs={docs}\nQuestion={message}"
            response = self.llm.generate(prompt)
            quality_score = self._heuristic_quality(message, response.text, docs)
            latency_ms = int((time.perf_counter() - started) * 1000)
            cost_usd = self._estimate_cost(
                response.usage.input_tokens,
                response.usage.output_tokens,
            )

            metrics.record_request(
                latency_ms=latency_ms,
                cost_usd=cost_usd,
                tokens_in=response.usage.input_tokens,
                tokens_out=response.usage.output_tokens,
                quality_score=quality_score,
            )

            result = AgentResult(
                answer=response.text,
                latency_ms=latency_ms,
                tokens_in=response.usage.input_tokens,
                tokens_out=response.usage.output_tokens,
                cost_usd=cost_usd,
                quality_score=quality_score,
            )
            update_current_span(
                output={
                    "answer_preview": summarize_text(response.text),
                    "quality_score": quality_score,
                },
                metadata={
                    "doc_count": str(len(docs)),
                    "latency_ms": str(latency_ms),
                    "cost_usd": f"{cost_usd:.6f}",
                },
            )
            return result

    def _estimate_cost(self, tokens_in: int, tokens_out: int) -> float:
        input_cost = (tokens_in / 1_000_000) * 3
        output_cost = (tokens_out / 1_000_000) * 15
        return round(input_cost + output_cost, 6)

    def _heuristic_quality(self, question: str, answer: str, docs: list[str]) -> float:
        score = 0.5
        if docs:
            score += 0.2
        if len(answer) > 40:
            score += 0.1
        if question.lower().split()[0:1] and any(token in answer.lower() for token in question.lower().split()[:3]):
            score += 0.1
        if "[REDACTED" in answer:
            score -= 0.2
        return round(max(0.0, min(1.0, score)), 2)
