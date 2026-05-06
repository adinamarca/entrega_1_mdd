"""Manejo global de errores de negocio.

Traduce excepciones del dominio a respuestas HTTP con codigos correctos:
- TransicionInvalidaError -> 409 Conflict
- ValueError (regla de negocio) -> 422 Unprocessable Entity
- KeyError / not found -> 404 Not Found
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.incidencias.estados import TransicionIncidenciaError
from src.domain.pedidos.estados import TransicionInvalidaError


def register_exception_handlers(app: FastAPI) -> None:
    """Registra los handlers globales en la app FastAPI."""

    @app.exception_handler(TransicionInvalidaError)
    async def _transicion_pedido(_: Request, exc: TransicionInvalidaError):
        return JSONResponse(
            status_code=409,
            content={"error": "transicion_invalida", "detail": str(exc)},
        )

    @app.exception_handler(TransicionIncidenciaError)
    async def _transicion_incidencia(_: Request, exc: TransicionIncidenciaError):
        return JSONResponse(
            status_code=409,
            content={"error": "transicion_invalida", "detail": str(exc)},
        )

    @app.exception_handler(ValueError)
    async def _value_error(_: Request, exc: ValueError):
        mensaje = str(exc)
        # Discriminar "no encontrado" vs reglas de negocio
        if "no encontrado" in mensaje.lower():
            return JSONResponse(
                status_code=404,
                content={"error": "no_encontrado", "detail": mensaje},
            )
        return JSONResponse(
            status_code=422,
            content={"error": "regla_de_negocio", "detail": mensaje},
        )
