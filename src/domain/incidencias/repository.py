from abc import ABC, abstractmethod

from src.domain.incidencias.incidencia import Incidencia


class IncidenciaRepository(ABC):

    @abstractmethod
    def guardar(self, incidencia: Incidencia) -> None: ...

    @abstractmethod
    def obtener_por_id(self, incidencia_id: str) -> Incidencia | None: ...

    @abstractmethod
    def listar_por_pedido(self, pedido_id: str) -> list[Incidencia]: ...

    @abstractmethod
    def listar_todas(self) -> list[Incidencia]: ...
