import datetime
from typing import List, Optional

from sqlalchemy import BigInteger, Boolean, Date, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_user_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    height_cm: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    weight_kg: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    onboarding_complete: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0", nullable=False
    )
    selected_occasion: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    language: Mapped[str] = mapped_column(String, default="en", server_default="en", nullable=False)
    daily_check_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    last_check_date: Mapped[Optional[datetime.date]] = mapped_column(Date, nullable=True)
    last_flow_image_path: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    outfit_checks: Mapped[List["OutfitCheck"]] = relationship(
        "OutfitCheck", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<User id={self.id} tg={self.telegram_user_id}>"


class OutfitCheck(Base):
    __tablename__ = "outfit_checks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    image_path: Mapped[str] = mapped_column(String, nullable=False)
    result_text: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship("User", back_populates="outfit_checks")

    def __repr__(self) -> str:
        return f"<OutfitCheck id={self.id} user_id={self.user_id}>"
