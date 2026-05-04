from __future__ import annotations

from dataclasses import dataclass, field
from uuid import uuid4

from src.domain.pedidos.estados import Creado, EstadoPedido
from src.domain.pedidos.value_objects import CanalOrigen, TipoCarga, TipoEntrega
from src.domain.shared.domain_event import DomainEvent
from src.domain.shared.value_objects import ContactInfo, Direccion


@dataclass
class Pedido:
    """Aggregate Root del bounded context de Pedidos.

    Representa una solicitud de entrega desde un origen a un destino.
    Su ciclo de vida se gestiona a traves del State pattern.
    """

    pedido_id: str
    canal: CanalOrigen
    direccion_origen: Direccion
    punto_origen_id: str
    direccion_destino: Direccion
    destinatario: ContactInfo
    tipo_entrega: TipoEntrega
    tipo_carga: TipoCarga
    peso_estimado_kg: float
    ventana_tiempo: str | None = None
    repartidor_id: str | None = None
    _estado: EstadoPedido = field(default_factory=Creado)
    _eventos: list[DomainEvent] = field(default_factory=list, repr=False)

    @property
    def estado(self) -> EstadoPedido:
        return self._estado

    @property
    def estado_nombre(self) -> str:
        return self._estado.nombre()

    def cambiar_estado(self, nuevo_estado: EstadoPedido) -> None:
        """Metodo interno usado por los estados para realizar la transicion."""
        self._estado = nuevo_estado

    # --- Operaciones delegadas al estado actual (State pattern) ---

    def validar(self) -> None:
        self._estado.validar(self)

    def poner_pendiente(self) -> None:
        self._estado.poner_pendiente(self)

    def asignar(self, repartidor_id: str) -> None:
        self._estado.asignar(self)
        self.repartidor_id = repartidor_id

    def iniciar_ruta(self) -> None:
        self._estado.iniciar_ruta(self)

    def registrar_intento_fallido(self) -> None:
        self._estado.registrar_intento_fallido(self)

    def reprogramar(self) -> None:
        self._estado.reprogramar(self)

    def entregar(self) -> None:
        self._estado.entregar(self)

    def cancelar(self) -> None:
        self._estado.cancelar(self)

    # --- Eventos de dominio ---

    def registrar_evento(self, evento: DomainEvent) -> None:
        self._eventos.append(evento)

    def obtener_eventos(self) -> list[DomainEvent]:
        eventos = list(self._eventos)
        self._eventos.clear()
        return eventos

    def __str__(self) -> str:
        return (
            f"Pedido({self.pedido_id[:8]}... | {self.canal.value} | "
            f"estado={self.estado_nombre})"
        )


def generar_pedido_id() -> str:
    return str(uuid4())
