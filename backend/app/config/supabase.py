from supabase import create_client, Client
from functools import lru_cache

from app.config.settings import get_settings


@lru_cache
def get_supabase() -> Client:
    """Get Supabase client (uses anon key, respects RLS)"""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_key)


@lru_cache
def get_supabase_admin() -> Client:
    """Service role client for admin operations (bypasses RLS)"""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_service_key)
