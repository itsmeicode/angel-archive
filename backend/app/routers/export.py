from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse, StreamingResponse
from typing import Any
from datetime import datetime, timedelta
import csv
import io

from app.config.supabase import get_supabase
from app.config.settings import get_settings

router = APIRouter(prefix="/api/export", tags=["export"])

settings = get_settings()

export_timestamps: dict[str, datetime] = {}


def can_export(user_id: str) -> tuple[bool, str]:
    """Check if user can export (1 hour cooldown in production)"""
    if settings.is_development or settings.disable_rate_limit:
        return True, ""
    
    last_export = export_timestamps.get(user_id)
    if last_export:
        time_since = datetime.utcnow() - last_export
        if time_since < timedelta(hours=1):
            remaining = timedelta(hours=1) - time_since
            minutes = int(remaining.total_seconds() / 60)
            return False, f"Please wait {minutes} minutes before exporting again"
    
    return True, ""


@router.get("/users/{user_id}")
async def export_user_data(
    user_id: str,
    format: str = Query(default="json", regex="^(json|csv)$"),
) -> Any:
    """Export user collection data as JSON or CSV"""
    can, message = can_export(user_id)
    if not can:
        raise HTTPException(status_code=429, detail=message)
    
    supabase = get_supabase()
    
    collections_result = supabase.table("user_collections").select(
        "*, angels:angel_id (name, series_id, card_number)"
    ).eq("user_id", user_id).execute()
    
    collections = collections_result.data or []
    
    export_data = {
        "exported_at": datetime.utcnow().isoformat(),
        "user_id": user_id,
        "collection": [
            {
                "angel_name": item.get("angels", {}).get("name"),
                "series_id": item.get("angels", {}).get("series_id"),
                "card_number": item.get("angels", {}).get("card_number"),
                "count": item.get("count", 0),
                "is_favorite": item.get("is_favorite", False),
                "in_search_of": item.get("in_search_of", False),
                "willing_to_trade": item.get("willing_to_trade", False),
            }
            for item in collections
        ],
        "summary": {
            "total_cards": sum(item.get("count", 0) for item in collections),
            "total_in_search": sum(1 for item in collections if item.get("in_search_of")),
            "total_willing_to_trade": sum(1 for item in collections if item.get("willing_to_trade")),
        },
    }
    
    export_timestamps[user_id] = datetime.utcnow()
    
    if format == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow([
            "angel_name", "series_id", "card_number", "count",
            "is_favorite", "in_search_of", "willing_to_trade"
        ])
        
        for item in export_data["collection"]:
            writer.writerow([
                item["angel_name"],
                item["series_id"],
                item["card_number"],
                item["count"],
                item["is_favorite"],
                item["in_search_of"],
                item["willing_to_trade"],
            ])
        
        output.seek(0)
        return StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename=angel_archive_export_{user_id}.csv"
            }
        )
    
    return JSONResponse(content=export_data)


@router.get("/users/{user_id}/status")
async def get_export_status(user_id: str) -> dict:
    """Get export status (last export time, can export)"""
    can, message = can_export(user_id)
    last_export = export_timestamps.get(user_id)
    
    # Calculate time remaining if rate limited
    time_remaining = None
    if not can and last_export:
        time_since = datetime.utcnow() - last_export
        remaining = timedelta(hours=1) - time_since
        time_remaining = max(0, int(remaining.total_seconds() / 60))
    
    return {
        "canExport": can,  # camelCase for frontend
        "timeRemaining": time_remaining,
        "message": message if not can else "Ready to export",
        "lastExport": last_export.isoformat() if last_export else None,
    }
