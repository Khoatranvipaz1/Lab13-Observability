from app.pii import scrub_text


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
