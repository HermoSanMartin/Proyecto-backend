from fastapi import APIRouter, Depends, Request, Response, status

from app.application.services.auth_service import AuthService
from app.domain.usuario import Usuario
from app.infrastructure.config import configuracion
from app.presentation.dependencies import obtener_servicio_auth, obtener_usuario_actual
from app.presentation.schemas.auth_schema import (
    MensajeOperacionRespuesta,
    RefreshEntrada,
    RestablecerPasswordEntrada,
    SolicitudRecuperacionEntrada,
    TokenRespuesta,
    UsuarioLoginEntrada,
    UsuarioRegistroEntrada,
    UsuarioRespuesta,
)
from app.presentation.schemas.respuesta import RespuestaError
from app.presentation.security.transporte_http import (
    establecer_cookie_refresh,
    extraer_refresh_token,
    limpiar_cookie_refresh,
)

router = APIRouter(prefix="/api/v1/auth", tags=["Autenticacion y Seguridad"])


@router.post(
    "/registro",
    response_model=UsuarioRespuesta,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar una nueva cuenta de usuario",
    responses={
        400: {
            "model": RespuestaError,
            "description": "Contrasena no cumple politica minima de 12 caracteres",
        },
        409: {"model": RespuestaError, "description": "Correo ya registrado"},
    },
)
def registrar_usuario(
    datos: UsuarioRegistroEntrada,
    servicio: AuthService = Depends(obtener_servicio_auth),
):
    usuario = servicio.registrar(datos.nombre, datos.email, datos.password)
    return UsuarioRespuesta.model_validate(usuario)


@router.post(
    "/login",
    response_model=TokenRespuesta,
    summary="Iniciar sesion y obtener tokens JWT",
    responses={
        401: {"model": RespuestaError, "description": "Credenciales invalidas"},
        429: {
            "model": RespuestaError,
            "description": "Cuenta bloqueada temporalmente por intentos fallidos",
        },
    },
)
def login(
    datos: UsuarioLoginEntrada,
    response: Response,
    servicio: AuthService = Depends(obtener_servicio_auth),
):
    usuario, access_token, refresh_token = servicio.iniciar_sesion(datos.email, datos.password)
    establecer_cookie_refresh(response, refresh_token)
    return TokenRespuesta(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in_minutes=configuracion.access_token_expire_minutes,
        usuario=UsuarioRespuesta.model_validate(usuario),
    )


@router.get(
    "/me",
    response_model=UsuarioRespuesta,
    summary="Consultar perfil del usuario autenticado",
    responses={401: {"model": RespuestaError, "description": "No autenticado o token invalido"}},
)
def obtener_perfil_actual(usuario: Usuario = Depends(obtener_usuario_actual)):
    return UsuarioRespuesta.model_validate(usuario)


@router.post(
    "/refresh",
    response_model=TokenRespuesta,
    summary="Rotar refresh token y emitir nuevo access token",
    responses={
        401: {
            "model": RespuestaError,
            "description": "Refresh token invalido, expirado o reutilizado",
        }
    },
)
def refrescar_sesion(
    request: Request,
    response: Response,
    datos: RefreshEntrada | None = None,
    servicio: AuthService = Depends(obtener_servicio_auth),
):
    token_body = datos.refresh_token if datos else None
    refresh_actual = extraer_refresh_token(request, token_body)
    nuevo_access, nuevo_refresh = servicio.renovar_tokens(refresh_actual)
    establecer_cookie_refresh(response, nuevo_refresh)
    usuario = servicio.obtener_usuario_desde_access_token(nuevo_access)
    return TokenRespuesta(
        access_token=nuevo_access,
        refresh_token=nuevo_refresh,
        expires_in_minutes=configuracion.access_token_expire_minutes,
        usuario=UsuarioRespuesta.model_validate(usuario),
    )


@router.post(
    "/logout",
    response_model=MensajeOperacionRespuesta,
    summary="Cerrar sesion y revocar refresh token",
)
def cerrar_sesion(
    request: Request,
    response: Response,
    datos: RefreshEntrada | None = None,
    servicio: AuthService = Depends(obtener_servicio_auth),
):
    token_body = datos.refresh_token if datos else None
    refresh_actual = extraer_refresh_token(request, token_body)
    servicio.cerrar_sesion(refresh_actual)
    limpiar_cookie_refresh(response)
    return MensajeOperacionRespuesta(mensaje="Sesion cerrada correctamente")


@router.post(
    "/solicitar-recuperacion",
    response_model=MensajeOperacionRespuesta,
    summary="Solicitar enlace de recuperacion de contrasena",
)
def solicitar_recuperacion(
    datos: SolicitudRecuperacionEntrada,
    servicio: AuthService = Depends(obtener_servicio_auth),
):
    servicio.solicitar_recuperacion(datos.email)
    return MensajeOperacionRespuesta(
        mensaje="Si el correo esta registrado, recibiras un enlace de recuperacion."
    )


@router.post(
    "/restablecer-password",
    response_model=MensajeOperacionRespuesta,
    summary="Restablecer contrasena usando JWT de recuperacion de un solo uso",
    responses={
        400: {
            "model": RespuestaError,
            "description": "Nueva contrasena no cumple politica de seguridad",
        },
        401: {
            "model": RespuestaError,
            "description": "Token de recuperacion invalido, expirado o ya utilizado",
        },
    },
)
def restablecer_password(
    datos: RestablecerPasswordEntrada,
    servicio: AuthService = Depends(obtener_servicio_auth),
):
    servicio.restablecer_password(datos.token, datos.nueva_password)
    return MensajeOperacionRespuesta(
        mensaje="Contrasena actualizada correctamente. Vuelve a iniciar sesion."
    )
