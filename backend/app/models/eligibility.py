from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base
from ..utils.validators import now


class EligibilityRecord(Base):
    """A qualification or identity document submitted by a user and verified by staff."""
    __tablename__ = "eligibility_records"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    requirement_type: Mapped[str] = mapped_column(String(80))  # "identity" or a qualification name
    status: Mapped[str] = mapped_column(String(20), default="pending")  # pending | verified | rejected
    document_url: Mapped[str | None] = mapped_column(String(500))
    verified_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=now)
