"""Middleware/dependencies de autenticacion y autorizacion.

Implementa control de acceso basado en roles (RBAC):
- require_auth: extrae el usuario actual del JWT
- require_roles(roles): verifica que el usuario tenga al menos uno de los roles
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from src.infrastructure.auth.jwt_provider import TokenInvalidError, validar_token
from src.infrastructure.auth.roles import Rol


bearer_scheme = HTTPBearer(auto_error=False)


class CurrentUser:
    """Usuario autenticado extraido del token."""

    def __init__(self, username: str, rol: Rol) -> None:
        self.username = username
        self.rol = rol

    def __repr__(self) -> str:
        return f"CurrentUser(username={self.username}, rol={self.rol.value})"


def require_auth(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> CurrentUser:
    """Dependency: verifica que el request tenga un JWT valido."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header faltante",
        )
    try:
        payload = validar_token(credentials.credentials)
    except TokenInvalidError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)
        ) from exc

    return CurrentUser(username=payload["sub"], rol=Rol(payload["rol"]))


def require_roles(*roles_permitidos: Rol):
    """Dependency factory: verifica que el usuario tenga uno de los roles."""

    def _checker(usuario: CurrentUser = Depends(require_auth)) -> CurrentUser:
        if usuario.rol not in roles_permitidos:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Rol '{usuario.rol.value}' no autorizado. "
                    f"Requiere uno de: {[r.value for r in roles_permitidos]}"
                ),
            )
        return usuario

    return _checker
