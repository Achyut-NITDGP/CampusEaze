from typing import Literal

from pydantic import BaseModel, Field


class IncidentIn(BaseModel):
    booking_id: int
    kind: Literal["damage", "delay", "dispute"]
    description: str = Field(min_length=5, max_length=2000)
    evidence_urls: list[str] = []


class IncidentUpdate(BaseModel):
    status: Literal["investigating", "resolved", "closed"]
    findings: str | None = Field(None, max_length=2000)
    resolution: str | None = Field(None, max_length=2000)
