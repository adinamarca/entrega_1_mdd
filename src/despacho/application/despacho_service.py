"""Facade pattern: servicio que orquesta el proceso completo de asignacion.

Simplifica la interaccion con los subsistemas de Pedidos, Repartidores y Asignacion.
El cliente solo llama a un metodo; la fachada coordina todas las operaciones internas.

DIP: depende de abstracciones (repositories, estrategia).
SRP: solo orquesta la asignacion, no implementa logica de dominio.
"""

from src.despacho.domain.asignacion import Asignacion, generar_asignacion_id
from src.despacho.domain.estrategias import EstrategiaAsignacion
from src.despacho.domain.eventos import PedidoAsignado, PedidoReasignado
from src.pedidos.domain.pedido import Pedido
from src.pedidos.domain.repository import PedidoRepository
from src.repartidores.domain.pool import DriverPool
from src.repartidores.domain.value_objects import Ubicacion
from src.shared.domain_event import EventBus


class DespachoService:
    """Facade que orquesta: buscar repartidor, validar capacidad, asignar, notificar."""

    def __init__(
        self,
        pedido_repository: PedidoRepository,
        estrategia: EstrategiaAsignacion,
        event_bus: EventBus,
    ) -> None:
        self._pedido_repo = pedido_repository
        self._estrategia = estrategia
        self._event_bus = event_bus
        self._pool = DriverPool()
        self._asignaciones: dict[str, Asignacion] = {}

    def cambiar_estrategia(self, nueva_estrategia: EstrategiaAsignacion) -> None:
        """OCP: permite cambiar la estrategia en tiempo de ejecucion."""
        self._estrategia = nueva_estrategia

    def asignar_pedido(self, pedido_id: str) -> Asignacion:
        """Proceso completo de asignacion (Facade):
        1. Obtiene el pedido y verifica que este pendiente de asignacion
        2. Busca repartidores disponibles en el pool
        3. Aplica la estrategia de seleccion
        4. Asigna el pedido al repartidor seleccionado
        5. Publica evento de dominio
        """
        pedido = self._obtener_pedido(pedido_id)

        if pedido.estado_nombre != "Pendiente de asignacion":
            raise ValueError(
                f"El pedido debe estar 'Pendiente de asignacion' para ser asignado. "
                f"Estado actual: '{pedido.estado_nombre}'"
            )

        disponibles = self._pool.listar_disponibles()
        if not disponibles:
            raise ValueError("No hay repartidores disponibles")

        ubicacion_destino = Ubicacion(
            latitud=hash(pedido.direccion_destino.ciudad) % 90,
            longitud=hash(pedido.direccion_destino.comuna) % 180,
        )

        repartidor = self._estrategia.seleccionar(disponibles, ubicacion_destino)
        if not repartidor:
            raise ValueError("La estrategia no pudo seleccionar un repartidor")

        repartidor.asignar_pedido(pedido_id)
        pedido.asignar(repartidor.repartidor_id)
        self._pedido_repo.guardar(pedido)

        asignacion = Asignacion(
            asignacion_id=generar_asignacion_id(),
            pedido_id=pedido_id,
            repartidor_id=repartidor.repartidor_id,
        )
        self._asignaciones[pedido_id] = asignacion

        self._event_bus.publish(
            PedidoAsignado(
                pedido_id=pedido_id,
                repartidor_id=repartidor.repartidor_id,
                estrategia=self._estrategia.nombre(),
            )
        )

        return asignacion

    def reasignar_pedido(self, pedido_id: str) -> Asignacion:
        """Reasigna un pedido a otro repartidor, liberando el anterior."""
        pedido = self._obtener_pedido(pedido_id)

        if pedido.estado_nombre != "Asignado":
            raise ValueError(
                f"Solo se pueden reasignar pedidos en estado 'Asignado'. "
                f"Estado actual: '{pedido.estado_nombre}'"
            )

        asignacion_anterior = self._asignaciones.get(pedido_id)
        repartidor_anterior_id = pedido.repartidor_id

        # Liberar al repartidor anterior
        if repartidor_anterior_id:
            repartidor_anterior = self._pool.obtener(repartidor_anterior_id)
            if repartidor_anterior:
                repartidor_anterior.liberar_pedido(pedido_id)

        if asignacion_anterior:
            asignacion_anterior.desactivar()

        # Volver a pendiente y reasignar
        pedido.poner_pendiente()
        self._pedido_repo.guardar(pedido)

        nueva_asignacion = self.asignar_pedido(pedido_id)

        self._event_bus.publish(
            PedidoReasignado(
                pedido_id=pedido_id,
                repartidor_anterior_id=repartidor_anterior_id or "",
                repartidor_nuevo_id=nueva_asignacion.repartidor_id,
            )
        )

        return nueva_asignacion

    def obtener_asignacion(self, pedido_id: str) -> Asignacion | None:
        return self._asignaciones.get(pedido_id)

    def _obtener_pedido(self, pedido_id: str) -> Pedido:
        pedido = self._pedido_repo.obtener_por_id(pedido_id)
        if not pedido:
            raise ValueError(f"Pedido no encontrado: {pedido_id}")
        return pedido
