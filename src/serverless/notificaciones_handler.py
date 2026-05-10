"""Handler 'serverless' simulado para notificaciones a clientes.

En produccion seria una funcion AWS Lambda / GCP Cloud Function suscrita
a una cola (SQS / PubSub) que recibe eventos del EventBus.

Aqui lo simulamos como un handler en proceso conectado al EventBus local.
"""

from src.domain.pedidos.eventos import PedidoCambioEstado


def notificar_cliente_cambio_estado(evento: PedidoCambioEstado) -> None:
    """Simula el envio de una notificacion al cliente.

    Estados que disparan notificacion al cliente final:
    - En ruta: "tu pedido salio a entrega"
    - Entregado: "tu pedido fue entregado"
    - Intento fallido: "intentamos entregar pero no estabas"
    """
    estados_notificables = {"En ruta", "Entregado", "Intento fallido"}
    if evento.estado_nuevo in estados_notificables:
        print(
            f"  [serverless::notificaciones] Pedido {evento.pedido_id[:8]} -> "
            f"'{evento.estado_nuevo}' (notificando al cliente)"
        )
