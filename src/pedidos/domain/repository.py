"""DIP: interfaz abstracta del repositorio de pedidos.

Los servicios de aplicacion dependen de esta abstraccion,
no de la implementacion concreta (InMemoryPedidoRepository).
"""

from abc import ABC, abstractmethod

from src.pedidos.domain.pedido import Pedido


class PedidoRepository(ABC):

    @abstractmethod
    def guardar(self, pedido: Pedido) -> None: ...

    @abstractmethod
    def obtener_por_id(self, pedido_id: str) -> Pedido | None: ...

    @abstractmethod
    def listar_todos(self) -> list[Pedido]: ...
