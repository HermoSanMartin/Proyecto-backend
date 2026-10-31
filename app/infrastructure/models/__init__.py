from app.infrastructure.models.artista_orm import ArtistaORM
from app.infrastructure.models.base import Base
from app.infrastructure.models.exposicion_orm import ExposicionORM
from app.infrastructure.models.obra_de_arte_orm import ObraDeArteORM
from app.infrastructure.models.solicitud_prestamo_orm import SolicitudPrestamoORM

__all__ = [
    "Base",
    "ArtistaORM",
    "ObraDeArteORM",
    "ExposicionORM",
    "SolicitudPrestamoORM",
]