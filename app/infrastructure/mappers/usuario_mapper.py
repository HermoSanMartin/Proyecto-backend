from app.domain.usuario import RolUsuario, Usuario
from app.infrastructure.models.usuario_orm import UsuarioORM


def orm_a_dominio(orm: UsuarioORM) -> Usuario:
    return Usuario(
        id=orm.id,
        nombre=orm.nombre,
        email=orm.email,
        password_hash=orm.password_hash,
        rol=RolUsuario(orm.rol),
        activo=orm.activo,
        intentos_fallidos=orm.intentos_fallidos,
        bloqueado_hasta=orm.bloqueado_hasta,
        token_version=orm.token_version,
    )


def dominio_a_orm(usuario: Usuario) -> UsuarioORM:
    return UsuarioORM(
        id=usuario.id,
        nombre=usuario.nombre,
        email=usuario.email,
        password_hash=usuario.password_hash,
        rol=usuario.rol.value,
        activo=usuario.activo,
        intentos_fallidos=usuario.intentos_fallidos,
        bloqueado_hasta=usuario.bloqueado_hasta,
        token_version=usuario.token_version,
    )
