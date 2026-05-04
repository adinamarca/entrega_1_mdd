from dataclasses import dataclass

from src.domain.shared.domain_event import DomainEvent


@dataclass(frozen=True)
class PedidoAsignado(DomainEvent):
    pedido_id: str = ""
    repartidor_id: str = ""
    estrategia: str = ""


@dataclass(frozen=True)
class PedidoReasignado(DomainEvent):
    pedido_id: str = ""
    repartidor_anterior_id: str = ""
    repartidor_nuevo_id: str = ""
