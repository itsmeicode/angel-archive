from fastapi import APIRouter, HTTPException
from typing import Any

from app.services.job_service import run_asset_pipeline, get_job_status, get_latest_job_run
from app.services.cron_manager import get_cron_status, is_job_running

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("/trigger")
async def trigger_job() -> Any:
    """Manually trigger the asset pipeline job"""
    if is_job_running:
        raise HTTPException(
            status_code=409,
            detail="Job is already running. Please wait for it to complete."
        )
    
    try:
        result = await run_asset_pipeline()
        return {
            "success": True,
            "message": "Asset pipeline completed successfully",
            "result": result,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Job failed: {str(e)}"
        )


@router.get("/status")
async def get_jobs_status(limit: int = 10) -> Any:
    """Get job history"""
    try:
        jobs = await get_job_status(limit)
        return {
            "success": True,
            "jobs": jobs,
            "cron": get_cron_status(),
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get job status: {str(e)}"
        )


@router.get("/latest")
async def get_latest_job() -> Any:
    """Get the most recent job run"""
    try:
        job = await get_latest_job_run()
        
        if not job:
            return {
                "success": True,
                "message": "No jobs have been run yet",
                "job": None,
            }
        
        return {
            "success": True,
            "job": job,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get latest job: {str(e)}"
        )


@router.get("/cron")
async def get_cron() -> Any:
    """Get cron scheduler status"""
    return {
        "success": True,
        "cron": get_cron_status(),
    }
