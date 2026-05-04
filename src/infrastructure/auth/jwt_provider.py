"""Proveedor de JWT para autenticacion stateless.

Genera y valida tokens firmados con HS256. El secret se lee desde
variable de entorno JWT_SECRET (con fallback para desarrollo).
"""

from __future__ import annotations

import os
from datetime import datetime, timedelta, timezone

import jwt

from src.infrastructure.auth.roles import Rol


JWT_SECRET = os.getenv("JWT_SECRET", "demo_secret_change_me")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRATION_MINUTES = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))


class TokenInvalidError(Exception):
    pass


def generar_token(username: str, rol: Rol) -> tuple[str, int]:
    """Genera un JWT y retorna (token, ttl_segundos)."""
    expira_en = datetime.now(timezone.utc) + timedelta(
        minutes=JWT_EXPIRATION_MINUTES
    )
    payload = {
        "sub": username,
        "rol": rol.value,
        "exp": expira_en,
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token, JWT_EXPIRATION_MINUTES * 60


def validar_token(token: str) -> dict:
    """Valida un JWT y retorna el payload. Lanza TokenInvalidError si falla."""
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError as exc:
        raise TokenInvalidError("Token expirado") from exc
    except jwt.InvalidTokenError as exc:
        raise TokenInvalidError(f"Token invalido: {exc}") from exc
