from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class AngelBase(BaseModel):
    id: int
    name: str
    card_number: Optional[str] = None
    series_id: Optional[int] = None
    image: Optional[str] = None
    image_bw: Optional[str] = None
    image_opacity: Optional[str] = None
    image_profile_pic: Optional[str] = None
    created_at: Optional[datetime] = None


class AngelResponse(AngelBase):
    image_url: Optional[str] = None
    image_bw_url: Optional[str] = None
    image_opacity_url: Optional[str] = None
    image_profile_pic_url: Optional[str] = None


class AngelProfilePicResponse(BaseModel):
    id: int
    name: str
    image_profile_pic: Optional[str] = None
    image_url: Optional[str] = None


class SeriesResponse(BaseModel):
    id: int
    name: str
    created_at: Optional[datetime] = None
