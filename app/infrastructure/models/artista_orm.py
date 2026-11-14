from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import TYPE_CHECKING

from app.infrastructure.models.base import Base

if TYPE_CHECKING:
    from app.infrastructure.models.obra_de_arte_orm import ObraDeArteORM


class ArtistaORM(Base):
    __tablename__ = "artistas"

    id: Mapped[int] = mapped_column(primary_key=True)
    nombre_artistico: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    nacionalidad: Mapped[str] = mapped_column(String(60))
    biografia: Mapped[str] = mapped_column(Text, default="")
    activo: Mapped[bool] = mapped_column(Boolean, default=True)

    obras: Mapped[list["ObraDeArteORM"]] = relationship(back_populates="artista")