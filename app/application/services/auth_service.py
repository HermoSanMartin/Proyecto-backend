import uuid
from datetime import UTC, datetime, timedelta
from typing import Any

from app.domain.excepciones import (
    ConflictoDeEstado,
    CuentaBloqueada,
    NoAutenticado,
)
from app.domain.usuario import RolUsuario, Usuario, validar_politica_password
from app.infrastructure.config import configuracion
from app.infrastructure.repositories.usuario_repository import UsuarioRepository
from app.infrastructure.security.jwt_manager import (
    crear_access_token,
    crear_recovery_token,
    generar_token_opaco,
    hashear_token_opaco,
    verificar_access_token,
    verificar_recovery_token,
)
from app.infrastructure.security.password_hasher import (
    hashear_password,
    verificar_password,
)


def _asegurar_utc(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt


class AuthService:
    MAX_INTENTOS_FALLIDOS = 5
    MINUTOS_BLOQUEO = 15

    def __init__(self, repo_usuario: UsuarioRepository, servicio_correo: Any) -> None:
        self.repo_usuario = repo_usuario
        self.servicio_correo = servicio_correo

    def registrar(self, nombre: str, email: str, password: str) -> Usuario:
        email_normalizado = email.lower().strip()
        if self.repo_usuario.obtener_por_email(email_normalizado) is not None:
            raise ConflictoDeEstado("Ya existe una cuenta registrada con ese correo")

        validar_politica_password(password)
        password_hash = hashear_password(password)

        nuevo_usuario = Usuario(
            nombre=nombre.strip(),
            email=email_normalizado,
            password_hash=password_hash,
            rol=RolUsuario.USUARIO,
            activo=True,
        )
        return self.repo_usuario.crear(nuevo_usuario)

    def iniciar_sesion(self, email: str, password: str) -> tuple[Usuario, str, str]:
        email_normalizado = email.lower().strip()
        usuario = self.repo_usuario.obtener_por_email(email_normalizado)
        if usuario is None or not usuario.activo:
            raise NoAutenticado("Credenciales invalidas")

        ahora = datetime.now(UTC)
        if usuario.bloqueado_hasta is not None:
            bloqueado_hasta = _asegurar_utc(usuario.bloqueado_hasta)
            if bloqueado_hasta > ahora:
                raise CuentaBloqueada(
                    "Cuenta bloqueada temporalmente por multiples intentos fallidos"
                )

        if not verificar_password(password, usuario.password_hash):
            usuario.intentos_fallidos += 1
            if usuario.intentos_fallidos >= self.MAX_INTENTOS_FALLIDOS:
                usuario.bloqueado_hasta = ahora + timedelta(minutes=self.MINUTOS_BLOQUEO)
            self.repo_usuario.actualizar(usuario)
            raise NoAutenticado("Credenciales invalidas")

        usuario.intentos_fallidos = 0
        usuario.bloqueado_hasta = None
        usuario = self.repo_usuario.actualizar(usuario) or usuario

        assert usuario.id is not None
        access_token = crear_access_token(
            usuario_id=usuario.id,
            rol=usuario.rol.value,
            token_version=usuario.token_version,
        )
        refresh_plano, refresh_hash = generar_token_opaco()
        familia_id = str(uuid.uuid4())
        expira_refresh = ahora + timedelta(days=configuracion.refresh_token_expire_days)

        self.repo_usuario.guardar_refresh_token(
            usuario_id=usuario.id,
            token_hash=refresh_hash,
            familia_id=familia_id,
            expira_en=expira_refresh,
        )
        return usuario, access_token, refresh_plano

    def renovar_tokens(self, refresh_token: str) -> tuple[str, str]:
        token_hash = hashear_token_opaco(refresh_token)
        registro = self.repo_usuario.obtener_refresh_por_hash(token_hash)
        if registro is None:
            raise NoAutenticado("Token de renovacion invalido")

        if registro.revocado:
            self.repo_usuario.revocar_familia_refresh(registro.familia_id)
            raise NoAutenticado("Reutilizacion de token detectada; sesion revocada")

        ahora = datetime.now(UTC)
        if _asegurar_utc(registro.expira_en) <= ahora:
            self.repo_usuario.revocar_refresh_token(token_hash)
            raise NoAutenticado("Token de renovacion expirado")

        usuario = self.repo_usuario.obtener_por_id(registro.usuario_id)
        if usuario is None or not usuario.activo or usuario.id is None:
            raise NoAutenticado("Usuario inactivo o inexistente")

        nuevo_plano, nuevo_hash = generar_token_opaco()
        nueva_expiracion = ahora + timedelta(days=configuracion.refresh_token_expire_days)
        self.repo_usuario.rotar_refresh_token(registro, nuevo_hash, nueva_expiracion)

        nuevo_access = crear_access_token(
            usuario_id=usuario.id,
            rol=usuario.rol.value,
            token_version=usuario.token_version,
        )
        return nuevo_access, nuevo_plano

    def cerrar_sesion(self, refresh_token: str) -> None:
        token_hash = hashear_token_opaco(refresh_token)
        registro = self.repo_usuario.obtener_refresh_por_hash(token_hash)
        if registro is not None:
            self.repo_usuario.revocar_familia_refresh(registro.familia_id)

    def obtener_usuario_desde_access_token(self, token: str) -> Usuario:
        payload = verificar_access_token(token)
        usuario_id = int(payload["sub"])
        token_version = int(payload["ver"])

        usuario = self.repo_usuario.obtener_por_id(usuario_id)
        if usuario is None or not usuario.activo:
            raise NoAutenticado("Usuario no valido o inactivo")

        if usuario.token_version != token_version:
            raise NoAutenticado("La sesion ha sido invalidada")

        return usuario

    def solicitar_recuperacion(self, email: str) -> str | None:
        email_normalizado = email.lower().strip()
        usuario = self.repo_usuario.obtener_por_email(email_normalizado)
        if usuario is None or not usuario.activo or usuario.id is None:
            return None

        jti = str(uuid.uuid4())
        token_recuperacion, expira_en = crear_recovery_token(
            usuario_id=usuario.id,
            jti=jti,
        )
        self.repo_usuario.guardar_token_recuperacion(
            usuario_id=usuario.id,
            jti=jti,
            expira_en=expira_en,
        )
        enlace = f"{configuracion.url_recuperacion_base}?token={token_recuperacion}"
        self.servicio_correo.enviar_recuperacion(usuario.email, enlace)
        return token_recuperacion

    def restablecer_password(self, token: str, nueva_password: str) -> None:
        payload = verificar_recovery_token(token)
        usuario_id = int(payload["sub"])
        jti = str(payload["jti"])

        registro = self.repo_usuario.obtener_token_recuperacion_por_jti(jti)
        if registro is None or registro.usuario_id != usuario_id:
            raise NoAutenticado("Token de recuperacion invalido")

        if registro.usado:
            raise NoAutenticado("El enlace de recuperacion ya fue utilizado")

        ahora = datetime.now(UTC)
        if _asegurar_utc(registro.expira_en) <= ahora:
            raise NoAutenticado("El enlace de recuperacion ha expirado")

        validar_politica_password(nueva_password)
        nuevo_hash = hashear_password(nueva_password)
        self.repo_usuario.consumir_recuperacion_y_cambiar_password(
            usuario_id=usuario_id,
            jti=jti,
            nuevo_password_hash=nuevo_hash,
        )
