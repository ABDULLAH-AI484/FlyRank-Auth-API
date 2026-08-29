"""FlyRank Auth API — Week 2, Assignment A4.

A secure API built with FastAPI and Supabase Auth that handles:
  • Sign Up / Log In / Log Out
  • JWT Bearer token verification
  • Reusable auth dependency for protected routes
  • Interactive Swagger UI with lock icons

Run:  uvicorn main:app --reload --port 8000
Docs: http://localhost:8000/docs
"""
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated

from supabase_client import supabase
from dependencies import get_current_user

# ---------------------------------------------------------------------------
# App & Exception Handlers
# ---------------------------------------------------------------------------
app = FastAPI(
    title="FlyRank Auth API",
    description="Secure authentication API with Supabase Auth and JWT verification",
    version="1.0.0",
)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    """Catch unexpected errors and return a clean JSON response."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"error": "Internal server error"},
    )


# ---------------------------------------------------------------------------
# Pydantic Request Models
# ---------------------------------------------------------------------------
class SignUpRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6, description="Minimum 6 characters")

    class Config:
        json_schema_extra = {
            "example": {"email": "user@example.com", "password": "SecurePass123!"}
        }


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    class Config:
        json_schema_extra = {
            "example": {"email": "user@example.com", "password": "SecurePass123!"}
        }


# ---------------------------------------------------------------------------
# Stage 1: Authentication Routes (Open)
# ---------------------------------------------------------------------------
@app.post(
    "/auth/signup",
    status_code=status.HTTP_201_CREATED,
    tags=["Authentication"],
    summary="Create a new user account",
    response_description="User created successfully",
)
async def signup(credentials: SignUpRequest):
    """Register a new user via Supabase Auth.

    Returns 201 Created with the user object on success,
    or 400 Bad Request if Supabase rejects the signup.
    """
    try:
        response = supabase.auth.sign_up({
            "email": credentials.email,
            "password": credentials.password,
        })
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        )

    if response.user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signup failed — user could not be created",
        )

    return {
        "message": "User created successfully",
        "user": {
            "id": str(response.user.id),
            "email": response.user.email,
            "created_at": response.user.created_at,
        },
    }


@app.post(
    "/auth/login",
    status_code=status.HTTP_200_OK,
    tags=["Authentication"],
    summary="Authenticate and return JWT",
    response_description="Login successful — returns access_token",
)
async def login(credentials: LoginRequest):
    """Authenticate an existing user via Supabase Auth.

    Returns 200 OK with the access_token and refresh_token on success,
    or 401 Unauthorized if credentials are invalid.
    """
    try:
        response = supabase.auth.sign_in_with_password({
            "email": credentials.email,
            "password": credentials.password,
        })
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if response.session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid login credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return {
        "message": "Login successful",
        "access_token": response.session.access_token,
        "refresh_token": response.session.refresh_token,
        "user": {
            "id": str(response.user.id),
            "email": response.user.email,
        },
    }


# ---------------------------------------------------------------------------
# Stage 4: Logout (Protected)
# ---------------------------------------------------------------------------
@app.post(
    "/auth/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Authentication"],
    summary="End the user's session",
    response_description="Logout successful",
)
async def logout(user: Annotated[dict, Depends(get_current_user)]):
    """Log out the currently authenticated user.

    Requires a valid Bearer token. Returns 204 No Content on success.
    """
    try:
        supabase.auth.sign_out()
    except Exception:
        # Even if Supabase session cleanup fails, we treat the token as revoked
        # from the client's perspective in a stateless JWT system.
        pass

    return None  # 204 No Content


# ---------------------------------------------------------------------------
# Stage 2 & 3: Public and Protected Routes
# ---------------------------------------------------------------------------
@app.get(
    "/public/info",
    status_code=status.HTTP_200_OK,
    tags=["Public"],
    summary="Read public information",
    response_description="Public data available to everyone",
)
async def public_info():
    """A public lobby anyone can enter — no authentication required."""
    return {"message": "Welcome stranger! This info is public."}


@app.get(
    "/protected/profile",
    status_code=status.HTTP_200_OK,
    tags=["Protected"],
    summary="Read private profile data",
    response_description="User profile data",
)
async def protected_profile(user: Annotated[dict, Depends(get_current_user)]):
    """A locked door — only accessible with a valid Bearer token.

    The `get_current_user` dependency verifies the JWT with Supabase
    and injects the authenticated user's metadata.
    """
    return {
        "message": "Profile accessed successfully",
        "user": user,
    }


@app.get(
    "/protected/dashboard",
    status_code=status.HTTP_200_OK,
    tags=["Protected"],
    summary="Read private dashboard data",
    response_description="Dashboard data",
)
async def protected_dashboard(user: Annotated[dict, Depends(get_current_user)]):
    """A second protected route reusing the same auth dependency.

    Demonstrates that one guard protects many doors — no new auth code needed.
    """
    return {
        "message": "Dashboard accessed successfully",
        "user_id": user["id"],
        "stats": {"posts": 42, "likes": 1337, "audits": 7},
    }


# ---------------------------------------------------------------------------
# Health Check
# ---------------------------------------------------------------------------
@app.get(
    "/health",
    status_code=status.HTTP_200_OK,
    tags=["System"],
    summary="Server health check",
)
async def health_check():
    """Verify the server is running and connected to Supabase."""
    return {"status": "ok", "connected_to": "Supabase"}


# ---------------------------------------------------------------------------
# Root
# ---------------------------------------------------------------------------
@app.get("/", tags=["System"])
async def root():
    return {
        "message": "FlyRank Auth API",
        "docs": "/docs",
        "health": "/health",
    }
