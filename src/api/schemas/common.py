"""Schemas comunes para respuestas y errores."""

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Respuesta estandar de error."""

    error: str
    detail: str | None = None


class MessageResponse(BaseModel):
    """Respuesta estandar de mensaje informativo."""

    message: str
