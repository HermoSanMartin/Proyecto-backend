from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.infrastructure.database import Base


class ArtistaModel(Base):
    __tablename__ = "artistas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_artistico: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    nacionalidad: Mapped[str] = mapped_column(String(60))
    biografia: Mapped[str] = mapped_column(Text)
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    obras: Mapped[list["ObraDeArteModel"]] = relationship(back_populates="artista")