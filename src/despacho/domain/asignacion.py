from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4


@dataclass
class Asignacion:
    """Entidad que representa el vinculo entre un pedido y un repartidor."""

    asignacion_id: str
    pedido_id: str
    repartidor_id: str
    fecha_asignacion: datetime = field(default_factory=datetime.now)
    activa: bool = True

    def desactivar(self) -> None:
        self.activa = False

    def __str__(self) -> str:
        estado = "activa" if self.activa else "inactiva"
        return (
            f"Asignacion({self.pedido_id[:8]}... -> "
            f"{self.repartidor_id[:8]}... | {estado})"
        )


def generar_asignacion_id() -> str:
    return str(uuid4())
