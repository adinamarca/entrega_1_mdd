"""Capa serverless (componentes event-driven).

Aqui viven las funciones que en produccion correrian como FaaS:
- notificaciones_handler: reacciona a cambios de estado del pedido
- webhook_handler: reacciona a pedidos creados desde canales externos
- reportes_handler: genera reportes batch periodicos

Se suscriben al EventBus en bootstrap (ver `wire_handlers` en api/app.py).
"""

from src.serverless.notificaciones_handler import notificar_cliente_cambio_estado
from src.serverless.reportes_handler import generar_reporte_diario
from src.serverless.webhook_handler import notificar_canal_externo_pedido_creado

__all__ = [
    "notificar_cliente_cambio_estado",
    "notificar_canal_externo_pedido_creado",
    "generar_reporte_diario",
]
