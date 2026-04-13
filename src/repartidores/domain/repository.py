from abc import ABC, abstractmethod

from src.repartidores.domain.repartidor import Repartidor


class RepartidorRepository(ABC):

    @abstractmethod
    def guardar(self, repartidor: Repartidor) -> None: ...

    @abstractmethod
    def obtener_por_id(self, repartidor_id: str) -> Repartidor | None: ...

    @abstractmethod
    def listar_disponibles(self) -> list[Repartidor]: ...

    @abstractmethod
    def listar_todos(self) -> list[Repartidor]: ...
