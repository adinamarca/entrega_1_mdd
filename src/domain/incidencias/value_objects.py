from dataclasses import dataclass
from enum import Enum


class TipoIncidencia(Enum):
    """Clasificacion del tipo de incidencia reportada."""

    PRODUCTO_NO_RECIBIDO = "producto_no_recibido"
    PRODUCTO_DANADO = "producto_danado"
    ENTREGA_INCORRECTA = "entrega_incorrecta"
    RETRASO = "retraso"
    OTRO = "otro"


@dataclass(frozen=True)
class Resolucion:
    """Value Object que representa la resolucion de una incidencia."""

    descripcion: str
    accion_tomada: str
    requiere_reenvio: bool = False
