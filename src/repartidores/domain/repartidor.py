from dataclasses import dataclass, field
from uuid import uuid4

from src.repartidores.domain.value_objects import Capacidad, Ubicacion


@dataclass
class Repartidor:
    """Entidad que representa a un repartidor de la flota.

    Gestiona su disponibilidad, capacidad y pedidos asignados.
    """

    repartidor_id: str
    nombre: str
    capacidad: Capacidad
    ubicacion: Ubicacion
    disponible: bool = True
    pedidos_asignados: list[str] = field(default_factory=list)

    @property
    def pedidos_actuales(self) -> int:
        return len(self.pedidos_asignados)

    @property
    def tiene_capacidad(self) -> bool:
        return self.pedidos_actuales < self.capacidad.max_pedidos

    @property
    def puede_recibir_pedido(self) -> bool:
        return self.disponible and self.tiene_capacidad

    def asignar_pedido(self, pedido_id: str) -> None:
        if not self.disponible:
            raise ValueError(
                f"Repartidor {self.nombre} no esta disponible"
            )
        if not self.tiene_capacidad:
            raise ValueError(
                f"Repartidor {self.nombre} ha alcanzado su capacidad maxima "
                f"({self.capacidad.max_pedidos} pedidos)"
            )
        self.pedidos_asignados.append(pedido_id)

    def liberar_pedido(self, pedido_id: str) -> None:
        if pedido_id in self.pedidos_asignados:
            self.pedidos_asignados.remove(pedido_id)

    def marcar_disponible(self) -> None:
        self.disponible = True

    def marcar_no_disponible(self) -> None:
        self.disponible = False

    def actualizar_ubicacion(self, nueva_ubicacion: Ubicacion) -> None:
        object.__setattr__(self, "ubicacion", nueva_ubicacion)

    def __str__(self) -> str:
        return (
            f"Repartidor({self.nombre} | "
            f"pedidos={self.pedidos_actuales}/{self.capacidad.max_pedidos} | "
            f"disponible={self.disponible})"
        )


def generar_repartidor_id() -> str:
    return str(uuid4())
