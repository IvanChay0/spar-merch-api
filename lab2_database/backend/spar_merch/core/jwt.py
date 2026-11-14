from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt

from core.config import get_settings

settings = get_settings()


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Создает JWT Access Token.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_LIFETIME_MINUTES)

    to_encode.update({"exp": expire, "type": "access"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """
    Создает JWT Refresh Token (живет дольше, чем access token).
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_LIFETIME_DAYS)

    to_encode.update({"exp": expire, "type": "refresh"})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        algorithm=settings.JWT_ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict | None:
    """
    Декодирует и проверяет валидность JWT токена.
    Возвращает payload (словарь с данными) или None, если токен невалиден/протух.
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except JWTError:
        return None