from sqlalchemy import Integer, String, Float, DateTime, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime, UTC
from database import Base

class Game(Base):
    __tablename__ = "games"

    id:Mapped[int] = mapped_column(Integer, primary_key=True, index = True)
    title:Mapped[str] = mapped_column(String(255), index = True)
    platform: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(
        String(20),
        CheckConstraint(
            "status IN ('backlog', 'playing', 'completed', 'dropped')",
            name="ck_status_valid",
        ),
    )
    rating: Mapped[int | None] = mapped_column(
        Integer,
        CheckConstraint("rating >= 1 AND rating <= 10", name="ck_rating_range"),
        nullable=True,
    )
    hours_played: Mapped[float] = mapped_column(Float,default=0.0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(UTC)
    )