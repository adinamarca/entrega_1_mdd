"""Builder pattern: construccion paso a paso de objetos Pedido complejos."""

from src.domain.pedidos.pedido import Pedido, generar_pedido_id
from src.domain.pedidos.value_objects import CanalOrigen, TipoCarga, TipoEntrega
from src.domain.shared.value_objects import ContactInfo, Direccion


class PedidoBuilder:
    """Permite construir un Pedido paso a paso, validando la completitud
    antes de crear el objeto final.

    Justificacion: el Pedido tiene multiples campos obligatorios y condicionales
    (ventana de tiempo solo aplica para entrega programada). Builder hace que
    la construccion sea legible y controlada.
    """

    def __init__(self) -> None:
        self._pedido_id: str = generar_pedido_id()
        self._canal: CanalOrigen | None = None
        self._direccion_origen: Direccion | None = None
        self._punto_origen_id: str | None = None
        self._direccion_destino: Direccion | None = None
        self._destinatario: ContactInfo | None = None
        self._tipo_entrega: TipoEntrega | None = None
        self._tipo_carga: TipoCarga | None = None
        self._peso_estimado_kg: float | None = None
        self._ventana_tiempo: str | None = None

    def con_canal(self, canal: CanalOrigen) -> "PedidoBuilder":
        self._canal = canal
        return self

    def con_origen(self, direccion: Direccion, punto_id: str) -> "PedidoBuilder":
        self._direccion_origen = direccion
        self._punto_origen_id = punto_id
        return self

    def con_destino(
        self, direccion: Direccion, destinatario: ContactInfo
    ) -> "PedidoBuilder":
        self._direccion_destino = direccion
        self._destinatario = destinatario
        return self

    def con_entrega(
        self, tipo: TipoEntrega, ventana: str | None = None
    ) -> "PedidoBuilder":
        self._tipo_entrega = tipo
        self._ventana_tiempo = ventana
        return self

    def con_carga(self, tipo: TipoCarga, peso_kg: float) -> "PedidoBuilder":
        self._tipo_carga = tipo
        self._peso_estimado_kg = peso_kg
        return self

    def build(self) -> Pedido:
        self._validar_campos_requeridos()
        return Pedido(
            pedido_id=self._pedido_id,
            canal=self._canal,
            direccion_origen=self._direccion_origen,
            punto_origen_id=self._punto_origen_id,
            direccion_destino=self._direccion_destino,
            destinatario=self._destinatario,
            tipo_entrega=self._tipo_entrega,
            tipo_carga=self._tipo_carga,
            peso_estimado_kg=self._peso_estimado_kg,
            ventana_tiempo=self._ventana_tiempo,
        )

    def _validar_campos_requeridos(self) -> None:
        campos_faltantes = []
        if not self._canal:
            campos_faltantes.append("canal")
        if not self._direccion_origen:
            campos_faltantes.append("direccion_origen")
        if not self._punto_origen_id:
            campos_faltantes.append("punto_origen_id")
        if not self._direccion_destino:
            campos_faltantes.append("direccion_destino")
        if not self._destinatario:
            campos_faltantes.append("destinatario")
        if not self._tipo_entrega:
            campos_faltantes.append("tipo_entrega")
        if not self._tipo_carga:
            campos_faltantes.append("tipo_carga")
        if self._peso_estimado_kg is None:
            campos_faltantes.append("peso_estimado_kg")

        if campos_faltantes:
            raise ValueError(
                f"No se puede construir el Pedido. Campos faltantes: {campos_faltantes}"
            )

        if (
            self._tipo_entrega == TipoEntrega.PROGRAMADA
            and not self._ventana_tiempo
        ):
            raise ValueError(
                "Entrega programada requiere una ventana de tiempo"
            )
