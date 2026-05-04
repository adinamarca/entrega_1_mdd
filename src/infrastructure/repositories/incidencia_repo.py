from src.domain.incidencias.incidencia import Incidencia
from src.domain.incidencias.repository import IncidenciaRepository


class InMemoryIncidenciaRepository(IncidenciaRepository):

    def __init__(self) -> None:
        self._incidencias: dict[str, Incidencia] = {}

    def guardar(self, incidencia: Incidencia) -> None:
        self._incidencias[incidencia.incidencia_id] = incidencia

    def obtener_por_id(self, incidencia_id: str) -> Incidencia | None:
        return self._incidencias.get(incidencia_id)

    def listar_por_pedido(self, pedido_id: str) -> list[Incidencia]:
        return [i for i in self._incidencias.values() if i.pedido_id == pedido_id]

    def listar_todas(self) -> list[Incidencia]:
        return list(self._incidencias.values())
