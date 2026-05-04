from enum import Enum


class TipoEntrega(Enum):
    """Clasificacion del tipo de entrega solicitado."""

    NORMAL = "normal"
    EXPRESS = "express"
    PROGRAMADA = "programada"


class TipoCarga(Enum):
    """Clasificacion del contenido del paquete."""

    ESTANDAR = "estandar"
    FRAGIL = "fragil"
    VOLUMINOSO = "voluminoso"


class CanalOrigen(Enum):
    """Canal por el cual se origina un pedido."""

    WEB = "web"
    APP_MOVIL = "app_movil"
    ECOMMERCE = "ecommerce"
    PARTNER = "partner"
