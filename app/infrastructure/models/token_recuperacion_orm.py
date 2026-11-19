from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.models.base import Base


class TokenRecuperacionORM(Base):
    __tablename__ = "tokens_recuperacion"

    id: Mapped[int] = mapped_column(primary_key=True)
    usuario_id: Mapped[int] = mapped_column(ForeignKey("usuarios.id", ondelete="CASCADE"), index=True)
    jti: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    expira_en: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    usado: Mapped[bool] = mapped_column(Boolean, default=False)
    usado_en: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
