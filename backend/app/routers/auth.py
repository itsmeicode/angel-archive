from fastapi import APIRouter, HTTPException
from typing import Any

from app.config.supabase import get_supabase, get_supabase_admin
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    LogoutRequest,
    CreateUserRequest,
    CheckResponse,
    EmailLookupResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

def _normalize_email(email: str) -> str:
    # Defensive normalization (helps when users paste quotes/whitespace)
    return str(email).strip().strip('"').strip("'").strip()


@router.get("")
async def auth_root():
    return {"message": "Auth routes are working"}


@router.post("/signup")
async def signup(request: SignupRequest) -> Any:
    """
    Create a Supabase Auth user and the app-profile row in public.users.

    Important: Using the Admin API here avoids dev-time email rate limits
    (and can auto-confirm emails), which otherwise cause 429s during testing.
    """
    email = _normalize_email(request.email)

    try:
        supabase_admin = get_supabase_admin()
        auth_result = supabase_admin.auth.admin.create_user({
            "email": email,
            "password": request.password,
            "email_confirm": True,
        })
    except Exception as e:
        # Supabase-py raises AuthApiError / HTTPStatusError; surface as 400 for the UI.
        raise HTTPException(status_code=400, detail=str(e))

    if auth_result is None or auth_result.user is None:
        raise HTTPException(status_code=400, detail="Signup failed")

    # Create app user profile row (bypasses RLS via service role key)
    try:
        supabase_admin.table("users").insert({
            "id": auth_result.user.id,
            "email": auth_result.user.email,
            # username/profile_pic are set by a follow-up call from the UI
        }).execute()
    except Exception:
        # If the row already exists (e.g. re-run), ignore; username is set later.
        pass

    return {
        "user": {
            "id": auth_result.user.id,
            "email": auth_result.user.email,
        },
        "session": None,
    }


@router.post("/login")
async def login(request: LoginRequest) -> Any:
    supabase = get_supabase()
    email = _normalize_email(request.email)
    result = supabase.auth.sign_in_with_password({
        "email": email,
        "password": request.password
    })

    if result.user is None:
        raise HTTPException(status_code=400, detail="Invalid credentials")

    return {
        "user": {
            "id": result.user.id,
            "email": result.user.email,
        },
        "session": result.session
    }


@router.post("/logout")
async def logout(request: LogoutRequest) -> Any:
    supabase = get_supabase()
    supabase.auth.sign_out()
    return {"message": "Logged out successfully"}


@router.get("/check/username/{username}")
async def check_username(username: str) -> CheckResponse:
    # Use admin client because RLS blocks anon reads on public.users
    supabase = get_supabase_admin()
    result = supabase.table("users").select("username").eq("username", username).execute()
    return CheckResponse(exists=len(result.data) > 0)


@router.get("/check/email/{email}")
async def check_email(email: str) -> CheckResponse:
    # Use admin client because RLS blocks anon reads on public.users
    supabase = get_supabase_admin()
    result = supabase.table("users").select("email").eq("email", _normalize_email(email)).execute()
    return CheckResponse(exists=len(result.data) > 0)


@router.get("/user")
async def get_current_user() -> Any:
    supabase = get_supabase()
    result = supabase.auth.get_user()

    if result is None or result.user is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    return {
        "user": {
            "id": result.user.id,
            "email": result.user.email,
        }
    }


@router.post("/users", status_code=201)
async def create_user(request: CreateUserRequest) -> Any:
    # Use admin client to bypass RLS, but this endpoint should only be called
    # immediately after signup for the same user.
    supabase = get_supabase_admin()

    result = supabase.table("users").upsert({
        "id": request.id,
        "email": _normalize_email(request.email),
        "username": request.username,
        "profile_pic": request.profile_pic,
    }, on_conflict="id").execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create user")

    return result.data[0]


@router.get("/users/by-username/{username}")
async def get_user_by_username(username: str) -> EmailLookupResponse:
    # Use admin client because RLS blocks anon reads on public.users
    supabase = get_supabase_admin()
    result = supabase.table("users").select("email").eq("username", username).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")

    return EmailLookupResponse(email=result.data[0]["email"])
