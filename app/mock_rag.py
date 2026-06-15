from __future__ import annotations

import time

from .incidents import STATE
from .pii import summarize_text
from .tracing import observe, update_current_span

CORPUS = {
    "refund": ["Refunds are available within 7 days with proof of purchase."],
    "monitoring": ["Metrics detect incidents, traces localize them, logs explain root cause."],
    "policy": ["Do not expose PII in logs. Use sanitized summaries only."],
}


@observe(name="knowledge-retrieval", capture_input=False, capture_output=False)
def retrieve(message: str) -> list[str]:
    update_current_span(input={"query_preview": summarize_text(message)})
    if STATE["tool_fail"]:
        raise RuntimeError("Vector store timeout")
    if STATE["rag_slow"]:
        time.sleep(5.2)
    lowered = message.lower()
    for key, docs in CORPUS.items():
        if key in lowered:
            update_current_span(
                output={"matched_topic": key, "document_count": len(docs)}
            )
            return docs
    docs = ["No domain document matched. Use general fallback answer."]
    update_current_span(output={"matched_topic": "fallback", "document_count": 1})
    return docs
