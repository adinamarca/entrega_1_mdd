"""Roles del sistema y permisos asociados.

La pauta del Entregable 2 menciona 4 tipos de usuarios:
operadores, repartidores, administradores e integraciones externas.
"""

from enum import Enum


class Rol(str, Enum):
    OPERADOR = "operador"
    REPARTIDOR = "repartidor"
    ADMIN = "admin"
    INTEGRACION = "integracion"


# Usuarios demo (en produccion vendrian de una BD)
USUARIOS_DEMO = {
    "operador1": {"password": "op123", "rol": Rol.OPERADOR},
    "repartidor1": {"password": "rep123", "rol": Rol.REPARTIDOR},
    "admin1": {"password": "admin123", "rol": Rol.ADMIN},
    "integracion1": {"password": "int123", "rol": Rol.INTEGRACION},
}
