from sqlalchemy import Boolean, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.models.base import Base
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.infrastructure.models.artista_orm import ArtistaORM


class ObraDeArteORM(Base):
    __tablename__ = "obras"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(150))
    precio_estimado: Mapped[float] = mapped_column(Float)
    anio_creacion: Mapped[int] = mapped_column(Integer)
    estilo: Mapped[str] = mapped_column(String(60))
    disponible: Mapped[bool] = mapped_column(Boolean, default=True)
    artista_id: Mapped[int] = mapped_column(ForeignKey("artistas.id"))

    artista: Mapped["ArtistaORM"] = relationship(back_populates="obras")