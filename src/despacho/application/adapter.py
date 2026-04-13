"""Adapter pattern: traduce modelos entre bounded contexts.

Permite que el BC de Despacho trabaje con datos de Pedidos y Repartidores
sin acoplarse directamente a sus modelos internos.
"""

from dataclasses import dataclass

from src.pedidos.domain.pedido import Pedido
from src.repartidores.domain.repartidor import Repartidor
from src.repartidores.domain.value_objects import Ubicacion


@dataclass(frozen=True)
class PedidoParaDespacho:
    """Representacion simplificada de un pedido dentro del contexto de despacho."""

    pedido_id: str
    destino_latitud: float
    destino_longitud: float
    peso_kg: float
    tipo_entrega: str
    estado: str


@dataclass(frozen=True)
class RepartidorParaDespacho:
    """Representacion simplificada de un repartidor dentro del contexto de despacho."""

    repartidor_id: str
    nombre: str
    ubicacion: Ubicacion
    pedidos_actuales: int
    capacidad_max: int
    disponible: bool


class PedidoAdapter:
    """Adapter: convierte Pedido del BC Pedidos al modelo interno de Despacho."""

    @staticmethod
    def adaptar(pedido: Pedido) -> PedidoParaDespacho:
        return PedidoParaDespacho(
            pedido_id=pedido.pedido_id,
            destino_latitud=pedido.direccion_destino.ciudad.__hash__() % 90,
            destino_longitud=pedido.direccion_destino.comuna.__hash__() % 180,
            peso_kg=pedido.peso_estimado_kg,
            tipo_entrega=pedido.tipo_entrega.value,
            estado=pedido.estado_nombre,
        )


class RepartidorAdapter:
    """Adapter: convierte Repartidor del BC Repartidores al modelo interno de Despacho."""

    @staticmethod
    def adaptar(repartidor: Repartidor) -> RepartidorParaDespacho:
        return RepartidorParaDespacho(
            repartidor_id=repartidor.repartidor_id,
            nombre=repartidor.nombre,
            ubicacion=repartidor.ubicacion,
            pedidos_actuales=repartidor.pedidos_actuales,
            capacidad_max=repartidor.capacidad.max_pedidos,
            disponible=repartidor.disponible,
        )
