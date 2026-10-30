from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from ..utils.validators import now


class ConditionReport(Base):
    __tablename__ = "condition_reports"
    id: Mapped[int] = mapped_column(primary_key=True)
    booking_id: Mapped[int] = mapped_column(ForeignKey("bookings.id"), index=True)
    report_type: Mapped[str] = mapped_column(String(10))  # checkin | checkout
    condition_notes: Mapped[str] = mapped_column(Text, default="")
    checklist_ok: Mapped[bool] = mapped_column(Boolean, default=True)
    damage_reported: Mapped[bool] = mapped_column(Boolean, default=False)
    photo_urls: Mapped[str] = mapped_column(Text, default="")
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    flagged: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    review_outcome: Mapped[str | None] = mapped_column(String(30))
    review_note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
