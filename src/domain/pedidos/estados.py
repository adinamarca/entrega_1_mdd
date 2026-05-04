"""State pattern: cada estado del pedido encapsula su comportamiento y transiciones validas."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.domain.pedidos.pedido import Pedido


class EstadoPedido(ABC):
    """Interfaz base para el State pattern del ciclo de vida del pedido."""

    @abstractmethod
    def nombre(self) -> str: ...

    def validar(self, pedido: Pedido) -> None:
        raise TransicionInvalidaError(self.nombre(), "Validado")

    def poner_pendiente(self, pedido: Pedido) -> None:
        raise TransicionInvalidaError(self.nombre(), "Pendiente de asignacion")

    def asignar(self, pedido: Pedido) -> None:
        raise TransicionInvalidaError(self.nombre(), "Asignado")

    def iniciar_ruta(self, pedido: Pedido) -> None:
        raise TransicionInvalidaError(self.nombre(), "En ruta")

    def registrar_intento_fallido(self, pedido: Pedido) -> None:
        raise TransicionInvalidaError(self.nombre(), "Intento fallido")

    def reprogramar(self, pedido: Pedido) -> None:
        raise TransicionInvalidaError(self.nombre(), "Reprogramado")

    def entregar(self, pedido: Pedido) -> None:
        raise TransicionInvalidaError(self.nombre(), "Entregado")

    def cancelar(self, pedido: Pedido) -> None:
        raise TransicionInvalidaError(self.nombre(), "Cancelado")

    def __str__(self) -> str:
        return self.nombre()


class TransicionInvalidaError(Exception):
    def __init__(self, estado_actual: str, estado_destino: str) -> None:
        super().__init__(
            f"Transicion invalida: no se puede pasar de '{estado_actual}' a '{estado_destino}'"
        )


# --- Implementaciones concretas de cada estado ---


class Creado(EstadoPedido):
    def nombre(self) -> str:
        return "Creado"

    def validar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Validado())

    def cancelar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Cancelado())


class Validado(EstadoPedido):
    def nombre(self) -> str:
        return "Validado"

    def poner_pendiente(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(PendienteAsignacion())

    def cancelar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Cancelado())


class PendienteAsignacion(EstadoPedido):
    def nombre(self) -> str:
        return "Pendiente de asignacion"

    def asignar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Asignado())

    def cancelar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Cancelado())


class Asignado(EstadoPedido):
    def nombre(self) -> str:
        return "Asignado"

    def iniciar_ruta(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(EnRuta())

    def poner_pendiente(self, pedido: Pedido) -> None:
        # Reasignacion: vuelve a pendiente
        pedido.cambiar_estado(PendienteAsignacion())

    def cancelar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Cancelado())


class EnRuta(EstadoPedido):
    def nombre(self) -> str:
        return "En ruta"

    def entregar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Entregado())

    def registrar_intento_fallido(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(IntentoFallido())

    def cancelar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Cancelado())


class IntentoFallido(EstadoPedido):
    def nombre(self) -> str:
        return "Intento fallido"

    def reprogramar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Reprogramado())

    def cancelar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Cancelado())


class Reprogramado(EstadoPedido):
    def nombre(self) -> str:
        return "Reprogramado"

    def asignar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Asignado())

    def cancelar(self, pedido: Pedido) -> None:
        pedido.cambiar_estado(Cancelado())


class Entregado(EstadoPedido):
    """Estado final. No permite transiciones a estados anteriores."""

    def nombre(self) -> str:
        return "Entregado"


class Cancelado(EstadoPedido):
    """Estado final. No permite ninguna transicion."""

    def nombre(self) -> str:
        return "Cancelado"
