from app.domain.solicitud_prestamo import SolicitudPrestamo
from app.infrastructure.models.solicitud_prestamo_orm import SolicitudPrestamoORM


def orm_a_dominio(orm: SolicitudPrestamoORM) -> SolicitudPrestamo:
    return SolicitudPrestamo(
        id=orm.id,
        obra_id=orm.obra_id,
        exposicion_id=orm.exposicion_id,
        dias_prestamo=orm.dias_prestamo,
        fecha_solicitud=orm.fecha_solicitud,
        estado_solicitud=orm.estado_solicitud,
    )


def dominio_a_orm(solicitud: SolicitudPrestamo) -> SolicitudPrestamoORM:
    return SolicitudPrestamoORM(
        id=solicitud.id,
        obra_id=solicitud.obra_id,
        exposicion_id=solicitud.exposicion_id,
        dias_prestamo=solicitud.dias_prestamo,
        fecha_solicitud=solicitud.fecha_solicitud,
        estado_solicitud=solicitud.estado_solicitud,
    )