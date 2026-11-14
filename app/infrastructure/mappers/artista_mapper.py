from app.domain.artista import Artista
from app.infrastructure.models.artista_orm import ArtistaORM


def orm_a_dominio(orm: ArtistaORM) -> Artista:
    return Artista(
        id=orm.id,
        nombre_artistico=orm.nombre_artistico,
        email=orm.email,
        nacionalidad=orm.nacionalidad,
        biografia=orm.biografia,
        activo=orm.activo,
    )


def dominio_a_orm(artista: Artista) -> ArtistaORM:
    return ArtistaORM(
        id=artista.id,
        nombre_artistico=artista.nombre_artistico,
        email=artista.email,
        nacionalidad=artista.nacionalidad,
        biografia=artista.biografia,
        activo=artista.activo,
    )