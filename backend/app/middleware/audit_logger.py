from fastapi import Request
from typing import Optional
from datetime import datetime

from app.config.supabase import get_supabase_admin


async def log_audit(
    action: str,
    resource: str,
    resource_id: Optional[str],
    user_id: Optional[str],
    details: Optional[dict] = None,
    request: Optional[Request] = None,
    status: str = "success",
) -> None:
    """
    Log an audit event to the database.
    
    Args:
        action: Action performed (CREATE, UPDATE, DELETE, LOGIN, LOGOUT, SIGNUP)
        resource: Resource type (user, collection, angel)
        resource_id: ID of the affected resource
        user_id: ID of the user performing the action
        details: Additional context
        request: FastAPI request for IP/user agent
        status: Status of the action (success, failure)
    """
    try:
        supabase = get_supabase_admin()
        
        ip_address = None
        user_agent = None
        
        if request:
            ip_address = request.client.host if request.client else None
            user_agent = request.headers.get("user-agent")
        
        audit_entry = {
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "resource_id": resource_id,
            "details": details,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.utcnow().isoformat(),
            "status": status,
        }
        
        supabase.table("audit_logs").insert(audit_entry).execute()
        
    except Exception as e:
        print(f"Audit log error: {e}")
