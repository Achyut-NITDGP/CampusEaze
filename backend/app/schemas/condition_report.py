from typing import Literal

from pydantic import BaseModel, Field, field_validator


class ReportIn(BaseModel):
    condition_notes: str = Field("", max_length=2000)
    checklist_ok: bool = True
    damage_reported: bool = False
    photo_urls: list[str] = []

    @field_validator("photo_urls")
    @classmethod
    def only_uploads(cls, v):
        if any(not u.startswith("/uploads/") for u in v):
            raise ValueError("photo_urls must come from the upload endpoint")
        return v


class ReportReview(BaseModel):
    outcome: Literal["cleared", "discrepancy_confirmed"]
    note: str = Field(min_length=3, max_length=1000)
