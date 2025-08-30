from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..auth import get_current_user

router = APIRouter(prefix="/auth", tags=["Auth"])


class ProfileResponse(BaseModel):
    """User profile response model."""
    user_id: str = Field(..., description="User unique identifier (subject)")
    email: str | None = Field(default=None, description="User email address if present in claims")
    role: str | None = Field(default=None, description="Role claim if present")


# PUBLIC_INTERFACE
@router.get("/me", summary="Get current user profile", response_model=ProfileResponse)
def get_me(user=Depends(get_current_user)):
    """Return the current authenticated user's basic profile derived from JWT claims.

    Parameters:
        user: Injected user claims via get_current_user dependency.

    Returns:
        ProfileResponse: Basic profile info from JWT claims.
    """
    return ProfileResponse(
        user_id=str(user.get("sub")),
        email=user.get("email"),
        role=user.get("role"),
    )


class SessionValidationResponse(BaseModel):
    """Represents the result of validating a Supabase session JWT on the backend."""
    valid: bool = Field(..., description="True if the session token is valid")
    user_id: str | None = Field(default=None, description="User ID (sub) if valid")
    email: str | None = Field(default=None, description="Email if present")
    role: str | None = Field(default=None, description="Role if present")
    reason: str | None = Field(default=None, description="Reason if invalid")


# PUBLIC_INTERFACE
@router.get(
    "/validate-session",
    summary="Validate Supabase session JWT",
    description="Validates the Authorization Bearer JWT (from Supabase Auth) and returns basic user info. "
                "Mobile app must forward the Supabase session access_token as the Authorization header.",
    response_model=SessionValidationResponse,
)
def validate_session(user=Depends(get_current_user)):
    """Validate the forwarded Supabase JWT and return basic user info."""
    return SessionValidationResponse(
        valid=True,
        user_id=str(user.get("sub")) if user.get("sub") else None,
        email=user.get("email"),
        role=user.get("role"),
        reason=None,
    )


# PUBLIC_INTERFACE
@router.get("/health", summary="Auth service health check")
def auth_health():
    """Simple health check for the auth router."""
    return {"status": "ok"}
