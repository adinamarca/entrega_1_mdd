from src.domain.repartidores.repartidor import Repartidor
from src.domain.repartidores.repository import RepartidorRepository


class InMemoryRepartidorRepository(RepartidorRepository):

    def __init__(self) -> None:
        self._repartidores: dict[str, Repartidor] = {}

    def guardar(self, repartidor: Repartidor) -> None:
        self._repartidores[repartidor.repartidor_id] = repartidor

    def obtener_por_id(self, repartidor_id: str) -> Repartidor | None:
        return self._repartidores.get(repartidor_id)

    def listar_disponibles(self) -> list[Repartidor]:
        return [r for r in self._repartidores.values() if r.puede_recibir_pedido]

    def listar_todos(self) -> list[Repartidor]:
        return list(self._repartidores.values())
