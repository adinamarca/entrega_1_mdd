"""Decorator pattern: validaciones apilables sobre pedidos.

Permite agregar capas de validacion sin modificar la clase base.
Cada decorador verifica un aspecto distinto del pedido.
"""

from abc import ABC, abstractmethod

from src.domain.pedidos.pedido import Pedido
from src.domain.pedidos.value_objects import TipoEntrega


class ValidadorPedido(ABC):
    """Interfaz base para el Decorator pattern de validaciones.

    ISP: interfaz minima con un solo metodo.
    """

    @abstractmethod
    def validar(self, pedido: Pedido) -> list[str]:
        """Retorna lista de errores. Lista vacia significa pedido valido."""
        ...


class ValidadorBase(ValidadorPedido):
    """Validacion base: verifica informacion minima requerida por las reglas de negocio."""

    def validar(self, pedido: Pedido) -> list[str]:
        errores = []

        if not pedido.direccion_origen.es_valida():
            errores.append("Direccion de origen invalida")
        if not pedido.punto_origen_id:
            errores.append("Falta identificacion del punto de origen")
        if not pedido.direccion_destino.es_valida():
            errores.append("Direccion de destino invalida")
        if not pedido.destinatario.nombre:
            errores.append("Falta nombre del destinatario")
        if not pedido.destinatario.tiene_medio_contacto():
            errores.append("Falta medio de contacto del destinatario")
        if pedido.peso_estimado_kg <= 0:
            errores.append("Peso estimado debe ser mayor a 0")

        return errores


class ValidadorDecorator(ValidadorPedido, ABC):
    """Clase base para decoradores de validacion."""

    def __init__(self, validador_interno: ValidadorPedido) -> None:
        self._validador_interno = validador_interno

    def validar(self, pedido: Pedido) -> list[str]:
        return self._validador_interno.validar(pedido)


class ValidadorExpress(ValidadorDecorator):
    """Decorador: agrega validaciones especificas para entregas express."""

    def validar(self, pedido: Pedido) -> list[str]:
        errores = super().validar(pedido)

        if pedido.tipo_entrega == TipoEntrega.EXPRESS:
            if pedido.peso_estimado_kg > 20:
                errores.append(
                    "Entrega express no disponible para paquetes mayores a 20 kg"
                )

        return errores


class ValidadorProgramada(ValidadorDecorator):
    """Decorador: agrega validaciones especificas para entregas programadas."""

    def validar(self, pedido: Pedido) -> list[str]:
        errores = super().validar(pedido)

        if pedido.tipo_entrega == TipoEntrega.PROGRAMADA:
            if not pedido.ventana_tiempo:
                errores.append(
                    "Entrega programada requiere ventana de tiempo"
                )

        return errores


class ValidadorZona(ValidadorDecorator):
    """Decorador: verifica que la zona de destino sea atendida."""

    ZONAS_ATENDIDAS = {"Santiago", "Valparaiso", "Vina del Mar", "Concepcion"}

    def validar(self, pedido: Pedido) -> list[str]:
        errores = super().validar(pedido)

        if pedido.direccion_destino.ciudad not in self.ZONAS_ATENDIDAS:
            errores.append(
                f"La ciudad '{pedido.direccion_destino.ciudad}' "
                f"no esta dentro de las zonas atendidas"
            )

        return errores


def crear_validador_completo() -> ValidadorPedido:
    """Construye la cadena de validadores con todos los decoradores apilados."""
    validador = ValidadorBase()
    validador = ValidadorExpress(validador)
    validador = ValidadorProgramada(validador)
    validador = ValidadorZona(validador)
    return validador
