"""Servicio de aplicacion para el caso de uso: Gestion de Incidencias.

SRP: orquesta creacion, avance y resolucion de incidencias.
DIP: depende de abstracciones (IncidenciaRepository, PedidoRepository, EventBus).
"""

from src.domain.incidencias.incidencia import Incidencia, generar_incidencia_id
from src.domain.incidencias.repository import IncidenciaRepository
from src.domain.incidencias.value_objects import Resolucion, TipoIncidencia
from src.domain.pedidos.repository import PedidoRepository
from src.domain.shared.domain_event import EventBus


class IncidenciaService:

    def __init__(
        self,
        incidencia_repo: IncidenciaRepository,
        pedido_repo: PedidoRepository,
        event_bus: EventBus,
    ) -> None:
        self._incidencia_repo = incidencia_repo
        self._pedido_repo = pedido_repo
        self._event_bus = event_bus

    def registrar_incidencia(
        self,
        pedido_id: str,
        tipo: TipoIncidencia,
        descripcion: str,
    ) -> Incidencia:
        """Registra una incidencia asociada a un pedido."""
        pedido = self._pedido_repo.obtener_por_id(pedido_id)
        if not pedido:
            raise ValueError(f"Pedido no encontrado: {pedido_id}")

        incidencia = Incidencia(
            incidencia_id=generar_incidencia_id(),
            pedido_id=pedido_id,
            tipo=tipo,
            descripcion=descripcion,
        )
        self._incidencia_repo.guardar(incidencia)
        return incidencia

    def iniciar_analisis(self, incidencia_id: str) -> None:
        incidencia = self._obtener_incidencia(incidencia_id)
        incidencia.iniciar_analisis()
        self._incidencia_repo.guardar(incidencia)

    def iniciar_resolucion(self, incidencia_id: str) -> None:
        incidencia = self._obtener_incidencia(incidencia_id)
        incidencia.iniciar_resolucion()
        self._incidencia_repo.guardar(incidencia)

    def resolver(
        self,
        incidencia_id: str,
        descripcion_resolucion: str,
        accion_tomada: str,
        requiere_reenvio: bool = False,
    ) -> None:
        """Asigna resolucion y cierra la incidencia."""
        incidencia = self._obtener_incidencia(incidencia_id)

        resolucion = Resolucion(
            descripcion=descripcion_resolucion,
            accion_tomada=accion_tomada,
            requiere_reenvio=requiere_reenvio,
        )
        incidencia.asignar_resolucion(resolucion)
        incidencia.resolver()
        self._incidencia_repo.guardar(incidencia)

    def intentar_resolver_sin_resolucion(self, incidencia_id: str) -> None:
        """Intenta cerrar una incidencia sin resolucion (debe fallar)."""
        incidencia = self._obtener_incidencia(incidencia_id)
        incidencia.resolver()

    def listar_por_pedido(self, pedido_id: str) -> list[Incidencia]:
        return self._incidencia_repo.listar_por_pedido(pedido_id)

    def obtener_incidencia(self, incidencia_id: str) -> Incidencia | None:
        return self._incidencia_repo.obtener_por_id(incidencia_id)

    def _obtener_incidencia(self, incidencia_id: str) -> Incidencia:
        incidencia = self._incidencia_repo.obtener_por_id(incidencia_id)
        if not incidencia:
            raise ValueError(f"Incidencia no encontrada: {incidencia_id}")
        return incidencia
