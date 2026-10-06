import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, Request, status

from app.config import get_settings
from app.database import get_user


ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt,
        240_000,
    )
    return f"pbkdf2_sha256$240000${salt.hex()}${digest.hex()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt_hex, digest_hex = encoded.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        candidate = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations),
        )
        return hmac.compare_digest(candidate.hex(), digest_hex)
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: int) -> str:
    settings = get_settings()
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }
    return jwt.encode(payload, settings.secret_key, algorithm=ALGORITHM)


def decode_access_token(token: str) -> int | None:
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        return int(payload["sub"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        return None


def current_user(request: Request) -> dict:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    user_id = decode_access_token(token)
    user = get_user(user_id) if user_id else None
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session",
        )
    return user


def optional_user(request: Request) -> dict | None:
    token = request.cookies.get("access_token")
    if not token:
        return None
    user_id = decode_access_token(token)
    return get_user(user_id) if user_id else None


def require_user(user=Depends(current_user)):
    return user
