from collections.abc import Generator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.application.services.artista_service import ArtistaService
from app.application.services.exposicion_service import ExposicionService
from app.application.services.obra_service import ObraService
from app.application.services.solicitud_service import SolicitudService
from app.infrastructure.database import SessionLocal
from app.infrastructure.repositories.artista_repository import ArtistaRepository
from app.infrastructure.repositories.exposicion_repository import ExposicionRepository
from app.infrastructure.repositories.obra_repository import ObraRepository
from app.infrastructure.repositories.solicitud_repository import SolicitudRepository


def obtener_sesion() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def obtener_servicio_artista(db: Session = Depends(obtener_sesion)) -> ArtistaService:
    return ArtistaService(ArtistaRepository(db))


def obtener_servicio_obra(db: Session = Depends(obtener_sesion)) -> ObraService:
    return ObraService(ObraRepository(db), ArtistaRepository(db))


def obtener_servicio_exposicion(db: Session = Depends(obtener_sesion)) -> ExposicionService:
    return ExposicionService(ExposicionRepository(db))


def obtener_servicio_solicitud(db: Session = Depends(obtener_sesion)) -> SolicitudService:
    return SolicitudService(
        SolicitudRepository(db), ObraRepository(db), ExposicionRepository(db)
    )