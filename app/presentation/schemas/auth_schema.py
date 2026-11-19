from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domain.usuario import RolUsuario


class UsuarioRegistroEntrada(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(..., min_length=12, max_length=128)


class UsuarioLoginEntrada(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class UsuarioRespuesta(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    email: EmailStr
    rol: RolUsuario
    activo: bool


class TokenRespuesta(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    usuario: UsuarioRespuesta


class RefreshEntrada(BaseModel):
    refresh_token: str | None = None


class SolicitudRecuperacionEntrada(BaseModel):
    email: EmailStr


class RestablecerPasswordEntrada(BaseModel):
    token: str = Field(..., min_length=10)
    nueva_password: str = Field(..., min_length=12, max_length=128)


class MensajeOperacionRespuesta(BaseModel):
    mensaje: str
