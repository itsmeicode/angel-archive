from fastapi import APIRouter, Query
from typing import List, Any

from app.config.supabase import get_supabase_admin

router = APIRouter(prefix="/api/audit", tags=["audit"])


@router.get("")
async def get_audit_logs(
    limit: int = Query(default=100, le=1000),
    offset: int = Query(default=0),
) -> List[Any]:
    """Get all audit logs (paginated)"""
    supabase = get_supabase_admin()
    result = supabase.table("audit_logs").select("*").order(
        "timestamp", desc=True
    ).range(offset, offset + limit - 1).execute()

    return result.data or []


@router.get("/user/{user_id}")
async def get_user_audit_logs(
    user_id: str,
    limit: int = Query(default=50, le=500),
) -> List[Any]:
    """Get audit logs for a specific user"""
    supabase = get_supabase_admin()
    result = supabase.table("audit_logs").select("*").eq(
        "user_id", user_id
    ).order("timestamp", desc=True).limit(limit).execute()

    return result.data or []


@router.get("/stats")
async def get_audit_stats() -> dict:
    """Get audit log statistics"""
    supabase = get_supabase_admin()
    
    total_result = supabase.table("audit_logs").select("id", count="exact").execute()
    total_count = total_result.count or 0
    
    actions_result = supabase.table("audit_logs").select("action").execute()
    action_counts = {}
    for log in actions_result.data or []:
        action = log.get("action", "unknown")
        action_counts[action] = action_counts.get(action, 0) + 1
    
    recent_result = supabase.table("audit_logs").select("*").order(
        "timestamp", desc=True
    ).limit(10).execute()
    
    return {
        "total_logs": total_count,
        "actions_breakdown": action_counts,
        "recent_activity": recent_result.data or [],
    }
