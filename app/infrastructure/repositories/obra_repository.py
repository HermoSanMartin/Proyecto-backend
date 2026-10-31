import math

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.domain.obra_de_arte import ObraDeArte
from app.infrastructure.mappers.obra_mapper import dominio_a_orm, orm_a_dominio
from app.infrastructure.models.obra_de_arte_orm import ObraDeArteORM

COLUMNAS_ORDENABLES = {
    "titulo": ObraDeArteORM.titulo,
    "precio_estimado": ObraDeArteORM.precio_estimado,
    "anio_creacion": ObraDeArteORM.anio_creacion,
    "estilo": ObraDeArteORM.estilo,
}


class ObraRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, obra: ObraDeArte) -> ObraDeArte:
        orm = dominio_a_orm(obra)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return orm_a_dominio(orm)

    def obtener_por_id(self, obra_id: int) -> ObraDeArte | None:
        orm = self.db.get(ObraDeArteORM, obra_id)
        return orm_a_dominio(orm) if orm else None

    def listar(
        self,
        estilo: str | None,
        ordenar_por: str,
        direccion: str,
        pagina: int,
        limite: int,
    ) -> tuple[list[ObraDeArte], int, int]:
        consulta = select(ObraDeArteORM)
        if estilo:
            consulta = consulta.where(ObraDeArteORM.estilo == estilo)

        total = self.db.scalar(
            select(func.count()).select_from(consulta.subquery())
        ) or 0

        columna = COLUMNAS_ORDENABLES[ordenar_por]
        consulta = consulta.order_by(
            columna.desc() if direccion == "desc" else columna.asc()
        )
        consulta = consulta.offset((pagina - 1) * limite).limit(limite)

        obras = [orm_a_dominio(o) for o in self.db.scalars(consulta).all()]
        total_paginas = math.ceil(total / limite) if total else 0
        return obras, total, total_paginas

    def actualizar(self, obra: ObraDeArte) -> ObraDeArte | None:
        orm = self.db.get(ObraDeArteORM, obra.id)
        if orm is None:
            return None
        orm.titulo = obra.titulo
        orm.precio_estimado = obra.precio_estimado
        orm.anio_creacion = obra.anio_creacion
        orm.estilo = obra.estilo
        orm.disponible = obra.disponible
        self.db.commit()
        self.db.refresh(orm)
        return orm_a_dominio(orm)

    def eliminar(self, obra_id: int) -> bool:
        orm = self.db.get(ObraDeArteORM, obra_id)
        if orm is None:
            return False
        self.db.delete(orm)
        self.db.commit()
        return True