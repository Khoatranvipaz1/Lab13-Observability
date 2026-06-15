import json

import pytest

from scripts import validate_logs


def _valid_record() -> dict:
    return {
        "ts": "2026-06-15T08:00:00Z",
        "level": "info",
        "service": "api",
        "event": "request_received",
        "correlation_id": "req-test0001",
        "env": "test",
        "user_id_hash": "abc123",
        "session_id": "def456",
        "feature": "qa",
        "model": "fake-model",
        "payload": {"message_preview": "safe"},
    }


def test_validator_rejects_malformed_json_and_scans_it_for_pii(
    tmp_path,
    monkeypatch,
    capsys,
) -> None:
    log_path = tmp_path / "logs.jsonl"
    schema_path = tmp_path / "schema.json"
    schema_path.write_text(
        validate_logs.SCHEMA_PATH.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    second_record = _valid_record()
    second_record["correlation_id"] = "req-test0002"
    log_path.write_text(
        "\n".join(
            [
                json.dumps(_valid_record()),
                json.dumps(second_record),
                '{"email":"student@example.com"',
            ]
        )
        + "\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(validate_logs, "LOG_PATH", log_path)
    monkeypatch.setattr(validate_logs, "SCHEMA_PATH", schema_path)

    validate_logs.main()

    output = capsys.readouterr().out
    assert "Malformed JSON records: 1" in output
    assert "Potential PII leaks detected: 1" in output
    assert "[FAILED] JSONL and schema validation" in output
    assert "Estimated Score: 40/100" in output


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("ts", "not-a-timestamp"),
        ("level", "verbose"),
        ("unexpected", "value"),
    ],
)
def test_schema_rejects_invalid_or_unknown_fields(field, value) -> None:
    record = _valid_record()
    record[field] = value
    validator = validate_logs.Draft202012Validator(
        json.loads(validate_logs.SCHEMA_PATH.read_text(encoding="utf-8"))
    )

    assert list(validator.iter_errors(record))
