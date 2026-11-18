from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.artista import Artista
from app.infrastructure.mappers.artista_mapper import dominio_a_orm, orm_a_dominio
from app.infrastructure.models.artista_orm import ArtistaORM


class ArtistaRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, artista: Artista) -> Artista:
        orm = dominio_a_orm(artista)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return orm_a_dominio(orm)

    def obtener_por_id(self, artista_id: int) -> Artista | None:
        orm = self.db.get(ArtistaORM, artista_id)
        return orm_a_dominio(orm) if orm else None

    def obtener_por_email(self, email: str) -> Artista | None:
        orm = self.db.scalar(select(ArtistaORM).where(ArtistaORM.email == email))
        return orm_a_dominio(orm) if orm else None

    def listar(self) -> list[Artista]:
        consulta = select(ArtistaORM).order_by(ArtistaORM.id)
        return [orm_a_dominio(o) for o in self.db.scalars(consulta).all()]

    def actualizar(self, artista: Artista) -> Artista | None:
        orm = self.db.get(ArtistaORM, artista.id)
        if orm is None:
            return None
        orm.nombre_artistico = artista.nombre_artistico
        orm.email = artista.email
        orm.nacionalidad = artista.nacionalidad
        orm.biografia = artista.biografia
        orm.activo = artista.activo
        self.db.commit()
        self.db.refresh(orm)
        return orm_a_dominio(orm)