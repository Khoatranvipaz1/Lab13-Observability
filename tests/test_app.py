import json
import importlib
from pathlib import Path

from fastapi.testclient import TestClient

from app.main import app


def test_chat_propagates_correlation_id_and_scrubs_logs(tmp_path, monkeypatch) -> None:
    from app import logging_config

    log_path = tmp_path / "logs.jsonl"
    monkeypatch.setattr(logging_config, "LOG_PATH", log_path)

    with TestClient(app) as client:
        response = client.post(
            "/chat",
            headers={"x-request-id": "req-demo1234"},
            json={
                "user_id": "student@vinuni.edu.vn",
                "session_id": "session-1",
                "feature": "qa",
                "message": "Contact student@vinuni.edu.vn or use 4111 1111 1111 1111",
            },
        )

    assert response.status_code == 200
    assert response.headers["x-request-id"] == "req-demo1234"
    assert float(response.headers["x-response-time-ms"]) >= 0

    records = [
        json.loads(line)
        for line in log_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    api_records = [record for record in records if record.get("service") == "api"]
    assert api_records
    assert all(record["correlation_id"] == "req-demo1234" for record in api_records)
    assert all(
        {"user_id_hash", "session_id", "feature", "model", "env"} <= record.keys()
        for record in api_records
    )
    raw = json.dumps(records)
    assert "student@" not in raw
    assert "4111" not in raw


def test_dashboard_is_available() -> None:
    with TestClient(app) as client:
        response = client.get("/dashboard")

    assert response.status_code == 200
    assert "Observability Control Room" in response.text


def test_langfuse_v3_adapter_moves_usage_into_metadata(monkeypatch) -> None:
    from app import tracing

    calls = []

    class FakeClient:
        def update_current_trace(self, **kwargs):
            calls.append(("trace", kwargs))

        def update_current_span(self, **kwargs):
            calls.append(("span", kwargs))

    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-test")
    monkeypatch.setattr("langfuse.get_client", lambda: FakeClient())
    reloaded = importlib.reload(tracing)

    reloaded.langfuse_context.update_current_observation(
        metadata={"doc_count": 1},
        usage_details={"input": 10, "output": 20},
    )

    assert calls == [
        (
            "span",
            {
                "metadata": {
                    "doc_count": 1,
                    "usage_details": {"input": 10, "output": 20},
                }
            },
        )
    ]

    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY")
    monkeypatch.delenv("LANGFUSE_SECRET_KEY")
    importlib.reload(tracing)


def test_agent_answers_expected_eval_phrases() -> None:
    from app.agent import LabAgent

    agent = LabAgent()
    cases = [
        json.loads(line)
        for line in Path("data/expected_answers.jsonl")
        .read_text(encoding="utf-8")
        .splitlines()
        if line.strip()
    ]

    for index, case in enumerate(cases):
        result = agent.run(
            user_id=f"test-{index}",
            feature="qa",
            session_id=f"test-session-{index}",
            message=case["question"],
        )
        answer = result.answer.lower()
        assert all(
            phrase.lower() in answer for phrase in case["must_include"]
        )
        assert all(
            phrase.lower() not in answer
            for phrase in case.get("must_not_include", [])
        )


def test_incident_control_requires_token() -> None:
    with TestClient(app) as client:
        unauthorized = client.post("/incidents/tool_fail/enable")
        authorized = client.post(
            "/incidents/tool_fail/enable",
            headers={"x-admin-token": "test-admin-token"},
        )
        health = client.get("/health")

    assert unauthorized.status_code == 401
    assert authorized.status_code == 200
    assert health.json()["incidents"]["tool_fail"] is True


def test_alert_status_reports_active_error_alert() -> None:
    from app import metrics

    metrics.record_request(6001, 0.011, 10, 20, 0.8)
    metrics.record_error("RuntimeError")
    with TestClient(app) as client:
        response = client.get("/alerts/status")

    assert response.status_code == 200
    payload = response.json()
    high_error = next(
        alert for alert in payload["alerts"] if alert["name"] == "high_error_rate"
    )
    high_latency = next(
        alert for alert in payload["alerts"] if alert["name"] == "high_latency_p95"
    )
    cost_spike = next(
        alert for alert in payload["alerts"] if alert["name"] == "cost_budget_spike"
    )
    assert high_error["active"] is True
    assert high_latency["active"] is True
    assert cost_spike["active"] is True


def test_agent_explicit_trace_metadata_does_not_contain_raw_pii(monkeypatch) -> None:
    from app import agent as agent_module

    calls = []

    class FakeContext:
        def update_current_trace(self, **kwargs):
            calls.append(kwargs)

        def update_current_observation(self, **kwargs):
            calls.append(kwargs)

    monkeypatch.setattr(agent_module, "langfuse_context", FakeContext())
    result = agent_module.LabAgent().run(
        user_id="student@example.com",
        feature="qa",
        session_id="private-session",
        message="My email is student@example.com. What is the refund policy?",
    )

    serialized = json.dumps(calls)
    assert result.answer
    assert "student@example.com" not in serialized
    assert "private-session" not in serialized
    assert "[REDACTED_EMAIL]" in serialized
