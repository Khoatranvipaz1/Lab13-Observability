from __future__ import annotations

import os
from typing import Any

TRACING_CONFIGURED = bool(
    os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY")
)


def _noop_observe(*args: Any, **kwargs: Any):
    def decorator(func):
        return func
    return decorator


class _DummyContext:
    def update_current_trace(self, **kwargs: Any) -> None:
        return None

    def update_current_observation(self, **kwargs: Any) -> None:
        return None


if TRACING_CONFIGURED:
    try:
        from langfuse import get_client, observe

        class _LangfuseV3Context:
            def update_current_trace(self, **kwargs: Any) -> None:
                get_client().update_current_trace(**kwargs)

            def update_current_observation(self, **kwargs: Any) -> None:
                usage_details = kwargs.pop("usage_details", None)
                if usage_details:
                    metadata = dict(kwargs.get("metadata") or {})
                    metadata["usage_details"] = usage_details
                    kwargs["metadata"] = metadata
                get_client().update_current_span(**kwargs)

        langfuse_context = _LangfuseV3Context()
    except Exception:  # pragma: no cover
        try:
            from langfuse.decorators import langfuse_context, observe
        except Exception:
            observe = _noop_observe
            langfuse_context = _DummyContext()
else:
    observe = _noop_observe
    langfuse_context = _DummyContext()


def tracing_enabled() -> bool:
    return TRACING_CONFIGURED
