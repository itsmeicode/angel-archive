from fastapi import APIRouter
from typing import List

from app.config.supabase import get_supabase
from app.schemas.angels import SeriesResponse


router = APIRouter(prefix="/series", tags=["series"])


@router.get("", response_model=List[SeriesResponse])
async def get_all_series():
    """Get all series (id + name)"""
    supabase = get_supabase()
    result = supabase.table("series").select("*").order("name").execute()
    return result.data or []

