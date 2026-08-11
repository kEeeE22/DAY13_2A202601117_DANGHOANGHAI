from app.pii import scrub_text


def test_scrub_email() -> None:
    out = scrub_text("Email me at student@vinuni.edu.vn")
    assert "student@" not in out
    assert "REDACTED_EMAIL" in out


def test_scrub_common_vietnamese_phone_formats() -> None:
    phone_numbers = (
        "0901234567",
        "090 123 4567",
        "090.123.4567",
        "090-123-4567",
        "+84 90 123 4567",
    )

    for phone_number in phone_numbers:
        out = scrub_text(f"Contact: {phone_number}")
        assert phone_number not in out
        assert "REDACTED_PHONE_VN" in out


def test_scrub_vietnamese_passport() -> None:
    passports = ("C1234567", "A0123456", "b9876543")

    for passport in passports:
        out = scrub_text(f"Passport: {passport}")
        assert passport.upper() not in out
        assert "REDACTED_PASSPORT" in out


def test_scrub_credit_card_formats() -> None:
    cards = (
        "4111 1111 1111 1111",
        "4111-1111-1111-1111",
        "4111111111111111",
    )

    for card in cards:
        out = scrub_text(f"Card {card}")
        assert card not in out
        assert "REDACTED_CREDIT_CARD" in out


def test_scrub_vietnamese_address() -> None:
    address = "số 12, đường nguyễn trãi, phường bến nghé, quận 1"

    out = scrub_text(f"Address: {address}")

    assert "nguyễn trãi" not in out
    assert "bến nghé" not in out
    assert "REDACTED_ADDRESS_VN" in out


def test_scrub_vietnamese_address_capitalized() -> None:
    # Case-insensitive matching handles capitalized keywords at sentence start.
    address = "Số 12, Đường Nguyễn Trãi, Quận 1, Thành phố Hồ Chí Minh"

    out = scrub_text(f"Address: {address}")

    assert "Nguyễn Trãi" not in out
    assert "REDACTED_ADDRESS_VN" in out


def test_scrub_nested_structures() -> None:
    out = scrub_text("Call 0901234567 or email a@b.com")

    assert "0901234567" not in out
    assert "a@b.com" not in out
    assert "REDACTED_PHONE_VN" in out
    assert "REDACTED_EMAIL" in out
