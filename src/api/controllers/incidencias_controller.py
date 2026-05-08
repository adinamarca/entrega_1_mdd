"""Controller HTTP para el caso de uso: Gestion de Incidencias."""

from fastapi import APIRouter, Depends, status

from src.api.dependencies import get_incidencia_service
from src.api.middleware.auth import require_roles
from src.api.schemas.incidencia_schema import (
    CrearIncidenciaRequest,
    IncidenciaResponse,
    ResolverIncidenciaRequest,
)
from src.application.incidencia_service import IncidenciaService
from src.domain.incidencias.incidencia import Incidencia
from src.domain.incidencias.value_objects import TipoIncidencia
from src.infrastructure.auth.roles import Rol


router = APIRouter(prefix="/incidencias", tags=["incidencias"])


def _to_response(incidencia: Incidencia) -> IncidenciaResponse:
    return IncidenciaResponse(
        incidencia_id=incidencia.incidencia_id,
        pedido_id=incidencia.pedido_id,
        tipo=incidencia.tipo.value,
        descripcion=incidencia.descripcion,
        estado=incidencia.estado_nombre,
        resolucion=(
            incidencia.resolucion.descripcion if incidencia.resolucion else None
        ),
    )


@router.post(
    "",
    response_model=IncidenciaResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_roles(Rol.OPERADOR, Rol.REPARTIDOR))],
)
def registrar_incidencia(
    body: CrearIncidenciaRequest,
    service: IncidenciaService = Depends(get_incidencia_service),
) -> IncidenciaResponse:
    """Registra una incidencia asociada a un pedido."""
    incidencia = service.registrar_incidencia(
        pedido_id=body.pedido_id,
        tipo=TipoIncidencia(body.tipo),
        descripcion=body.descripcion,
    )
    return _to_response(incidencia)


@router.post(
    "/{incidencia_id}/analizar",
    response_model=IncidenciaResponse,
    dependencies=[Depends(require_roles(Rol.OPERADOR, Rol.ADMIN))],
)
def iniciar_analisis(
    incidencia_id: str,
    service: IncidenciaService = Depends(get_incidencia_service),
) -> IncidenciaResponse:
    """Avanza la incidencia al estado 'En analisis'."""
    service.iniciar_analisis(incidencia_id)
    return _to_response(service.obtener_incidencia(incidencia_id))


@router.post(
    "/{incidencia_id}/resolver-iniciar",
    response_model=IncidenciaResponse,
    dependencies=[Depends(require_roles(Rol.OPERADOR, Rol.ADMIN))],
)
def iniciar_resolucion(
    incidencia_id: str,
    service: IncidenciaService = Depends(get_incidencia_service),
) -> IncidenciaResponse:
    """Avanza la incidencia al estado 'En resolucion'."""
    service.iniciar_resolucion(incidencia_id)
    return _to_response(service.obtener_incidencia(incidencia_id))


@router.put(
    "/{incidencia_id}/resolver",
    response_model=IncidenciaResponse,
    dependencies=[Depends(require_roles(Rol.OPERADOR, Rol.ADMIN))],
)
def resolver_incidencia(
    incidencia_id: str,
    body: ResolverIncidenciaRequest,
    service: IncidenciaService = Depends(get_incidencia_service),
) -> IncidenciaResponse:
    """Cierra la incidencia asignando una resolucion (obligatoria por regla de negocio)."""
    service.resolver(
        incidencia_id=incidencia_id,
        descripcion_resolucion=body.descripcion_resolucion,
        accion_tomada=body.accion_tomada,
        requiere_reenvio=body.requiere_reenvio,
    )
    return _to_response(service.obtener_incidencia(incidencia_id))
