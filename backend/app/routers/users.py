from fastapi import APIRouter, HTTPException
from typing import List, Any
from datetime import datetime

from app.config.supabase import get_supabase
from app.config.settings import get_settings
from app.schemas.users import UserProfile, UserProfileUpdate
from app.schemas.collections import (
    CollectionItemCreate,
    CollectionItemResponse,
    CollectionDeleteResponse,
)

router = APIRouter(prefix="/api/users", tags=["users"])

settings = get_settings()


def add_collection_image_urls(collection: dict) -> dict:
    """Add full CDN URLs to collection angel images"""
    base_url = settings.storage_base_url
    angels = collection.get("angels", {})
    
    if angels:
        angels_with_urls = {
            **angels,
            "image_url": f"{base_url}/{angels['image']}" if angels.get("image") else None,
            "image_bw_url": f"{base_url}/{angels['image_bw']}" if angels.get("image_bw") else None,
            "image_opacity_url": f"{base_url}/{angels['image_opacity']}" if angels.get("image_opacity") else None,
            "image_profile_pic_url": f"{base_url}/{angels['image_profile_pic']}" if angels.get("image_profile_pic") else None,
        }
        return {**collection, "angels": angels_with_urls}
    
    return collection


@router.get("/{user_id}", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """Get user profile by ID"""
    supabase = get_supabase()
    result = supabase.table("users").select(
        "id, username, email, profile_pic, created_at"
    ).eq("id", user_id).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")

    return result.data


@router.put("/{user_id}", response_model=UserProfile)
async def update_user_profile(user_id: str, updates: UserProfileUpdate):
    """Update user profile (username and/or profile_pic only)"""
    supabase = get_supabase()

    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields to update")

    result = supabase.table("users").update(update_data).eq("id", user_id).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to update user")

    return result.data[0]


@router.get("/{user_id}/collections", response_model=List[CollectionItemResponse])
async def get_user_collections(user_id: str):
    """Get all collection items for a user with angel details"""
    supabase = get_supabase()
    result = supabase.table("user_collections").select(
        "*, angels:angel_id (id, name, series_id, image, image_bw, image_opacity, image_profile_pic)"
    ).eq("user_id", user_id).order("updated_at", desc=True).execute()

    if not result.data:
        return []

    return [add_collection_image_urls(item) for item in result.data]


@router.post("/{user_id}/collections", response_model=Any)
async def upsert_collection(user_id: str, item: CollectionItemCreate):
    """Add or update a collection item (upsert on user_id + angel_id)"""
    supabase = get_supabase()

    collection_data = {
        "user_id": user_id,
        "angel_id": item.angel_id,
        "count": item.count,
        "trade_count": item.trade_count,
        "is_favorite": item.is_favorite,
        "in_search_of": item.in_search_of,
        "willing_to_trade": item.willing_to_trade,
        "updated_at": datetime.utcnow().isoformat(),
    }

    result = supabase.table("user_collections").upsert(
        collection_data,
        on_conflict="user_id,angel_id"
    ).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to upsert collection")

    return result.data[0]


@router.delete("/{user_id}/collections/{angel_id}", response_model=CollectionDeleteResponse)
async def delete_collection(user_id: str, angel_id: int):
    """Remove an angel from user's collection"""
    supabase = get_supabase()

    result = supabase.table("user_collections").delete().match({
        "user_id": user_id,
        "angel_id": angel_id
    }).execute()

    return CollectionDeleteResponse(success=True, message="Collection item deleted")
