from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4

from src.domain.incidencias.estados import Abierta, EstadoIncidencia
from src.domain.incidencias.value_objects import Resolucion, TipoIncidencia


@dataclass
class Incidencia:
    """Aggregate Root del bounded context de Incidencias.

    Toda incidencia debe estar asociada a un pedido.
    No puede cerrarse sin resolucion.
    """

    incidencia_id: str
    pedido_id: str
    tipo: TipoIncidencia
    descripcion: str
    fecha_creacion: datetime = field(default_factory=datetime.now)
    resolucion: Resolucion | None = None
    _estado: EstadoIncidencia = field(default_factory=Abierta)

    @property
    def estado(self) -> EstadoIncidencia:
        return self._estado

    @property
    def estado_nombre(self) -> str:
        return self._estado.nombre()

    def cambiar_estado(self, nuevo_estado: EstadoIncidencia) -> None:
        self._estado = nuevo_estado

    # --- Operaciones delegadas al estado (State pattern) ---

    def iniciar_analisis(self) -> None:
        self._estado.iniciar_analisis(self)

    def iniciar_resolucion(self) -> None:
        self._estado.iniciar_resolucion(self)

    def asignar_resolucion(self, resolucion: Resolucion) -> None:
        self.resolucion = resolucion

    def resolver(self) -> None:
        self._estado.resolver(self)

    def __str__(self) -> str:
        return (
            f"Incidencia({self.incidencia_id[:8]}... | "
            f"pedido={self.pedido_id[:8]}... | "
            f"tipo={self.tipo.value} | estado={self.estado_nombre})"
        )


def generar_incidencia_id() -> str:
    return str(uuid4())
