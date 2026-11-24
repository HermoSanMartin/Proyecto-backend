from sqlalchemy import func, select, update
from sqlalchemy.orm import Session

from app.domain.solicitud_prestamo import EstadoSolicitud, SolicitudPrestamo
from app.infrastructure.mappers.solicitud_mapper import dominio_a_orm, orm_a_dominio
from app.infrastructure.models.obra_de_arte_orm import ObraDeArteORM
from app.infrastructure.models.solicitud_prestamo_orm import SolicitudPrestamoORM


class SolicitudRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def crear(self, solicitud: SolicitudPrestamo) -> SolicitudPrestamo:
        orm = dominio_a_orm(solicitud)
        self.db.add(orm)
        self.db.commit()
        self.db.refresh(orm)
        return orm_a_dominio(orm)

    def obtener_por_id(
        self, solicitud_id: int, *, bloquear: bool = False
    ) -> SolicitudPrestamo | None:
        orm = self.db.get(
            SolicitudPrestamoORM,
            solicitud_id,
            with_for_update=bloquear or None,
            populate_existing=bloquear,
        )
        return orm_a_dominio(orm) if orm else None

    def listar(self) -> list[SolicitudPrestamo]:
        consulta = select(SolicitudPrestamoORM).order_by(SolicitudPrestamoORM.id)
        return [orm_a_dominio(o) for o in self.db.scalars(consulta).all()]

    def contar_aprobadas(self, exposicion_id: int) -> int:
        consulta = (
            select(func.count())
            .select_from(SolicitudPrestamoORM)
            .where(
                SolicitudPrestamoORM.exposicion_id == exposicion_id,
                SolicitudPrestamoORM.estado_solicitud == EstadoSolicitud.APROBADO,
            )
        )
        return self.db.scalar(consulta) or 0

    def actualizar(self, solicitud: SolicitudPrestamo) -> SolicitudPrestamo | None:
        orm = self.db.get(SolicitudPrestamoORM, solicitud.id)
        if orm is None:
            return None
        orm.estado_solicitud = solicitud.estado_solicitud
        self.db.commit()
        self.db.refresh(orm)
        return orm_a_dominio(orm)

    def guardar_aprobacion(
        self, solicitud: SolicitudPrestamo, disponible: bool
    ) -> SolicitudPrestamo:
        # Las filas ya estan bloqueadas por la misma sesion durante la validacion.
        try:
            self.db.execute(
                update(ObraDeArteORM)
                .where(ObraDeArteORM.id == solicitud.obra_id)
                .values(disponible=disponible)
            )
            self.db.execute(
                update(SolicitudPrestamoORM)
                .where(SolicitudPrestamoORM.id == solicitud.id)
                .values(estado_solicitud=solicitud.estado_solicitud)
            )
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        return solicitud
