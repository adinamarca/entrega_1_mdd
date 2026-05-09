"""Contenedor de dependencias (DI).

Crea las instancias singleton de repositorios, services y event bus.
FastAPI las inyecta en los controllers via Depends().
"""

from functools import lru_cache

from src.application.despacho_service import DespachoService
from src.application.incidencia_service import IncidenciaService
from src.application.pedido_service import PedidoService
from src.application.repartidor_service import RepartidorService
from src.domain.despacho.estrategias import AsignacionPorProximidad
from src.domain.shared.domain_event import EventBus
from src.infrastructure.repositories.incidencia_repo import (
    InMemoryIncidenciaRepository,
)
from src.infrastructure.repositories.pedido_repo import InMemoryPedidoRepository
from src.infrastructure.repositories.repartidor_repo import (
    InMemoryRepartidorRepository,
)


class Container:
    """Container singleton que mantiene las instancias compartidas."""

    def __init__(self) -> None:
        self.event_bus = EventBus()
        self.pedido_repo = InMemoryPedidoRepository()
        self.repartidor_repo = InMemoryRepartidorRepository()
        self.incidencia_repo = InMemoryIncidenciaRepository()

        self.pedido_service = PedidoService(self.pedido_repo, self.event_bus)
        self.repartidor_service = RepartidorService(self.repartidor_repo)
        self.despacho_service = DespachoService(
            self.pedido_repo, AsignacionPorProximidad(), self.event_bus
        )
        self.incidencia_service = IncidenciaService(
            self.incidencia_repo, self.pedido_repo, self.event_bus
        )


@lru_cache
def get_container() -> Container:
    return Container()


# --- Dependency functions para FastAPI ---


def get_pedido_service() -> PedidoService:
    return get_container().pedido_service


def get_repartidor_service() -> RepartidorService:
    return get_container().repartidor_service


def get_despacho_service() -> DespachoService:
    return get_container().despacho_service


def get_incidencia_service() -> IncidenciaService:
    return get_container().incidencia_service


def get_event_bus() -> EventBus:
    return get_container().event_bus
