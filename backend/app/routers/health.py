from fastapi import APIRouter
from datetime import datetime
import time
import psutil

router = APIRouter(prefix="/health", tags=["health"])

start_time = time.time()
metrics = {
    "request_count": 0,
    "error_count": 0,
    "request_durations": [],
}


def record_request(duration_ms: float, is_error: bool = False):
    """Record request metrics for monitoring"""
    metrics["request_count"] += 1
    if is_error:
        metrics["error_count"] += 1
    metrics["request_durations"].append(duration_ms)
    if len(metrics["request_durations"]) > 1000:
        metrics["request_durations"].pop(0)


@router.get("")
async def health_check():
    """Liveness check - is the service running?"""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": time.time() - start_time,
    }


@router.get("/ready")
async def readiness_check():
    """Readiness check - is the service ready to accept traffic?"""
    checks = {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {},
    }

    process = psutil.Process()
    memory_info = process.memory_info()
    heap_used = memory_info.rss
    heap_total = psutil.virtual_memory().total
    memory_ratio = heap_used / heap_total

    checks["services"]["memory"] = {
        "status": "ok" if memory_ratio < 0.9 else "warning",
        "heapUsed": f"{heap_used // 1024 // 1024}MB",
        "heapTotal": f"{heap_total // 1024 // 1024}MB",
    }

    return checks


@router.get("/metrics")
async def metrics_check():
    """Prometheus-style metrics endpoint"""
    durations = metrics["request_durations"]
    avg_duration = sum(durations) / len(durations) if durations else 0
    sorted_durations = sorted(durations)
    p95_duration = (
        sorted_durations[int(len(sorted_durations) * 0.95)] if sorted_durations else 0
    )

    uptime = time.time() - start_time
    process = psutil.Process()
    memory_info = process.memory_info()

    return {
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": int(uptime),
        "metrics": {
            "http_requests_total": metrics["request_count"],
            "http_errors_total": metrics["error_count"],
            "http_request_duration_avg_ms": round(avg_duration),
            "http_request_duration_p95_ms": round(p95_duration),
            "error_rate": (
                f"{(metrics['error_count'] / metrics['request_count'] * 100):.2f}%"
                if metrics["request_count"] > 0
                else "0%"
            ),
        },
        "system": {
            "memory_heap_used_bytes": memory_info.rss,
            "memory_heap_total_bytes": psutil.virtual_memory().total,
            "memory_rss_bytes": memory_info.rss,
            "uptime_seconds": int(uptime),
        },
    }
