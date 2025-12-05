from fastapi import APIRouter, HTTPException
from typing import Any

from app.config.supabase import get_supabase
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    LogoutRequest,
    CreateUserRequest,
    CheckResponse,
    EmailLookupResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("")
async def auth_root():
    return {"message": "Auth routes are working"}


@router.post("/signup")
async def signup(request: SignupRequest) -> Any:
    supabase = get_supabase()
    result = supabase.auth.sign_up({
        "email": request.email,
        "password": request.password
    })

    if result.user is None:
        raise HTTPException(status_code=400, detail="Signup failed")

    return {
        "user": {
            "id": result.user.id,
            "email": result.user.email,
        },
        "session": result.session
    }


@router.post("/login")
async def login(request: LoginRequest) -> Any:
    supabase = get_supabase()
    result = supabase.auth.sign_in_with_password({
        "email": request.email,
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
    supabase = get_supabase()
    result = supabase.table("users").select("username").eq("username", username).execute()
    return CheckResponse(exists=len(result.data) > 0)


@router.get("/check/email/{email}")
async def check_email(email: str) -> CheckResponse:
    supabase = get_supabase()
    result = supabase.table("users").select("email").eq("email", email).execute()
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
    supabase = get_supabase()

    result = supabase.table("users").insert({
        "id": request.id,
        "email": request.email,
        "username": request.username,
        "profile_pic": request.profile_pic
    }).execute()

    if not result.data:
        raise HTTPException(status_code=400, detail="Failed to create user")

    return result.data[0]


@router.get("/users/by-username/{username}")
async def get_user_by_username(username: str) -> EmailLookupResponse:
    supabase = get_supabase()
    result = supabase.table("users").select("email").eq("username", username).execute()

    if not result.data:
        raise HTTPException(status_code=404, detail="User not found")

    return EmailLookupResponse(email=result.data[0]["email"])
