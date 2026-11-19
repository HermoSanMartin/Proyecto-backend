from datetime import UTC, datetime, timedelta
import hashlib
import secrets
from typing import Any

import jwt
from jwt import InvalidTokenError

from app.domain.excepciones import NoAutenticado
from app.infrastructure.config import configuracion


def crear_access_token(usuario_id: int, rol: str, token_version: int) -> str:
    ahora = datetime.now(UTC)
    expira = ahora + timedelta(minutes=configuracion.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": str(usuario_id),
        "rol": rol,
        "ver": token_version,
        "type": "access",
        "iat": int(ahora.timestamp()),
        "exp": int(expira.timestamp()),
    }
    return jwt.encode(payload, configuracion.jwt_secret_key, algorithm=configuracion.jwt_algorithm)


def verificar_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            configuracion.jwt_secret_key,
            algorithms=[configuracion.jwt_algorithm],
            options={"require": ["sub", "exp", "type", "ver"]},
        )
    except InvalidTokenError as exc:
        raise NoAutenticado("Token de acceso invalido o expirado") from exc

    if payload.get("type") != "access":
        raise NoAutenticado("Tipo de token invalido para autenticacion")
    return payload


def crear_recovery_token(usuario_id: int, jti: str) -> tuple[str, datetime]:
    ahora = datetime.now(UTC)
    expira = ahora + timedelta(minutes=configuracion.recovery_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": str(usuario_id),
        "jti": jti,
        "type": "recovery",
        "iat": int(ahora.timestamp()),
        "exp": int(expira.timestamp()),
    }
    token = jwt.encode(payload, configuracion.jwt_secret_key, algorithm=configuracion.jwt_algorithm)
    return token, expira


def verificar_recovery_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            configuracion.jwt_secret_key,
            algorithms=[configuracion.jwt_algorithm],
            options={"require": ["sub", "exp", "type", "jti"]},
        )
    except InvalidTokenError as exc:
        raise NoAutenticado("Token de recuperacion invalido o expirado") from exc

    if payload.get("type") != "recovery":
        raise NoAutenticado("El token proporcionado no corresponde a recuperacion")
    return payload


def generar_token_opaco() -> tuple[str, str]:
    token_plano = secrets.token_urlsafe(48)
    token_hash = hashear_token_opaco(token_plano)
    return token_plano, token_hash


def hashear_token_opaco(token_plano: str) -> str:
    return hashlib.sha256(token_plano.encode("utf-8")).hexdigest()
