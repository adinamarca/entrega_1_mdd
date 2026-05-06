"""Pydantic schemas para los endpoints de Despacho."""

from pydantic import BaseModel, Field


class AsignarPedidoRequest(BaseModel):
    """Body para POST /pedidos/{id}/asignar.

    La estrategia es opcional; si no se especifica usa la default del servicio.
    """

    estrategia: str | None = Field(
        None, description="proximidad | capacidad | round_robin"
    )


class AsignacionResponse(BaseModel):
    """Representacion de una asignacion en respuestas HTTP."""

    asignacion_id: str
    pedido_id: str
    repartidor_id: str
    estrategia_usada: str
    activa: bool
