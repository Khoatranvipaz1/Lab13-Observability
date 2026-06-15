from __future__ import annotations

import os
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

TRACING_CONFIGURED = (
    os.getenv("LANGFUSE_TRACING_ENABLED", "true").lower() != "false"
    and bool(os.getenv("LANGFUSE_PUBLIC_KEY") and os.getenv("LANGFUSE_SECRET_KEY"))
)


def _noop_observe(*args: Any, **kwargs: Any):
    if args and callable(args[0]) and len(args) == 1:
        return args[0]

    def decorator(func):
        return func

    return decorator


if TRACING_CONFIGURED:
    try:
        from langfuse import get_client, observe, propagate_attributes
    except Exception:  # pragma: no cover
        observe = _noop_observe
        get_client = None
        propagate_attributes = None
else:
    observe = _noop_observe
    get_client = None
    propagate_attributes = None


@contextmanager
def trace_attributes(**kwargs: Any):
    if propagate_attributes is None:
        yield
        return
    with propagate_attributes(**kwargs):
        yield


def update_current_span(**kwargs: Any) -> None:
    if get_client is not None:
        get_client().update_current_span(**kwargs)


def update_current_generation(**kwargs: Any) -> None:
    if get_client is not None:
        get_client().update_current_generation(**kwargs)


def flush_traces() -> None:
    if get_client is not None:
        get_client().flush()


def tracing_enabled() -> bool:
    return TRACING_CONFIGURED and get_client is not None
