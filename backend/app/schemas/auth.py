from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LogoutRequest(BaseModel):
    userId: Optional[str] = None


class CreateUserRequest(BaseModel):
    id: str
    email: EmailStr
    username: str
    profile_pic: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    username: str
    profile_pic: Optional[str] = None
    created_at: Optional[datetime] = None


class CheckResponse(BaseModel):
    exists: bool


class EmailLookupResponse(BaseModel):
    email: str
