from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class UserProfile(BaseModel):
    id: str
    username: str
    email: str
    profile_pic: Optional[str] = None
    created_at: Optional[datetime] = None


class UserProfileUpdate(BaseModel):
    username: Optional[str] = None
    profile_pic: Optional[str] = None
