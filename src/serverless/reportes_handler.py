"""Handler 'serverless' simulado para generacion de reportes batch.

En produccion: AWS Lambda con cron trigger (EventBridge) o GCP Cloud Scheduler.
Ejecucion periodica, sin estado, agrega informacion del dia.

Aqui exponemos una funcion que el handler-cron puede invocar.
"""

from src.domain.pedidos.pedido import Pedido


def generar_reporte_diario(pedidos: list[Pedido]) -> dict:
    """Genera un reporte agregado con metricas del dia.

    Diseno: stateless, idempotente, dura segundos. Ideal para serverless.
    """
    total = len(pedidos)
    por_estado: dict[str, int] = {}
    por_canal: dict[str, int] = {}

    for pedido in pedidos:
        estado = pedido.estado_nombre
        canal = pedido.canal.value
        por_estado[estado] = por_estado.get(estado, 0) + 1
        por_canal[canal] = por_canal.get(canal, 0) + 1

    return {
        "total_pedidos": total,
        "por_estado": por_estado,
        "por_canal": por_canal,
    }
