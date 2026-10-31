from datetime import date

from sqlalchemy import select

from app.domain.exposicion import EstadoExposicion
from app.domain.solicitud_prestamo import EstadoSolicitud
from app.infrastructure.database import SessionLocal
from app.infrastructure.models import (
    ArtistaORM,
    ExposicionORM,
    ObraDeArteORM,
    SolicitudPrestamoORM,
)


def ejecutar() -> None:
    db = SessionLocal()
    try:
        if db.scalar(select(ArtistaORM).limit(1)) is not None:
            print("La base ya tiene datos; no se cargó nada.")
            return

        artistas = [
            ArtistaORM(nombre_artistico="Frida Kahlo", email="frida@galeria.cl",
                       nacionalidad="Mexicana", biografia="Pintora mexicana.", activo=True),
            ArtistaORM(nombre_artistico="Roberto Matta", email="matta@galeria.cl",
                       nacionalidad="Chilena", biografia="Pintor surrealista chileno.", activo=True),
        ]
        db.add_all(artistas)
        db.flush()

        obras = [
            ObraDeArteORM(titulo="Las dos Fridas", precio_estimado=9000, anio_creacion=1939,
                          estilo="Surrealismo", disponible=True, artista_id=artistas[0].id),
            ObraDeArteORM(titulo="La columna rota", precio_estimado=8000, anio_creacion=1944,
                          estilo="Surrealismo", disponible=True, artista_id=artistas[0].id),
            ObraDeArteORM(titulo="Autorretrato", precio_estimado=7000, anio_creacion=1940,
                          estilo="Realismo", disponible=True, artista_id=artistas[0].id),
            ObraDeArteORM(titulo="Inscape", precio_estimado=6500, anio_creacion=1942,
                          estilo="Surrealismo", disponible=True, artista_id=artistas[1].id),
            ObraDeArteORM(titulo="Los Poderes", precio_estimado=5500, anio_creacion=1950,
                          estilo="Abstracto", disponible=True, artista_id=artistas[1].id),
            ObraDeArteORM(titulo="Vertigo", precio_estimado=5000, anio_creacion=1955,
                          estilo="Abstracto", disponible=True, artista_id=artistas[1].id),
        ]
        db.add_all(obras)

        exposiciones = [
            ExposicionORM(nombre_evento="Muestra Sur", lugar="Temuco",
                          fecha_inicio=date(2026, 12, 1), fecha_fin=date(2026, 12, 15),
                          estado=EstadoExposicion.PLANIFICADA),
            ExposicionORM(nombre_evento="Arte Latinoamericano", lugar="Valdivia",
                          fecha_inicio=date(2027, 1, 10), fecha_fin=date(2027, 1, 30),
                          estado=EstadoExposicion.PLANIFICADA),
        ]
        db.add_all(exposiciones)
        db.flush()

        solicitudes = [
            SolicitudPrestamoORM(obra_id=obras[0].id, exposicion_id=exposiciones[0].id,
                                 fecha_solicitud=date.today(), dias_prestamo=15,
                                 estado_solicitud=EstadoSolicitud.PENDIENTE),
            SolicitudPrestamoORM(obra_id=obras[3].id, exposicion_id=exposiciones[1].id,
                                 fecha_solicitud=date.today(), dias_prestamo=20,
                                 estado_solicitud=EstadoSolicitud.PENDIENTE),
        ]
        db.add_all(solicitudes)
        db.commit()
        print("Datos de ejemplo cargados: 2 artistas, 6 obras, 2 exposiciones y 2 solicitudes.")
    finally:
        db.close()


if __name__ == "__main__":
    ejecutar()