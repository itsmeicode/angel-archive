from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import os

scheduler = AsyncIOScheduler()
is_job_running = False


def get_cron_status() -> dict:
    """Get current cron scheduler status"""
    return {
        "enabled": os.getenv("CRON_ENABLED", "false").lower() == "true",
        "schedule": os.getenv("CRON_SCHEDULE", "0 2 * * 0"),
        "running": scheduler.running,
        "job_in_progress": is_job_running,
        "next_run": None,
    }


async def run_scheduled_job():
    """Wrapper for scheduled job execution"""
    global is_job_running
    
    if is_job_running:
        print("Job already running, skipping...")
        return
    
    is_job_running = True
    try:
        from app.services.job_service import run_asset_pipeline
        await run_asset_pipeline()
    finally:
        is_job_running = False


def initialize_cron():
    """Initialize the cron scheduler"""
    cron_enabled = os.getenv("CRON_ENABLED", "false").lower() == "true"
    
    if not cron_enabled:
        print("Cron scheduler disabled (CRON_ENABLED=false)")
        return
    
    cron_schedule = os.getenv("CRON_SCHEDULE", "0 2 * * 0")
    
    try:
        trigger = CronTrigger.from_crontab(cron_schedule)
        scheduler.add_job(
            run_scheduled_job,
            trigger=trigger,
            id="asset_pipeline",
            name="Asset Pipeline Job",
            replace_existing=True,
        )
        scheduler.start()
        print(f"Cron scheduler started with schedule: {cron_schedule}")
    except Exception as e:
        print(f"Failed to start cron scheduler: {e}")


def shutdown_cron():
    """Shutdown the cron scheduler"""
    if scheduler.running:
        scheduler.shutdown()
        print("Cron scheduler stopped")
