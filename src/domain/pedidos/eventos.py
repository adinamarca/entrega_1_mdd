from dataclasses import dataclass

from src.domain.shared.domain_event import DomainEvent


@dataclass(frozen=True)
class PedidoCreado(DomainEvent):
    pedido_id: str = ""
    canal: str = ""


@dataclass(frozen=True)
class PedidoValidado(DomainEvent):
    pedido_id: str = ""


@dataclass(frozen=True)
class PedidoCambioEstado(DomainEvent):
    pedido_id: str = ""
    estado_anterior: str = ""
    estado_nuevo: str = ""


@dataclass(frozen=True)
class PedidoCancelado(DomainEvent):
    pedido_id: str = ""
    motivo: str = ""
