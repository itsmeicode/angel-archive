from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
import time

from app.config.settings import get_settings
from app.routers import health, auth, angels, users, audit, export, jobs, series
from app.middleware.rate_limiter import limiter
from app.services.cron_manager import initialize_cron, shutdown_cron


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events"""
    initialize_cron()
    yield
    shutdown_cron()


settings = get_settings()

app = FastAPI(
    title="Angel Archive API",
    description="Backend API for Angel Archive - Sonny Angel collection management",
    version="1.0.0",
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """Track request metrics for health monitoring"""
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    health.record_request(duration_ms, response.status_code >= 400)
    return response


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(angels.router)
app.include_router(users.router)
app.include_router(audit.router)
app.include_router(export.router)
app.include_router(jobs.router)
app.include_router(series.router)


@app.get("/")
async def root():
    return {"message": "Welcome to the API"}
