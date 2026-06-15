from __future__ import annotations

import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi import Header
from fastapi.responses import FileResponse, JSONResponse
from structlog.contextvars import bind_contextvars, unbind_contextvars

load_dotenv(Path(__file__).resolve().parents[1] / ".env")

from .agent import LabAgent
from .alerts import evaluate_alerts
from .incidents import disable, enable, status
from .logging_config import configure_logging, get_logger
from .metrics import record_error, snapshot
from .middleware import CorrelationIdMiddleware
from .pii import hash_user_id, summarize_text
from .schemas import ChatRequest, ChatResponse
from .tracing import flush_traces, tracing_enabled

configure_logging()
log = get_logger()
agent = LabAgent()
DASHBOARD_PATH = Path(__file__).resolve().parents[1] / "static" / "dashboard.html"


@asynccontextmanager
async def lifespan(_: FastAPI):
    log.info(
        "app_started",
        service=os.getenv("APP_NAME", "day13-observability-lab"),
        env=os.getenv("APP_ENV", "dev"),
        correlation_id="system",
        payload={"tracing_enabled": tracing_enabled()},
    )
    try:
        yield
    finally:
        flush_traces()


app = FastAPI(title="Day 13 Observability Lab", lifespan=lifespan)
app.add_middleware(CorrelationIdMiddleware)


@app.get("/health")
async def health() -> dict:
    return {"ok": True, "tracing_enabled": tracing_enabled(), "incidents": status()}


@app.get("/dashboard", include_in_schema=False)
async def dashboard() -> FileResponse:
    return FileResponse(DASHBOARD_PATH)


@app.get("/metrics")
async def metrics() -> dict:
    return snapshot()


@app.get("/alerts/status")
async def alert_status() -> dict:
    current = snapshot()
    alerts = evaluate_alerts(current)
    return {
        "active_count": sum(alert["active"] for alert in alerts),
        "alerts": alerts,
    }


def _authorize_incident(request: Request, admin_token: str | None) -> None:
    configured = os.getenv("INCIDENT_ADMIN_TOKEN")
    if os.getenv("APP_ENV", "dev") != "dev":
        raise HTTPException(status_code=403, detail="Incident controls are disabled")
    if request.client and request.client.host not in {"127.0.0.1", "::1", "testclient"}:
        raise HTTPException(status_code=403, detail="Incident controls are local-only")
    if not configured or admin_token != configured:
        raise HTTPException(status_code=401, detail="Invalid incident admin token")


@app.post("/chat", response_model=ChatResponse)
async def chat(request: Request, body: ChatRequest) -> ChatResponse:
    bind_contextvars(
        user_id_hash=hash_user_id(body.user_id),
        session_id=hash_user_id(body.session_id),
        feature=body.feature,
        model=agent.model,
        env=os.getenv("APP_ENV", "dev"),
    )

    log.info(
        "request_received",
        service="api",
        payload={"message_preview": summarize_text(body.message)},
    )
    try:
        result = agent.run(
            user_id=body.user_id,
            feature=body.feature,
            session_id=body.session_id,
            message=body.message,
        )
        log.info(
            "response_sent",
            service="api",
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            payload={"answer_preview": summarize_text(result.answer)},
        )
        return ChatResponse(
            answer=result.answer,
            correlation_id=request.state.correlation_id,
            latency_ms=result.latency_ms,
            tokens_in=result.tokens_in,
            tokens_out=result.tokens_out,
            cost_usd=result.cost_usd,
            quality_score=result.quality_score,
        )
    except Exception as exc:  # pragma: no cover
        error_type = type(exc).__name__
        record_error(error_type)
        log.error(
            "request_failed",
            service="api",
            error_type=error_type,
            payload={"detail": str(exc), "message_preview": summarize_text(body.message)},
        )
        raise HTTPException(status_code=500, detail=error_type) from exc
    finally:
        unbind_contextvars("user_id_hash", "session_id", "feature", "model", "env")


@app.post("/incidents/{name}/enable")
async def enable_incident(
    name: str,
    request: Request,
    x_admin_token: str | None = Header(default=None),
) -> JSONResponse:
    _authorize_incident(request, x_admin_token)
    try:
        enable(name)
        log.warning(
            "incident_enabled",
            service="control",
            env=os.getenv("APP_ENV", "dev"),
            audit=True,
            payload={"name": name},
        )
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/incidents/{name}/disable")
async def disable_incident(
    name: str,
    request: Request,
    x_admin_token: str | None = Header(default=None),
) -> JSONResponse:
    _authorize_incident(request, x_admin_token)
    try:
        disable(name)
        log.warning(
            "incident_disabled",
            service="control",
            env=os.getenv("APP_ENV", "dev"),
            audit=True,
            payload={"name": name},
        )
        return JSONResponse({"ok": True, "incidents": status()})
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
