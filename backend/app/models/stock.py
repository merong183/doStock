from datetime import datetime

from sqlalchemy import DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Stock(Base):
    __tablename__ = "stocks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    ticker: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    market: Mapped[str] = mapped_column(String(8), nullable=False)  # KR | US
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
