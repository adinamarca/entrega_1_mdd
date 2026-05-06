"""Pydantic schemas para los endpoints de Incidencias."""

from pydantic import BaseModel, Field


class CrearIncidenciaRequest(BaseModel):
    """Body para POST /incidencias."""

    pedido_id: str
    tipo: str = Field(
        ...,
        description=(
            "producto_no_recibido | producto_danado | entrega_incorrecta | retraso | otro"
        ),
    )
    descripcion: str = Field(..., min_length=1)


class ResolverIncidenciaRequest(BaseModel):
    """Body para PUT /incidencias/{id}/resolver."""

    descripcion_resolucion: str
    accion_tomada: str
    requiere_reenvio: bool = False


class IncidenciaResponse(BaseModel):
    """Representacion de una incidencia en respuestas HTTP."""

    incidencia_id: str
    pedido_id: str
    tipo: str
    descripcion: str
    estado: str
    resolucion: str | None = None
