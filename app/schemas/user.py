# app/schemas/user.py
from pydantic import BaseModel, EmailStr
from enum import Enum

class RoleEnum(str, Enum):
    freelancer = "freelancer"
    employer = "employer"

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    role: RoleEnum

class UserOut(UserCreate):
    id: int

    class Config:
        from_attributes = True
