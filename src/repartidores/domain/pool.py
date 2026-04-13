"""Singleton pattern: pool centralizado de repartidores.

Garantiza un unico punto de acceso global para consultar
y gestionar la disponibilidad de la flota de repartidores.
"""

from __future__ import annotations

from src.repartidores.domain.repartidor import Repartidor


class DriverPool:
    """Singleton que administra el pool global de repartidores disponibles."""

    _instance: DriverPool | None = None

    def __new__(cls) -> DriverPool:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._repartidores = {}
        return cls._instance

    def registrar(self, repartidor: Repartidor) -> None:
        self._repartidores[repartidor.repartidor_id] = repartidor

    def obtener(self, repartidor_id: str) -> Repartidor | None:
        return self._repartidores.get(repartidor_id)

    def listar_disponibles(self) -> list[Repartidor]:
        return [r for r in self._repartidores.values() if r.puede_recibir_pedido]

    def listar_todos(self) -> list[Repartidor]:
        return list(self._repartidores.values())

    @classmethod
    def reset(cls) -> None:
        """Reinicia la instancia singleton (util para testing y demo)."""
        cls._instance = None
