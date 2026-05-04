"""Factory Method pattern: cada canal de origen produce pedidos de forma distinta.

OCP: para agregar un nuevo canal, se crea una nueva subclase de PedidoFactory
sin modificar las fabricas existentes.
"""

from abc import ABC, abstractmethod

from src.domain.pedidos.builder import PedidoBuilder
from src.domain.pedidos.pedido import Pedido
from src.domain.pedidos.value_objects import CanalOrigen, TipoCarga, TipoEntrega
from src.domain.shared.value_objects import ContactInfo, Direccion


class PedidoFactory(ABC):
    """Interfaz del Factory Method para creacion de pedidos."""

    @abstractmethod
    def crear_pedido(self, datos: dict) -> Pedido:
        """Crea un pedido a partir de datos del canal correspondiente."""
        ...

    def _builder_base(self, datos: dict, canal: CanalOrigen) -> PedidoBuilder:
        """Construye un builder con los datos comunes a todos los canales."""
        return (
            PedidoBuilder()
            .con_canal(canal)
            .con_origen(
                Direccion(
                    calle=datos["origen_calle"],
                    numero=datos["origen_numero"],
                    ciudad=datos["origen_ciudad"],
                    comuna=datos["origen_comuna"],
                ),
                punto_id=datos["punto_origen_id"],
            )
            .con_destino(
                Direccion(
                    calle=datos["destino_calle"],
                    numero=datos["destino_numero"],
                    ciudad=datos["destino_ciudad"],
                    comuna=datos["destino_comuna"],
                ),
                ContactInfo(
                    nombre=datos["destinatario_nombre"],
                    telefono=datos.get("destinatario_telefono"),
                    email=datos.get("destinatario_email"),
                ),
            )
            .con_entrega(
                TipoEntrega(datos["tipo_entrega"]),
                ventana=datos.get("ventana_tiempo"),
            )
            .con_carga(
                TipoCarga(datos["tipo_carga"]),
                peso_kg=datos["peso_kg"],
            )
        )


class WebPedidoFactory(PedidoFactory):
    """Fabrica de pedidos originados desde la plataforma web."""

    def crear_pedido(self, datos: dict) -> Pedido:
        builder = self._builder_base(datos, CanalOrigen.WEB)
        return builder.build()


class AppMovilPedidoFactory(PedidoFactory):
    """Fabrica de pedidos originados desde la aplicacion movil."""

    def crear_pedido(self, datos: dict) -> Pedido:
        builder = self._builder_base(datos, CanalOrigen.APP_MOVIL)
        return builder.build()


class EcommercePedidoFactory(PedidoFactory):
    """Fabrica de pedidos originados desde plataformas e-commerce."""

    def crear_pedido(self, datos: dict) -> Pedido:
        builder = self._builder_base(datos, CanalOrigen.ECOMMERCE)
        return builder.build()


class PartnerPedidoFactory(PedidoFactory):
    """Fabrica de pedidos originados desde partners externos."""

    def crear_pedido(self, datos: dict) -> Pedido:
        builder = self._builder_base(datos, CanalOrigen.PARTNER)
        return builder.build()


def obtener_factory(canal: str) -> PedidoFactory:
    """Retorna la fabrica apropiada segun el canal de origen."""
    fabricas: dict[str, PedidoFactory] = {
        "web": WebPedidoFactory(),
        "app_movil": AppMovilPedidoFactory(),
        "ecommerce": EcommercePedidoFactory(),
        "partner": PartnerPedidoFactory(),
    }
    factory = fabricas.get(canal)
    if not factory:
        raise ValueError(f"Canal no soportado: {canal}")
    return factory
