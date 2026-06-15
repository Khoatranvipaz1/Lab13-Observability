import json

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
