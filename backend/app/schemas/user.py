from typing import Literal

from pydantic import BaseModel, EmailStr, Field

from . import ORM


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    role: str = "user"  # public sign-up may only choose user or owner


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class UserOut(ORM):
    id: int
    name: str
    email: str
    role: str
    verification_status: str
    active: bool


class UserUpdate(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=120)
    role: Literal["user", "owner", "manager", "admin"] | None = None
    verification_status: Literal["unverified", "pending", "verified", "rejected"] | None = None
    active: bool | None = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class EligibilityIn(BaseModel):
    requirement_type: str = Field(min_length=2, max_length=80)
    document_url: str | None = None


class EligibilityReview(BaseModel):
    status: Literal["verified", "rejected"]
