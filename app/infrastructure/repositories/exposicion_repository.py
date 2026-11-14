from sqlalchemy import select
from sqlalchemy.orm import Session

from app.domain.exposicion import Exposicion
from app.infrastructure.mappers.exposicion_mapper import dominio_a_orm, orm_a_dominio
from app.infrastructure.models.exposicion_orm import ExposicionORM


class ExposicionRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, exposicion: Exposicion) -> Exposicion:
        orm = dominio_a_orm(exposicion)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return orm_a_dominio(orm)

    def obtener_por_id(self, exposicion_id: int) -> Exposicion | None:
        orm = self.db.get(ExposicionORM, exposicion_id)
        return orm_a_dominio(orm) if orm else None

    def listar(self) -> list[Exposicion]:
        consulta = select(ExposicionORM).order_by(ExposicionORM.id)
        return [orm_a_dominio(o) for o in self.db.scalars(consulta).all()]