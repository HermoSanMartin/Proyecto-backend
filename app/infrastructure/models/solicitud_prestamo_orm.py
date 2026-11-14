from datetime import date

from sqlalchemy import Date, Enum, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.solicitud_prestamo import EstadoSolicitud
from app.infrastructure.models.base import Base


class SolicitudPrestamoORM(Base):
    __tablename__ = "solicitudes_prestamo"

    id: Mapped[int] = mapped_column(primary_key=True)
    obra_id: Mapped[int] = mapped_column(ForeignKey("obras.id"))
    exposicion_id: Mapped[int] = mapped_column(ForeignKey("exposiciones.id"))
    fecha_solicitud: Mapped[date] = mapped_column(Date)
    dias_prestamo: Mapped[int] = mapped_column(Integer)
    estado_solicitud: Mapped[EstadoSolicitud] = mapped_column(
        Enum(EstadoSolicitud, name="estado_solicitud"),
        default=EstadoSolicitud.PENDIENTE,
    )