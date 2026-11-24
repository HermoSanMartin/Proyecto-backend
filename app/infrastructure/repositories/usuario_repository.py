from datetime import UTC, datetime, timedelta

from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from app.domain.usuario import Usuario
from app.infrastructure.mappers.usuario_mapper import dominio_a_orm, orm_a_dominio
from app.infrastructure.models.refresh_token_orm import RefreshTokenORM
from app.infrastructure.models.token_recuperacion_orm import TokenRecuperacionORM
from app.infrastructure.models.usuario_orm import UsuarioORM


class UsuarioRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, usuario: Usuario) -> Usuario:
        orm = dominio_a_orm(usuario)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return orm_a_dominio(orm)

    def obtener_por_id(self, usuario_id: int) -> Usuario | None:
        orm = self.db.get(UsuarioORM, usuario_id)
        return orm_a_dominio(orm) if orm else None

    def obtener_por_email(self, email: str) -> Usuario | None:
        orm = self.db.scalar(select(UsuarioORM).where(UsuarioORM.email == email.lower().strip()))
        return orm_a_dominio(orm) if orm else None

    def actualizar(self, usuario: Usuario) -> Usuario | None:
        orm = self.db.get(UsuarioORM, usuario.id)
        if orm is None:
            return None
        orm.nombre = usuario.nombre
        orm.email = usuario.email
        orm.password_hash = usuario.password_hash
        orm.rol = usuario.rol.value
        orm.activo = usuario.activo
        orm.intentos_fallidos = usuario.intentos_fallidos
        orm.bloqueado_hasta = usuario.bloqueado_hasta
        orm.token_version = usuario.token_version
        self.db.commit()
        self.db.refresh(orm)
        return orm_a_dominio(orm)

    # --- Gestion de Refresh Tokens ---
    def guardar_refresh_token(
        self,
        usuario_id: int,
        token_hash: str,
        familia_id: str,
        expira_en: datetime,
    ) -> RefreshTokenORM:
        registro = RefreshTokenORM(
            usuario_id=usuario_id,
            token_hash=token_hash,
            familia_id=familia_id,
            expira_en=expira_en,
            revocado=False,
            creado_en=datetime.now(UTC),
        )
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def obtener_refresh_por_hash(self, token_hash: str) -> RefreshTokenORM | None:
        return self.db.scalar(
            select(RefreshTokenORM).where(RefreshTokenORM.token_hash == token_hash)
        )

    def rotar_refresh_token(
        self,
        actual: RefreshTokenORM,
        nuevo_hash: str,
        nueva_expiracion: datetime,
    ) -> RefreshTokenORM:
        actual.revocado = True
        actual.reemplazado_por_hash = nuevo_hash
        nuevo = RefreshTokenORM(
            usuario_id=actual.usuario_id,
            token_hash=nuevo_hash,
            familia_id=actual.familia_id,
            expira_en=nueva_expiracion,
            revocado=False,
            creado_en=datetime.now(UTC),
        )
        self.db.add(nuevo)
        self.db.commit()
        self.db.refresh(nuevo)
        return nuevo

    def revocar_refresh_token(self, token_hash: str) -> None:
        self.db.execute(
            update(RefreshTokenORM)
            .where(RefreshTokenORM.token_hash == token_hash)
            .values(revocado=True)
        )
        self.db.commit()

    def revocar_familia_refresh(self, familia_id: str) -> None:
        self.db.execute(
            update(RefreshTokenORM)
            .where(RefreshTokenORM.familia_id == familia_id)
            .values(revocado=True)
        )
        self.db.commit()

    def revocar_todos_refresh_usuario(self, usuario_id: int) -> None:
        self.db.execute(
            update(RefreshTokenORM)
            .where(RefreshTokenORM.usuario_id == usuario_id)
            .values(revocado=True)
        )
        self.db.commit()

    # --- Gestion de Tokens de Recuperacion (uso unico) ---
    def guardar_token_recuperacion(
        self, usuario_id: int, jti: str, expira_en: datetime
    ) -> TokenRecuperacionORM | None:
        ahora = datetime.now(UTC)
        reserva = self.db.execute(
            update(UsuarioORM)
            .where(
                UsuarioORM.id == usuario_id,
                or_(
                    UsuarioORM.proxima_recuperacion.is_(None),
                    UsuarioORM.proxima_recuperacion <= ahora,
                ),
            )
            .values(proxima_recuperacion=ahora + timedelta(minutes=1))
            .execution_options(synchronize_session=False)
        )
        if reserva.rowcount != 1:
            self.db.rollback()
            return None
        registro = TokenRecuperacionORM(
            usuario_id=usuario_id,
            jti=jti,
            expira_en=expira_en,
            usado=False,
        )
        self.db.add(registro)
        self.db.commit()
        self.db.refresh(registro)
        return registro

    def obtener_token_recuperacion_por_jti(self, jti: str) -> TokenRecuperacionORM | None:
        return self.db.scalar(select(TokenRecuperacionORM).where(TokenRecuperacionORM.jti == jti))

    def consumir_recuperacion_y_cambiar_password(
        self,
        usuario_id: int,
        jti: str,
        nuevo_password_hash: str,
    ) -> None:
        ahora = datetime.now(UTC)
        # Marca el token actual como usado e invalida cualquier otro pendiente del usuario
        self.db.execute(
            update(TokenRecuperacionORM)
            .where(
                TokenRecuperacionORM.usuario_id == usuario_id,
                TokenRecuperacionORM.usado.is_(False),
            )
            .values(usado=True, usado_en=ahora)
        )
        # Actualiza hash, resetea bloqueos e incrementa token_version para invalidar access tokens
        usuario_orm = self.db.get(UsuarioORM, usuario_id)
        if usuario_orm is not None:
            usuario_orm.password_hash = nuevo_password_hash
            usuario_orm.intentos_fallidos = 0
            usuario_orm.bloqueado_hasta = None
            usuario_orm.token_version += 1
        # Revoca todos los refresh tokens previos
        self.db.execute(
            update(RefreshTokenORM)
            .where(RefreshTokenORM.usuario_id == usuario_id)
            .values(revocado=True)
        )
        self.db.commit()
