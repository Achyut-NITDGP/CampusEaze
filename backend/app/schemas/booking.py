from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class BookingIn(BaseModel):
    resource_id: int
    start_time: datetime
    end_time: datetime
    purpose: str = Field(min_length=3, max_length=500)


class DecisionIn(BaseModel):
    decision: Literal["approve", "reject", "waitlist"]
    reason: str = Field("", max_length=1000)
