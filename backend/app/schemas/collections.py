from pydantic import BaseModel
from typing import Optional
from datetime import datetime


class CollectionItemBase(BaseModel):
    angel_id: int
    count: int = 0
    is_favorite: bool = False
    in_search_of: bool = False
    willing_to_trade: bool = False


class CollectionItemCreate(CollectionItemBase):
    pass


class CollectionItemResponse(CollectionItemBase):
    id: int
    user_id: str
    updated_at: Optional[datetime] = None
    angels: Optional[dict] = None


class CollectionDeleteResponse(BaseModel):
    success: bool
    message: str
