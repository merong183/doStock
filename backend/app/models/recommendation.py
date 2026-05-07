from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_level: Mapped[str | None] = mapped_column(String(16), nullable=True)  # low | mid | high
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
