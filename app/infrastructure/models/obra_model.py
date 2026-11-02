from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class ObraDeArteModel(Base):
    __tablename__ = "obras"

    id: Mapped[int] = mapped_column(primary_key=True)
    titulo: Mapped[str] = mapped_column(String(150))
    precio_estimado: Mapped[float] = mapped_column(Numeric(12, 2, asdecimal=False))
    anio_creacion: Mapped[int] = mapped_column(Integer)
    estilo: Mapped[str] = mapped_column(String(60), index=True)
    disponible: Mapped[bool] = mapped_column(Boolean, default=True)
    artista_id: Mapped[int] = mapped_column(ForeignKey("artistas.id"))

    artista: Mapped["ArtistaModel"] = relationship(back_populates="obras")