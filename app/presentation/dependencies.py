from collections.abc import Generator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from app.application.services.artista_service import ArtistaService
from app.application.services.auth_service import AuthService
from app.application.services.exposicion_service import ExposicionService
from app.application.services.obra_service import ObraService
from app.application.services.solicitud_service import SolicitudService
from app.domain.excepciones import NoAutenticado, PermisoDenegado
from app.domain.usuario import RolUsuario, Usuario
from app.infrastructure.database import SessionLocal
from app.infrastructure.repositories.artista_repository import ArtistaRepository
from app.infrastructure.repositories.exposicion_repository import ExposicionRepository
from app.infrastructure.repositories.obra_repository import ObraRepository
from app.infrastructure.repositories.solicitud_repository import SolicitudRepository
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.security.email_sender import ServicioCorreoSMTP
from app.presentation.security.transporte_http import esquema_bearer


def obtener_sesion() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def obtener_servicio_correo() -> ServicioCorreoSMTP:
    return ServicioCorreoSMTP()


def obtener_servicio_auth(
    db: Session = Depends(obtener_sesion),
    servicio_correo: ServicioCorreoSMTP = Depends(obtener_servicio_correo),
) -> AuthService:
    return AuthService(UsuarioRepository(db), servicio_correo)


def obtener_usuario_actual(
    credenciales: HTTPAuthorizationCredentials | None = Depends(esquema_bearer),
    servicio_auth: AuthService = Depends(obtener_servicio_auth),
) -> Usuario:
    if credenciales is None or credenciales.scheme.lower() != "bearer":
        raise NoAutenticado("Se requiere un token de acceso Bearer")
    return servicio_auth.obtener_usuario_desde_access_token(credenciales.credentials)


def exigir_admin(usuario: Usuario = Depends(obtener_usuario_actual)) -> Usuario:
    if usuario.rol != RolUsuario.ADMIN:
        raise PermisoDenegado("No tienes permisos suficientes para realizar esta operacion")
    return usuario


def obtener_servicio_artista(db: Session = Depends(obtener_sesion)) -> ArtistaService:
    return ArtistaService(ArtistaRepository(db))


def obtener_servicio_obra(db: Session = Depends(obtener_sesion)) -> ObraService:
    return ObraService(ObraRepository(db), ArtistaRepository(db))


def obtener_servicio_exposicion(db: Session = Depends(obtener_sesion)) -> ExposicionService:
    return ExposicionService(ExposicionRepository(db))


def obtener_servicio_solicitud(db: Session = Depends(obtener_sesion)) -> SolicitudService:
    return SolicitudService(SolicitudRepository(db), ObraRepository(db), ExposicionRepository(db))
