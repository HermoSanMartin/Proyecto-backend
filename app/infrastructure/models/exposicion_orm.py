from datetime import date

from sqlalchemy import Date, Enum, String
from sqlalchemy.orm import Mapped, mapped_column

from app.domain.exposicion import EstadoExposicion
from app.infrastructure.models.base import Base


class ExposicionORM(Base):
    __tablename__ = "exposiciones"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_evento: Mapped[str] = mapped_column(String(150))
    lugar: Mapped[str] = mapped_column(String(150))
    fecha_inicio: Mapped[date] = mapped_column(Date)
    fecha_fin: Mapped[date] = mapped_column(Date)
    estado: Mapped[EstadoExposicion] = mapped_column(
        Enum(EstadoExposicion, name="estado_exposicion"),
        default=EstadoExposicion.PLANIFICADA,
    )