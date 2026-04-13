"""State pattern: ciclo de vida de una incidencia.

Estados: Abierta -> En analisis -> En resolucion -> Resuelta
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.incidencias.domain.incidencia import Incidencia


class EstadoIncidencia(ABC):

    @abstractmethod
    def nombre(self) -> str: ...

    def iniciar_analisis(self, incidencia: Incidencia) -> None:
        raise TransicionIncidenciaError(self.nombre(), "En analisis")

    def iniciar_resolucion(self, incidencia: Incidencia) -> None:
        raise TransicionIncidenciaError(self.nombre(), "En resolucion")

    def resolver(self, incidencia: Incidencia) -> None:
        raise TransicionIncidenciaError(self.nombre(), "Resuelta")

    def __str__(self) -> str:
        return self.nombre()


class TransicionIncidenciaError(Exception):
    def __init__(self, estado_actual: str, estado_destino: str) -> None:
        super().__init__(
            f"Transicion invalida en incidencia: "
            f"no se puede pasar de '{estado_actual}' a '{estado_destino}'"
        )


class Abierta(EstadoIncidencia):
    def nombre(self) -> str:
        return "Abierta"

    def iniciar_analisis(self, incidencia: Incidencia) -> None:
        incidencia.cambiar_estado(EnAnalisis())


class EnAnalisis(EstadoIncidencia):
    def nombre(self) -> str:
        return "En analisis"

    def iniciar_resolucion(self, incidencia: Incidencia) -> None:
        incidencia.cambiar_estado(EnResolucion())


class EnResolucion(EstadoIncidencia):
    def nombre(self) -> str:
        return "En resolucion"

    def resolver(self, incidencia: Incidencia) -> None:
        if not incidencia.resolucion:
            raise ValueError(
                "No se puede cerrar la incidencia sin una resolucion asociada"
            )
        incidencia.cambiar_estado(Resuelta())


class Resuelta(EstadoIncidencia):
    """Estado final. No permite mas transiciones."""

    def nombre(self) -> str:
        return "Resuelta"
