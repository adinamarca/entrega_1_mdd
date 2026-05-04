from dataclasses import dataclass


@dataclass(frozen=True)
class Direccion:
    """Value Object que representa una direccion fisica."""

    calle: str
    numero: str
    ciudad: str
    comuna: str

    def es_valida(self) -> bool:
        return all([self.calle, self.numero, self.ciudad, self.comuna])

    def __str__(self) -> str:
        return f"{self.calle} {self.numero}, {self.comuna}, {self.ciudad}"


@dataclass(frozen=True)
class ContactInfo:
    """Value Object que representa informacion de contacto del destinatario."""

    nombre: str
    telefono: str | None = None
    email: str | None = None

    def tiene_medio_contacto(self) -> bool:
        return bool(self.telefono or self.email)
