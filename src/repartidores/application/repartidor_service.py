"""Servicio de aplicacion para el caso de uso: Gestion de Repartidores.

SRP: solo orquesta operaciones sobre repartidores.
DIP: depende de RepartidorRepository (abstraccion) y DriverPool.
"""

from src.repartidores.domain.pool import DriverPool
from src.repartidores.domain.repartidor import Repartidor, generar_repartidor_id
from src.repartidores.domain.repository import RepartidorRepository
from src.repartidores.domain.value_objects import Capacidad, Ubicacion


class RepartidorService:

    def __init__(self, repository: RepartidorRepository) -> None:
        self._repository = repository
        self._pool = DriverPool()

    def registrar_repartidor(
        self,
        nombre: str,
        max_pedidos: int,
        max_peso_kg: float,
        latitud: float,
        longitud: float,
    ) -> Repartidor:
        repartidor = Repartidor(
            repartidor_id=generar_repartidor_id(),
            nombre=nombre,
            capacidad=Capacidad(max_pedidos=max_pedidos, max_peso_kg=max_peso_kg),
            ubicacion=Ubicacion(latitud=latitud, longitud=longitud),
        )
        self._repository.guardar(repartidor)
        self._pool.registrar(repartidor)
        return repartidor

    def cambiar_disponibilidad(self, repartidor_id: str, disponible: bool) -> None:
        repartidor = self._obtener_repartidor(repartidor_id)
        if disponible:
            repartidor.marcar_disponible()
        else:
            repartidor.marcar_no_disponible()
        self._repository.guardar(repartidor)

    def actualizar_ubicacion(
        self, repartidor_id: str, latitud: float, longitud: float
    ) -> None:
        repartidor = self._obtener_repartidor(repartidor_id)
        repartidor.actualizar_ubicacion(Ubicacion(latitud, longitud))
        self._repository.guardar(repartidor)

    def consultar_disponibles(self) -> list[Repartidor]:
        return self._pool.listar_disponibles()

    def obtener_repartidor(self, repartidor_id: str) -> Repartidor | None:
        return self._repository.obtener_por_id(repartidor_id)

    def listar_todos(self) -> list[Repartidor]:
        return self._repository.listar_todos()

    def _obtener_repartidor(self, repartidor_id: str) -> Repartidor:
        repartidor = self._repository.obtener_por_id(repartidor_id)
        if not repartidor:
            raise ValueError(f"Repartidor no encontrado: {repartidor_id}")
        return repartidor
