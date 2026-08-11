from __future__ import annotations

import hashlib
import re

PII_PATTERNS: dict[str, str] = {
    "email": r"[\w\.-]+@[\w\.-]+\.\w+",
    "phone_vn": r"(?<!\d)(?:\+84|0)(?:[ .-]?\d){9}(?!\d)",
    "cccd": r"\b\d{12}\b",
    "credit_card": r"\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b",
    # Vietnamese passport: one letter followed by 7-8 digits (e.g. C1234567).
    "passport": r"\b[A-Z]\d{7,8}\b",
    # Vietnamese address keywords: house number, street, ward, district, province.
    # Each keyword consumes the following 1-3 tokens (stops at , ; newline) so the
    # street/ward name itself is hidden, not just the keyword.
    # "số" only matches a house number (số + digits) to avoid over-redaction
    # of common phrases like "số lượng"; "số nhà" is matched as a full keyword.
    "address_vn": (
        r"\b(?:số\s*\d+|"
        r"(?:số nhà|thành phố|đường|phường|quận|huyện|tỉnh|xã|ấp)"
        r"\s+[^,\s;]+(?:\s+[^,\s;]+){0,2})"
    ),
}


def scrub_text(text: str) -> str:
    safe = text
    for name, pattern in PII_PATTERNS.items():
        # IGNORECASE handles capitalized Vietnamese address keywords (Đường, Quận, ...).
        safe = re.sub(pattern, f"[REDACTED_{name.upper()}]", safe, flags=re.IGNORECASE)
    return safe


def summarize_text(text: str, max_len: int = 80) -> str:
    safe = scrub_text(text).strip().replace("\n", " ")
    return safe[:max_len] + ("..." if len(safe) > max_len else "")


def hash_user_id(user_id: str) -> str:
    return hashlib.sha256(user_id.encode("utf-8")).hexdigest()[:12]
