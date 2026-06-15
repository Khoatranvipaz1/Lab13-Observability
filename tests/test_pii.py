import json

from app.logging_config import scrub_event
from app.pii import detect_pii, scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_sensitive_values() -> None:
    text = (
        "Phone 090 123 4567, card 4111 1111 1111 1111, "
        "Passport: A1234567, địa chỉ: 123 Nguyen Trai, Quan 1, TP HCM"
    )
    out = scrub_text(text)
    assert "090 123 4567" not in out
    assert "4111" not in out
    assert "A1234567" not in out
    assert "123 Nguyen Trai" not in out


def test_scrub_plus_address_email() -> None:
    out = scrub_text("Email a+b@example.co.uk for support")
    assert "a+b@" not in out
    assert "[REDACTED_EMAIL]" in out
    assert detect_pii(out) == []


def test_scrub_nested_payload() -> None:
    event = {
        "payload": {
            "contacts": [
                "a+b@example.co.uk",
                {"phone": "+84 987 654 321"},
            ]
        }
    }
    scrubbed = scrub_event(None, "info", event)
    assert detect_pii(json.dumps(scrubbed)) == []
