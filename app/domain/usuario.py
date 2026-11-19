from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from app.domain.excepciones import ReglaDeNegocioViolada


class RolUsuario(str, Enum):
    ADMIN = "admin"
    USUARIO = "usuario"


def validar_politica_password(password: str) -> None:
    errores: list[dict[str, str]] = []
    if len(password) < 12:
        errores.append({"campo": "password", "mensaje": "Debe tener al menos 12 caracteres"})
    if not any(c.isupper() for c in password):
        errores.append({"campo": "password", "mensaje": "Debe incluir al menos una mayuscula"})
    if not any(c.islower() for c in password):
        errores.append({"campo": "password", "mensaje": "Debe incluir al menos una minuscula"})
    if not any(c.isdigit() for c in password):
        errores.append({"campo": "password", "mensaje": "Debe incluir al menos un numero"})
    if errores:
        raise ReglaDeNegocioViolada("La contrasena no cumple la politica de seguridad", errores)


@dataclass
class Usuario:
    nombre: str
    email: str
    password_hash: str
    rol: RolUsuario = RolUsuario.USUARIO
    activo: bool = True
    intentos_fallidos: int = 0
    bloqueado_hasta: datetime | None = None
    token_version: int = 1
    id: int | None = None
