from fastapi import Request, Response
from fastapi.security import HTTPBearer

from app.domain.excepciones import PermisoDenegado
from app.infrastructure.config import configuracion

esquema_bearer = HTTPBearer(auto_error=False)
NOMBRE_COOKIE_REFRESH = "galeria_refresh_token"


def establecer_cookie_refresh(response: Response, refresh_token: str) -> None:
    response.set_cookie(
        key=NOMBRE_COOKIE_REFRESH,
        value=refresh_token,
        httponly=True,
        secure=configuracion.cookie_secure,
        samesite="lax",
        max_age=configuracion.refresh_token_expire_days * 24 * 60 * 60,
        path="/api/v1/auth",
    )


def limpiar_cookie_refresh(response: Response) -> None:
    response.delete_cookie(
        key=NOMBRE_COOKIE_REFRESH,
        httponly=True,
        secure=configuracion.cookie_secure,
        samesite="lax",
        path="/api/v1/auth",
    )


def extraer_refresh_token(request: Request, token_body: str | None = None) -> str | None:
    if token_body:
        return token_body
    cookie = request.cookies.get(NOMBRE_COOKIE_REFRESH)
    if cookie and request.headers.get("X-CSRF-Protection") != "1":
        raise PermisoDenegado("Se requiere X-CSRF-Protection para usar la cookie de sesion")
    return cookie
