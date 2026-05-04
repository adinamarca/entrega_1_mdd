"""Strategy pattern: algoritmos intercambiables de asignacion de repartidores.

OCP: agregar una nueva estrategia no requiere modificar DespachoService.
LSP: todas las estrategias implementan el mismo contrato sin romper comportamiento.
"""

from abc import ABC, abstractmethod

from src.domain.repartidores.repartidor import Repartidor
from src.domain.repartidores.value_objects import Ubicacion


class EstrategiaAsignacion(ABC):
    """Interfaz base del Strategy pattern para seleccion de repartidor."""

    @abstractmethod
    def seleccionar(
        self,
        repartidores_disponibles: list[Repartidor],
        ubicacion_destino: Ubicacion,
    ) -> Repartidor | None:
        """Selecciona el mejor repartidor segun el criterio de la estrategia."""
        ...

    @abstractmethod
    def nombre(self) -> str: ...


class AsignacionPorProximidad(EstrategiaAsignacion):
    """Selecciona el repartidor mas cercano al destino de entrega."""

    def seleccionar(
        self,
        repartidores_disponibles: list[Repartidor],
        ubicacion_destino: Ubicacion,
    ) -> Repartidor | None:
        if not repartidores_disponibles:
            return None
        return min(
            repartidores_disponibles,
            key=lambda r: r.ubicacion.distancia_a(ubicacion_destino),
        )

    def nombre(self) -> str:
        return "Proximidad"


class AsignacionPorCapacidad(EstrategiaAsignacion):
    """Selecciona el repartidor con mayor capacidad disponible."""

    def seleccionar(
        self,
        repartidores_disponibles: list[Repartidor],
        ubicacion_destino: Ubicacion,
    ) -> Repartidor | None:
        if not repartidores_disponibles:
            return None
        return max(
            repartidores_disponibles,
            key=lambda r: r.capacidad.max_pedidos - r.pedidos_actuales,
        )

    def nombre(self) -> str:
        return "Capacidad"


class AsignacionRoundRobin(EstrategiaAsignacion):
    """Distribuye pedidos de forma equitativa entre repartidores."""

    def __init__(self) -> None:
        self._indice = 0

    def seleccionar(
        self,
        repartidores_disponibles: list[Repartidor],
        ubicacion_destino: Ubicacion,
    ) -> Repartidor | None:
        if not repartidores_disponibles:
            return None
        repartidor = repartidores_disponibles[self._indice % len(repartidores_disponibles)]
        self._indice += 1
        return repartidor

    def nombre(self) -> str:
        return "Round Robin"
