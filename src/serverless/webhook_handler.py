"""Handler 'serverless' simulado para webhooks de canales externos.

En produccion: AWS Lambda con HTTP trigger, recibe POST de e-commerce/partners
y publica eventos al EventBus interno.
"""

from src.domain.pedidos.eventos import PedidoCreado


def notificar_canal_externo_pedido_creado(evento: PedidoCreado) -> None:
    """Simula el envio de un webhook de confirmacion al canal externo
    cuando se crea un pedido desde ese canal.
    """
    if evento.canal in {"ecommerce", "partner"}:
        print(
            f"  [serverless::webhook] Pedido {evento.pedido_id[:8]} desde "
            f"'{evento.canal}' (enviando confirmacion via webhook)"
        )
