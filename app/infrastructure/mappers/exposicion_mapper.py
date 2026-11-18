from app.domain.exposicion import Exposicion
from app.infrastructure.models.exposicion_orm import ExposicionORM


def orm_a_dominio(orm: ExposicionORM) -> Exposicion:
    return Exposicion(
        id=orm.id,
        nombre_evento=orm.nombre_evento,
        lugar=orm.lugar,
        fecha_inicio=orm.fecha_inicio,
        fecha_fin=orm.fecha_fin,
        estado=orm.estado,
    )


def dominio_a_orm(exposicion: Exposicion) -> ExposicionORM:
    return ExposicionORM(
        id=exposicion.id,
        nombre_evento=exposicion.nombre_evento,
        lugar=exposicion.lugar,
        fecha_inicio=exposicion.fecha_inicio,
        fecha_fin=exposicion.fecha_fin,
        estado=exposicion.estado,
    )