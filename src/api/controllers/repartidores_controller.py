"""Controller HTTP para el caso de uso: Gestion de Repartidores."""

from fastapi import APIRouter, Depends, status

from src.api.dependencies import get_repartidor_service
from src.api.middleware.auth import require_roles
from src.api.schemas.repartidor_schema import (
    CambioDisponibilidadRequest,
    CrearRepartidorRequest,
    RepartidorResponse,
)
from src.application.repartidor_service import RepartidorService
from src.domain.repartidores.repartidor import Repartidor
from src.infrastructure.auth.roles import Rol


router = APIRouter(prefix="/repartidores", tags=["repartidores"])


def _to_response(repartidor: Repartidor) -> RepartidorResponse:
    return RepartidorResponse(
        repartidor_id=repartidor.repartidor_id,
        nombre=repartidor.nombre,
        capacidad_max=repartidor.capacidad.max_pedidos,
        pedidos_actuales=repartidor.pedidos_actuales,
        disponible=repartidor.disponible,
        latitud=repartidor.ubicacion.latitud,
        longitud=repartidor.ubicacion.longitud,
    )


@router.post(
    "",
    response_model=RepartidorResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(Rol.ADMIN))],
)
def registrar_repartidor(
    body: CrearRepartidorRequest,
    service: RepartidorService = Depends(get_repartidor_service),
) -> RepartidorResponse:
    """Registra un nuevo repartidor en la flota."""
    repartidor = service.registrar_repartidor(
        nombre=body.nombre,
        max_pedidos=body.max_pedidos,
        max_peso_kg=body.max_peso_kg,
        latitud=body.latitud,
        longitud=body.longitud,
    )
    return _to_response(repartidor)


@router.get(
    "/disponibles",
    response_model=list[RepartidorResponse],
    dependencies=[Depends(require_roles(Rol.OPERADOR, Rol.ADMIN))],
)
def listar_disponibles(
    service: RepartidorService = Depends(get_repartidor_service),
) -> list[RepartidorResponse]:
    """Lista repartidores disponibles via el DriverPool (Singleton del E1)."""
    return [_to_response(r) for r in service.consultar_disponibles()]


@router.put(
    "/{repartidor_id}/disponibilidad",
    response_model=RepartidorResponse,
    dependencies=[Depends(require_roles(Rol.REPARTIDOR, Rol.ADMIN))],
)
def cambiar_disponibilidad(
    repartidor_id: str,
    body: CambioDisponibilidadRequest,
    service: RepartidorService = Depends(get_repartidor_service),
) -> RepartidorResponse:
    """Marca al repartidor como disponible o no disponible."""
    service.cambiar_disponibilidad(repartidor_id, body.disponible)
    repartidor = service.obtener_repartidor(repartidor_id)
    return _to_response(repartidor)
