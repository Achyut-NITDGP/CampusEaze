from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class ResourceIn(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str = ""
    category: Literal["equipment", "space", "service"]
    location: str = Field(min_length=2, max_length=160)
    price_per_hour: float = Field(0, ge=0)
    rules: str = ""
    required_qualification: str | None = None
    requires_verification: bool = True
    photo_url: str | None = None
    status: Literal["active", "inactive", "maintenance"] = "active"


class BlockIn(BaseModel):
    start_time: datetime
    end_time: datetime
    reason: str = Field("Blocked", max_length=200)
