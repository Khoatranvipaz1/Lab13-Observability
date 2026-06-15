import pytest

from app import incidents, logging_config, metrics


@pytest.fixture(autouse=True)
def isolate_runtime_state(tmp_path, monkeypatch):
    metrics.reset()
    for name in incidents.STATE:
        incidents.STATE[name] = False
    monkeypatch.setattr(logging_config, "LOG_PATH", tmp_path / "logs.jsonl")
    monkeypatch.setattr(logging_config, "AUDIT_LOG_PATH", tmp_path / "audit.jsonl")
    monkeypatch.setenv("INCIDENT_ADMIN_TOKEN", "test-admin-token")
    yield
    metrics.reset()
    for name in incidents.STATE:
        incidents.STATE[name] = False
