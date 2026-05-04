from src.domain.despacho.asignacion import Asignacion


class InMemoryAsignacionRepository:

    def __init__(self) -> None:
        self._asignaciones: dict[str, Asignacion] = {}

    def guardar(self, asignacion: Asignacion) -> None:
        self._asignaciones[asignacion.asignacion_id] = asignacion

    def obtener_por_pedido(self, pedido_id: str) -> Asignacion | None:
        for a in self._asignaciones.values():
            if a.pedido_id == pedido_id and a.activa:
                return a
        return None

    def listar_activas(self) -> list[Asignacion]:
        return [a for a in self._asignaciones.values() if a.activa]
