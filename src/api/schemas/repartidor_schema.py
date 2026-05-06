"""Pydantic schemas para los endpoints de Repartidores."""

from pydantic import BaseModel, Field


class CrearRepartidorRequest(BaseModel):
    """Body para POST /repartidores."""

    nombre: str = Field(..., min_length=1)
    max_pedidos: int = Field(..., gt=0)
    max_peso_kg: float = Field(..., gt=0)
    latitud: float
    longitud: float


class RepartidorResponse(BaseModel):
    """Representacion del repartidor en respuestas HTTP."""

    repartidor_id: str
    nombre: str
    capacidad_max: int
    pedidos_actuales: int
    disponible: bool
    latitud: float
    longitud: float


class CambioDisponibilidadRequest(BaseModel):
    """Body para PUT /repartidores/{id}/disponibilidad."""

    disponible: bool
