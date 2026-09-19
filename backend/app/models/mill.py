from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

MILL_STATUSES = ("grinding", "idle", "wash")
DEFAULT_MILL_STATUS = "idle"


def normalize_mill_status(value: str | None) -> str | None:
    """把机台状态归一到约定枚举；无法识别返回 None。"""
    if value is None:
        return None
    status = str(value).strip().lower()
    return status if status in MILL_STATUSES else None


class Mill(Base):
    __tablename__ = "mills"
    __table_args__ = (UniqueConstraint("workshop_id", "mill_code", name="uq_mill_workshop_code"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    workshop_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("workshops.id", ondelete="CASCADE"), nullable=False
    )
    mill_code: Mapped[str] = mapped_column(String(64), nullable=False)
    pigment_base: Mapped[str] = mapped_column(String(128), nullable=False)
    bowl_liters: Mapped[Decimal] = mapped_column(Numeric(8, 2), nullable=False, default=0)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="idle")
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.current_timestamp()
    )

    workshop: Mapped["Workshop"] = relationship("Workshop", back_populates="mills")
    viscosity_samples: Mapped[list["ViscositySample"]] = relationship(
        "ViscositySample", back_populates="mill"
    )
    grind_passes: Mapped[list["GrindPass"]] = relationship("GrindPass", back_populates="mill")
