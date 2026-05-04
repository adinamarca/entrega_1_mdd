from src.domain.pedidos.pedido import Pedido
from src.domain.pedidos.repository import PedidoRepository


class InMemoryPedidoRepository(PedidoRepository):
    """Implementacion en memoria del repositorio de pedidos.

    Cumple con DIP: es la implementacion concreta de la abstraccion PedidoRepository.
    """

    def __init__(self) -> None:
        self._pedidos: dict[str, Pedido] = {}

    def guardar(self, pedido: Pedido) -> None:
        self._pedidos[pedido.pedido_id] = pedido

    def obtener_por_id(self, pedido_id: str) -> Pedido | None:
        return self._pedidos.get(pedido_id)

    def listar_todos(self) -> list[Pedido]:
        return list(self._pedidos.values())
