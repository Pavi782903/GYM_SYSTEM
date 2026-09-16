from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from enum import Enum


class RoleEnum(str, Enum):
    member = "member"
    admin = "admin"


class StatusEnum(str, Enum):
    confirmed = "confirmed"
    cancelled = "cancelled"


# ─── Auth ────────────────────────────────────────────────────────────────────

class UserRegister(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: RoleEnum = RoleEnum.member


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: RoleEnum
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ─── Classes ─────────────────────────────────────────────────────────────────

class ClassCreate(BaseModel):
    title: str
    instructor: str
    category: str
    capacity: int
    schedule_time: datetime


class ClassUpdate(BaseModel):
    title: Optional[str] = None
    instructor: Optional[str] = None
    category: Optional[str] = None
    capacity: Optional[int] = None
    schedule_time: Optional[datetime] = None


class ClassOut(BaseModel):
    id: int
    title: str
    instructor: str
    category: str
    capacity: int
    available_spots: int
    schedule_time: datetime
    created_at: datetime

    class Config:
        from_attributes = True


# ─── Bookings ────────────────────────────────────────────────────────────────

class BookingOut(BaseModel):
    id: int
    user_id: int
    class_id: int
    booking_date: datetime
    status: StatusEnum
    created_at: datetime
    gym_class: Optional[ClassOut] = None
    user: Optional[UserOut] = None

    class Config:
        from_attributes = True
