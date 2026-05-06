"""Controller para autenticacion (login)."""

from fastapi import APIRouter, HTTPException, status

from src.api.schemas.auth_schema import LoginRequest, TokenResponse
from src.infrastructure.auth.jwt_provider import generar_token
from src.infrastructure.auth.roles import USUARIOS_DEMO


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest) -> TokenResponse:
    """Autentica y devuelve un JWT.

    Usuarios demo:
    - operador1 / op123
    - repartidor1 / rep123
    - admin1 / admin123
    - integracion1 / int123
    """
    usuario = USUARIOS_DEMO.get(body.username)
    if not usuario or usuario["password"] != body.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales invalidas",
        )

    token, ttl = generar_token(body.username, usuario["rol"])
    return TokenResponse(
        access_token=token, role=usuario["rol"].value, expires_in=ttl
    )
