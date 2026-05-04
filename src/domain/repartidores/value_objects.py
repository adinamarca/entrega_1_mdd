from dataclasses import dataclass


@dataclass(frozen=True)
class Ubicacion:
    """Value Object que representa la ubicacion geografica de un repartidor."""

    latitud: float
    longitud: float

    def distancia_a(self, otra: "Ubicacion") -> float:
        """Calculo simplificado de distancia euclidiana (simulacion)."""
        return ((self.latitud - otra.latitud) ** 2 + (self.longitud - otra.longitud) ** 2) ** 0.5


@dataclass(frozen=True)
class Capacidad:
    """Value Object que representa la capacidad de carga de un repartidor."""

    max_pedidos: int
    max_peso_kg: float
