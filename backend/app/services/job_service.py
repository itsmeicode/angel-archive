from datetime import datetime
from typing import Optional
import os

from app.config.supabase import get_supabase_admin


async def create_job_run(job_name: str) -> int:
    """Create a new job run record"""
    supabase = get_supabase_admin()
    
    result = supabase.table("job_runs").insert({
        "job_name": job_name,
        "status": "running",
        "started_at": datetime.utcnow().isoformat(),
    }).execute()
    
    return result.data[0]["id"] if result.data else None


async def update_job_run(
    job_id: int,
    status: str,
    images_found: int = 0,
    images_processed: int = 0,
    images_uploaded: int = 0,
    angels_created: int = 0,
    error_message: Optional[str] = None,
):
    """Update job run with results"""
    supabase = get_supabase_admin()
    
    started_at = supabase.table("job_runs").select("started_at").eq("id", job_id).single().execute()
    started = datetime.fromisoformat(started_at.data["started_at"].replace("Z", "+00:00"))
    duration = int((datetime.utcnow() - started.replace(tzinfo=None)).total_seconds())
    
    supabase.table("job_runs").update({
        "status": status,
        "completed_at": datetime.utcnow().isoformat(),
        "images_found": images_found,
        "images_processed": images_processed,
        "images_uploaded": images_uploaded,
        "angels_created": angels_created,
        "error_message": error_message,
        "duration_seconds": duration,
    }).eq("id", job_id).execute()


async def run_asset_pipeline() -> dict:
    """
    Run the asset pipeline job:
    1. Scan scraper/images for new images
    2. Process images (grayscale, opacity, circular)
    3. Upload to Supabase Storage
    4. Create angel records in database
    """
    job_id = await create_job_run("asset_pipeline")
    
    try:
        print("Starting asset pipeline...")
        
        # Placeholder for actual pipeline logic
        # In production, this would:
        # 1. Scan scraper/images/ directory
        # 2. Compare with existing angels in database
        # 3. Process new images through image processing
        # 4. Upload to Supabase Storage
        # 5. Create angel records
        
        images_found = 0
        images_processed = 0
        images_uploaded = 0
        angels_created = 0
        
        await update_job_run(
            job_id,
            status="success",
            images_found=images_found,
            images_processed=images_processed,
            images_uploaded=images_uploaded,
            angels_created=angels_created,
        )
        
        print("Asset pipeline completed successfully")
        
        return {
            "job_id": job_id,
            "status": "success",
            "images_found": images_found,
            "images_processed": images_processed,
            "images_uploaded": images_uploaded,
            "angels_created": angels_created,
        }
        
    except Exception as e:
        await update_job_run(job_id, status="failed", error_message=str(e))
        print(f"Asset pipeline failed: {e}")
        raise


async def get_job_status(limit: int = 10) -> list:
    """Get recent job runs"""
    supabase = get_supabase_admin()
    
    result = supabase.table("job_runs").select("*").order(
        "started_at", desc=True
    ).limit(limit).execute()
    
    return result.data or []


async def get_latest_job_run() -> Optional[dict]:
    """Get the most recent job run"""
    supabase = get_supabase_admin()
    
    result = supabase.table("job_runs").select("*").order(
        "started_at", desc=True
    ).limit(1).execute()
    
    return result.data[0] if result.data else None
