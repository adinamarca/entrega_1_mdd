"""Pydantic schemas para autenticacion."""

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    """Body para POST /auth/login."""

    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    """Respuesta con el JWT generado."""

    access_token: str
    token_type: str = "bearer"
    role: str
    expires_in: int
