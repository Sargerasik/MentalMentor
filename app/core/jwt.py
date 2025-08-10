from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Tuple
from uuid import uuid4

from jose import jwt, JWTError

from app.core.settings import settings

TokenType = Literal["access", "refresh"]

def _now() -> datetime:
    return datetime.now(timezone.utc)

def _exp(minutes: int | None = None, days: int | None = None) -> datetime:
    delta = timedelta(minutes=minutes or 0, days=days or 0)
    return _now() + delta

def create_token(*, sub: str, type_: TokenType, extra: dict[str, Any] | None = None) -> Tuple[str, str]:
    """
    Возвращает (token, jti). Для refresh используем Redis (jti -> user_id) как источник истины.
    """
    jti = str(uuid4())
    payload = {
        "sub": sub,
        "jti": jti,
        "type": type_,
        "iat": int(_now().timestamp()),
        "nbf": int(_now().timestamp()),
        "iss": settings.APP_NAME,
        "aud": settings.APP_NAME,
    }
    if type_ == "access":
        payload["exp"] = int(_exp(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES).timestamp())
    else:
        payload["exp"] = int(_exp(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).timestamp())

    if extra:
        payload.update(extra)

    token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
    return token, jti

def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(
        token,
        settings.JWT_SECRET,
        algorithms=[settings.JWT_ALG],
        audience=settings.APP_NAME,
        options={"verify_aud": True},
    )

def is_access(payload: dict[str, Any]) -> bool:
    return payload.get("type") == "access"

def is_refresh(payload: dict[str, Any]) -> bool:
    return payload.get("type") == "refresh"
