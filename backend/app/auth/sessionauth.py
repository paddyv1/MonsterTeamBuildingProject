import hmac
import hashlib
import os
from typing import Optional

COOKIE_NAME = "session"

def _secret() -> bytes:
    secret = os.getenv("SESSION_SECRET")
    if not secret:
        raise ValueError("SESSION_SECRET environment variable is not set")
    return secret.encode("utf-8")


def sign(value: str) -> str:
    signature = hmac.new(_secret(), value.encode("utf-8"), hashlib.sha256).hexdigest()
    return f"{value}.{signature}"


def verify(signed_value: str) -> Optional[str]:
    try:
        value, signature = signed_value.rsplit(".", 1)
    except ValueError:
        return None

    expected_signature = hmac.new(_secret(), value.encode("utf-8"), hashlib.sha256).hexdigest()
    if hmac.compare_digest(signature, expected_signature):
        return value
    return None