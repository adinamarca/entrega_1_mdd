"""Controller HTTP para el caso de uso: Gestion de Pedidos.

Capa de presentacion (MVC adaptado a REST):
- Recibe requests HTTP, los traduce a llamadas al Service Layer
- Mapea respuestas del dominio a JSON
"""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_pedido_service
from src.api.middleware.auth import require_roles
from src.api.schemas.pedido_schema import (
    CambioEstadoRequest,
    CrearPedidoRequest,
    PedidoResponse,
    ValidacionResponse,
)
from src.application.pedido_service import PedidoService
from src.domain.pedidos.pedido import Pedido
from src.infrastructure.auth.roles import Rol


router = APIRouter(prefix="/pedidos", tags=["pedidos"])


def _to_response(pedido: Pedido) -> PedidoResponse:
    """Mapea entidad de dominio -> DTO HTTP."""
    return PedidoResponse(
        pedido_id=pedido.pedido_id,
        canal=pedido.canal.value,
        estado=pedido.estado_nombre,
        tipo_entrega=pedido.tipo_entrega.value,
        tipo_carga=pedido.tipo_carga.value,
        peso_kg=pedido.peso_estimado_kg,
        direccion_destino=str(pedido.direccion_destino),
        destinatario=pedido.destinatario.nombre,
        repartidor_id=pedido.repartidor_id,
    )


@router.post(
    "",
    response_model=PedidoResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(Rol.OPERADOR, Rol.INTEGRACION))],
)
def crear_pedido(
    body: CrearPedidoRequest,
    service: PedidoService = Depends(get_pedido_service),
) -> PedidoResponse:
    """Crea un pedido usando la fabrica del canal correspondiente (Factory + Builder)."""
    pedido = service.crear_pedido(body.canal, body.to_factory_data())
    return _to_response(pedido)


@router.get(
    "/{pedido_id}",
    response_model=PedidoResponse,
    dependencies=[
        Depends(
            require_roles(Rol.OPERADOR, Rol.REPARTIDOR, Rol.ADMIN, Rol.INTEGRACION)
        )
    ],
)
def consultar_pedido(
    pedido_id: str,
    service: PedidoService = Depends(get_pedido_service),
) -> PedidoResponse:
    """Consulta el estado de un pedido por ID."""
    pedido = service.obtener_pedido(pedido_id)
    if not pedido:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Pedido no encontrado: {pedido_id}",
        )
    return _to_response(pedido)


@router.post(
    "/{pedido_id}/validar",
    response_model=ValidacionResponse,
    dependencies=[Depends(require_roles(Rol.OPERADOR))],
)
def validar_pedido(
    pedido_id: str,
    service: PedidoService = Depends(get_pedido_service),
) -> ValidacionResponse:
    """Valida un pedido aplicando los decoradores de validacion del E1.

    Si pasa, transiciona el estado a Validado.
    """
    errores = service.validar_pedido(pedido_id)
    pedido = service.obtener_pedido(pedido_id)
    return ValidacionResponse(
        pedido_id=pedido_id,
        valido=not errores,
        errores=errores,
        estado=pedido.estado_nombre,
    )


@router.put(
    "/{pedido_id}/estado",
    response_model=PedidoResponse,
    dependencies=[Depends(require_roles(Rol.OPERADOR, Rol.REPARTIDOR))],
)
def cambiar_estado_pedido(
    pedido_id: str,
    body: CambioEstadoRequest,
    service: PedidoService = Depends(get_pedido_service),
) -> PedidoResponse:
    """Cambia el estado del pedido via State pattern del E1.

    Las acciones permitidas dependen del estado actual; transiciones
    invalidas devuelven HTTP 409 (gestionado por error_handler global).
    """
    acciones = {
        "poner_pendiente": service.poner_pendiente,
        "iniciar_ruta": service.iniciar_ruta,
        "intento_fallido": service.registrar_intento_fallido,
        "reprogramar": service.reprogramar,
        "entregar": service.entregar,
        "cancelar": service.cancelar,
    }

    accion = acciones.get(body.accion)
    if not accion:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"Accion '{body.accion}' no soportada. Validas: "
                f"{list(acciones.keys())}"
            ),
        )

    accion(pedido_id)
    pedido = service.obtener_pedido(pedido_id)
    return _to_response(pedido)
