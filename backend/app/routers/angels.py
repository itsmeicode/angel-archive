from fastapi import APIRouter, HTTPException
from typing import List

from app.config.supabase import get_supabase
from app.config.settings import get_settings
from app.schemas.angels import AngelResponse, AngelProfilePicResponse

router = APIRouter(prefix="/angels", tags=["angels"])

settings = get_settings()


def add_image_urls(angel: dict) -> dict:
    """Add full CDN URLs to angel image paths"""
    base_url = settings.storage_base_url
    return {
        **angel,
        "image_url": f"{base_url}/{angel['image']}" if angel.get("image") else None,
        "image_bw_url": f"{base_url}/{angel['image_bw']}" if angel.get("image_bw") else None,
        "image_opacity_url": f"{base_url}/{angel['image_opacity']}" if angel.get("image_opacity") else None,
        "image_profile_pic_url": f"{base_url}/{angel['image_profile_pic']}" if angel.get("image_profile_pic") else None,
    }


@router.get("", response_model=List[AngelResponse])
async def get_all_angels():
    """Get all angels with image URLs"""
    supabase = get_supabase()
    result = supabase.table("angels").select("*").execute()

    if not result.data:
        return []

    return [add_image_urls(angel) for angel in result.data]


@router.get("/profile-pictures", response_model=List[AngelProfilePicResponse])
async def get_profile_pictures():
    """Get angels with profile picture URLs (for profile pic selection)"""
    supabase = get_supabase()
    result = supabase.table("angels").select("id, name, image_profile_pic").execute()

    if not result.data:
        return []

    base_url = settings.storage_base_url
    return [
        {
            **angel,
            "image_url": f"{base_url}/{angel['image_profile_pic']}" if angel.get("image_profile_pic") else None,
        }
        for angel in result.data
    ]


@router.get("/series/{series_id}", response_model=List[AngelResponse])
async def get_angels_by_series(series_id: int):
    """Get all angels in a specific series"""
    supabase = get_supabase()
    result = supabase.table("angels").select("*").eq("series_id", series_id).execute()

    if not result.data:
        return []

    return [add_image_urls(angel) for angel in result.data]


@router.get("/{angel_id}", response_model=AngelResponse)
async def get_angel_by_id(angel_id: int):
    """Get a single angel by ID"""
    supabase = get_supabase()
    result = supabase.table("angels").select("*").eq("id", angel_id).single().execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="Angel not found")

    return add_image_urls(result.data)
