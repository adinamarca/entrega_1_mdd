"""Pydantic schemas para los endpoints de Pedidos."""

from pydantic import BaseModel, Field


class DireccionSchema(BaseModel):
    calle: str
    numero: str
    ciudad: str
    comuna: str


class ContactInfoSchema(BaseModel):
    nombre: str
    telefono: str | None = None
    email: str | None = None


class CrearPedidoRequest(BaseModel):
    """Body para POST /pedidos."""

    canal: str = Field(..., description="web | app_movil | ecommerce | partner")
    origen: DireccionSchema
    punto_origen_id: str
    destino: DireccionSchema
    destinatario: ContactInfoSchema
    tipo_entrega: str = Field(..., description="normal | express | programada")
    tipo_carga: str = Field(..., description="estandar | fragil | voluminoso")
    peso_kg: float = Field(..., gt=0)
    ventana_tiempo: str | None = None

    def to_factory_data(self) -> dict:
        """Convierte el schema HTTP al dict que espera la fabrica del E1."""
        return {
            "origen_calle": self.origen.calle,
            "origen_numero": self.origen.numero,
            "origen_ciudad": self.origen.ciudad,
            "origen_comuna": self.origen.comuna,
            "punto_origen_id": self.punto_origen_id,
            "destino_calle": self.destino.calle,
            "destino_numero": self.destino.numero,
            "destino_ciudad": self.destino.ciudad,
            "destino_comuna": self.destino.comuna,
            "destinatario_nombre": self.destinatario.nombre,
            "destinatario_telefono": self.destinatario.telefono,
            "destinatario_email": self.destinatario.email,
            "tipo_entrega": self.tipo_entrega,
            "tipo_carga": self.tipo_carga,
            "peso_kg": self.peso_kg,
            "ventana_tiempo": self.ventana_tiempo,
        }


class PedidoResponse(BaseModel):
    """Representacion del pedido en respuestas HTTP."""

    pedido_id: str
    canal: str
    estado: str
    tipo_entrega: str
    tipo_carga: str
    peso_kg: float
    direccion_destino: str
    destinatario: str
    repartidor_id: str | None = None


class CambioEstadoRequest(BaseModel):
    """Body para PUT /pedidos/{id}/estado."""

    accion: str = Field(
        ...,
        description=(
            "validar | poner_pendiente | iniciar_ruta | intento_fallido | "
            "reprogramar | entregar | cancelar"
        ),
    )


class ValidacionResponse(BaseModel):
    """Resultado de validar un pedido (puede contener errores)."""

    pedido_id: str
    valido: bool
    errores: list[str]
    estado: str
