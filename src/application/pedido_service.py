"""Servicio de aplicacion para el caso de uso: Gestion de Pedidos.

SRP: orquesta la logica de negocio sin implementarla directamente.
DIP: depende de abstracciones (PedidoRepository, ValidadorPedido, EventBus).
"""

from src.domain.pedidos.eventos import PedidoCambioEstado, PedidoCreado
from src.domain.pedidos.factory import obtener_factory
from src.domain.pedidos.pedido import Pedido
from src.domain.pedidos.repository import PedidoRepository
from src.domain.pedidos.validador import ValidadorPedido, crear_validador_completo
from src.domain.shared.domain_event import EventBus


class PedidoService:

    def __init__(
        self,
        repository: PedidoRepository,
        event_bus: EventBus,
        validador: ValidadorPedido | None = None,
    ) -> None:
        self._repository = repository
        self._event_bus = event_bus
        self._validador = validador or crear_validador_completo()

    def crear_pedido(self, canal: str, datos: dict) -> Pedido:
        """Crea un pedido usando la fabrica correspondiente al canal."""
        factory = obtener_factory(canal)
        pedido = factory.crear_pedido(datos)
        self._repository.guardar(pedido)
        self._event_bus.publish(
            PedidoCreado(pedido_id=pedido.pedido_id, canal=canal)
        )
        return pedido

    def validar_pedido(self, pedido_id: str) -> list[str]:
        """Valida un pedido y, si pasa, lo transiciona a estado Validado."""
        pedido = self._obtener_pedido(pedido_id)

        errores = self._validador.validar(pedido)
        if errores:
            return errores

        estado_anterior = pedido.estado_nombre
        pedido.validar()
        self._repository.guardar(pedido)
        self._event_bus.publish(
            PedidoCambioEstado(
                pedido_id=pedido_id,
                estado_anterior=estado_anterior,
                estado_nuevo=pedido.estado_nombre,
            )
        )
        return []

    def poner_pendiente(self, pedido_id: str) -> None:
        """Marca un pedido validado como pendiente de asignacion."""
        pedido = self._obtener_pedido(pedido_id)
        estado_anterior = pedido.estado_nombre
        pedido.poner_pendiente()
        self._repository.guardar(pedido)
        self._publicar_cambio_estado(pedido_id, estado_anterior, pedido.estado_nombre)

    def iniciar_ruta(self, pedido_id: str) -> None:
        pedido = self._obtener_pedido(pedido_id)
        estado_anterior = pedido.estado_nombre
        pedido.iniciar_ruta()
        self._repository.guardar(pedido)
        self._publicar_cambio_estado(pedido_id, estado_anterior, pedido.estado_nombre)

    def registrar_intento_fallido(self, pedido_id: str) -> None:
        pedido = self._obtener_pedido(pedido_id)
        estado_anterior = pedido.estado_nombre
        pedido.registrar_intento_fallido()
        self._repository.guardar(pedido)
        self._publicar_cambio_estado(pedido_id, estado_anterior, pedido.estado_nombre)

    def reprogramar(self, pedido_id: str) -> None:
        pedido = self._obtener_pedido(pedido_id)
        estado_anterior = pedido.estado_nombre
        pedido.reprogramar()
        self._repository.guardar(pedido)
        self._publicar_cambio_estado(pedido_id, estado_anterior, pedido.estado_nombre)

    def entregar(self, pedido_id: str) -> None:
        pedido = self._obtener_pedido(pedido_id)
        estado_anterior = pedido.estado_nombre
        pedido.entregar()
        self._repository.guardar(pedido)
        self._publicar_cambio_estado(pedido_id, estado_anterior, pedido.estado_nombre)

    def cancelar(self, pedido_id: str) -> None:
        pedido = self._obtener_pedido(pedido_id)
        estado_anterior = pedido.estado_nombre
        pedido.cancelar()
        self._repository.guardar(pedido)
        self._publicar_cambio_estado(pedido_id, estado_anterior, pedido.estado_nombre)

    def obtener_pedido(self, pedido_id: str) -> Pedido | None:
        return self._repository.obtener_por_id(pedido_id)

    def listar_pedidos(self) -> list[Pedido]:
        return self._repository.listar_todos()

    # --- Metodos internos ---

    def _obtener_pedido(self, pedido_id: str) -> Pedido:
        pedido = self._repository.obtener_por_id(pedido_id)
        if not pedido:
            raise ValueError(f"Pedido no encontrado: {pedido_id}")
        return pedido

    def _publicar_cambio_estado(
        self, pedido_id: str, anterior: str, nuevo: str
    ) -> None:
        self._event_bus.publish(
            PedidoCambioEstado(
                pedido_id=pedido_id,
                estado_anterior=anterior,
                estado_nuevo=nuevo,
            )
        )
