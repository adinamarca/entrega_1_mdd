"""Factory de la app FastAPI.

Esta es la capa de presentacion del servicio web. Compone:
- Routers (controllers) por caso de uso
- Middleware de error_handler global
- Suscripcion de handlers serverless al EventBus
"""

from fastapi import FastAPI

from src.api.controllers import (
    auth_controller,
    despacho_controller,
    incidencias_controller,
    pedidos_controller,
    repartidores_controller,
)
from src.api.dependencies import get_container
from src.api.middleware.error_handler import register_exception_handlers
from src.domain.pedidos.eventos import PedidoCambioEstado, PedidoCreado
from src.serverless import (
    notificar_canal_externo_pedido_creado,
    notificar_cliente_cambio_estado,
)


def create_app() -> FastAPI:
    """Construye la app FastAPI lista para servir."""
    app = FastAPI(
        title="Logistica Ultima Milla - Servicio Web",
        description=(
            "Servicio HTTP para gestion de pedidos, repartidores, "
            "despacho e incidencias. Implementa los 4 casos de uso del "
            "Entregable 1 bajo arquitectura cliente-servidor + layered."
        ),
        version="1.0.0",
    )

    # Capa de presentacion: registro de routers
    app.include_router(auth_controller.router)
    app.include_router(pedidos_controller.router)
    app.include_router(repartidores_controller.router)
    app.include_router(despacho_controller.router)
    app.include_router(incidencias_controller.router)

    # Middleware: traduce errores de dominio a HTTP codes
    register_exception_handlers(app)

    # Wire de handlers serverless al EventBus (Observer pattern)
    container = get_container()
    container.event_bus.subscribe(
        PedidoCambioEstado, notificar_cliente_cambio_estado
    )
    container.event_bus.subscribe(
        PedidoCreado, notificar_canal_externo_pedido_creado
    )

    @app.get("/health", tags=["health"])
    def health() -> dict:
        return {"status": "ok"}

    return app
