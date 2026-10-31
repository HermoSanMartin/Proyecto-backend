from app.domain.obra_de_arte import ObraDeArte
from app.infrastructure.models.obra_de_arte_orm import ObraDeArteORM


def orm_a_dominio(orm: ObraDeArteORM) -> ObraDeArte:
    return ObraDeArte(
        id=orm.id,
        titulo=orm.titulo,
        precio_estimado=orm.precio_estimado,
        anio_creacion=orm.anio_creacion,
        estilo=orm.estilo,
        disponible=orm.disponible,
        artista_id=orm.artista_id,
    )


def dominio_a_orm(obra: ObraDeArte) -> ObraDeArteORM:
    return ObraDeArteORM(
        id=obra.id,
        titulo=obra.titulo,
        precio_estimado=obra.precio_estimado,
        anio_creacion=obra.anio_creacion,
        estilo=obra.estilo,
        disponible=obra.disponible,
        artista_id=obra.artista_id,
    )