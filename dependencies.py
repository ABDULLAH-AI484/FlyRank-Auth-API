"""Authentication dependencies.

The `get_current_user` dependency acts as a reusable guard for protected routes.
It extracts the Bearer token from the Authorization header, verifies it with
Supabase, and injects the authenticated user into the route handler.
"""
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase_client import supabase

# HTTPBearer with auto_error=False so we can return 401 instead of 403
# when the Authorization header is missing
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
) -> dict:
    """Verify the Bearer JWT with Supabase and return the user.

    Args:
        credentials: The parsed Authorization header from HTTPBearer.

    Returns:
        A dict containing the authenticated user's metadata.

    Raises:
        HTTPException: 401 if the token is missing, malformed, or invalid.
    """
    # 1. Check if Authorization header is present and uses Bearer scheme
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Verify the token with Supabase (network call to Supabase Auth)
    try:
        response = supabase.auth.get_user(token)
        user = response.user
    except Exception:
        # Supabase rejected the token (expired, tampered, or invalid)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Return safe user metadata for the route handler
    return {
        "id": str(user.id),
        "email": user.email,
        "created_at": user.created_at,
    }
