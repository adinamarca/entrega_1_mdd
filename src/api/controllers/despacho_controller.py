"""Controller HTTP para el caso de uso: Asignacion y Despacho."""

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_despacho_service
from src.api.middleware.auth import require_roles
from src.api.schemas.despacho_schema import (
    AsignacionResponse,
    AsignarPedidoRequest,
)
from src.application.despacho_service import DespachoService
from src.domain.despacho.asignacion import Asignacion
from src.domain.despacho.estrategias import (
    AsignacionPorCapacidad,
    AsignacionPorProximidad,
    AsignacionRoundRobin,
    EstrategiaAsignacion,
)
from src.infrastructure.auth.roles import Rol


router = APIRouter(prefix="/pedidos", tags=["despacho"])


_ESTRATEGIAS: dict[str, type[EstrategiaAsignacion]] = {
    "proximidad": AsignacionPorProximidad,
    "capacidad": AsignacionPorCapacidad,
    "round_robin": AsignacionRoundRobin,
}


def _to_response(asignacion: Asignacion, estrategia: str) -> AsignacionResponse:
    return AsignacionResponse(
        asignacion_id=asignacion.asignacion_id,
        pedido_id=asignacion.pedido_id,
        repartidor_id=asignacion.repartidor_id,
        estrategia_usada=estrategia,
        activa=asignacion.activa,
    )


@router.post(
    "/{pedido_id}/asignar",
    response_model=AsignacionResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(Rol.OPERADOR))],
)
def asignar_pedido(
    pedido_id: str,
    body: AsignarPedidoRequest | None = None,
    service: DespachoService = Depends(get_despacho_service),
) -> AsignacionResponse:
    """Asigna un pedido a un repartidor via Facade + Strategy del E1.

    Si se especifica una estrategia distinta a la default, la cambia
    en runtime antes de asignar.
    """
    estrategia_nombre = body.estrategia if body and body.estrategia else None

    if estrategia_nombre:
        clase = _ESTRATEGIAS.get(estrategia_nombre)
        if not clase:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=(
                    f"Estrategia '{estrategia_nombre}' no soportada. "
                    f"Validas: {list(_ESTRATEGIAS.keys())}"
                ),
            )
        service.cambiar_estrategia(clase())

    asignacion = service.asignar_pedido(pedido_id)
    return _to_response(
        asignacion, estrategia_nombre or service._estrategia.nombre().lower()
    )


@router.post(
    "/{pedido_id}/reasignar",
    response_model=AsignacionResponse,
    dependencies=[Depends(require_roles(Rol.OPERADOR))],
)
def reasignar_pedido(
    pedido_id: str,
    service: DespachoService = Depends(get_despacho_service),
) -> AsignacionResponse:
    """Reasigna un pedido a otro repartidor liberando al anterior."""
    asignacion = service.reasignar_pedido(pedido_id)
    return _to_response(asignacion, service._estrategia.nombre().lower())
