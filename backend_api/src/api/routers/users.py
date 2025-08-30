from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, EmailStr

from ..auth import get_current_user
from ..supabase_client import get_supabase_client

router = APIRouter(prefix="/users", tags=["Users"])


class UserSummary(BaseModel):
    user_id: str = Field(..., description="User ID")
    email: str | None = Field(default=None, description="User email")


class UserProfile(BaseModel):
    """Represents a persisted user profile row in Supabase public.user_profiles table."""
    user_id: str = Field(..., description="User ID (auth subject)")
    email: Optional[EmailStr] = Field(default=None, description="Email")
    display_name: Optional[str] = Field(default=None, description="Display name")
    role: Optional[str] = Field(default="rider", description="App role: rider|host|admin")


class ProfileSyncRequest(BaseModel):
    """Fields to upsert from the mobile app's claims/profile into backend storage."""
    display_name: Optional[str] = Field(default=None, description="Display name to persist")
    role: Optional[str] = Field(default=None, description="Desired role (if allowed)")


class RoleAssignRequest(BaseModel):
    """Admin or self-service role assignment request. Backend must enforce permissions."""
    role: str = Field(..., description="New role to assign: rider|host")
    # In a simple model, only rider<->host is allowed by user; admin remains server-managed.


# PUBLIC_INTERFACE
@router.get("/me", summary="Get my user summary", response_model=UserSummary)
def me(user=Depends(get_current_user)):
    """Return a simple user summary for the authenticated user."""
    return UserSummary(user_id=str(user.get("sub")), email=user.get("email"))


# PUBLIC_INTERFACE
@router.get("/profile", summary="Get my full profile", response_model=UserProfile)
def get_profile(user=Depends(get_current_user)):
    """Fetch a user's profile from Supabase table user_profiles; create default if missing."""
    sb = get_supabase_client()
    uid = str(user.get("sub"))
    email = user.get("email")
    # Try to fetch profile
    res = sb.table("user_profiles").select("*").eq("user_id", uid).limit(1).execute()
    if res.data and len(res.data) > 0:
        row = res.data[0]
    else:
        # Create default profile if not exists
        default_role = user.get("role") or "rider"
        insert_res = sb.table("user_profiles").insert(
            {"user_id": uid, "email": email, "display_name": None, "role": default_role}
        ).execute()
        row = insert_res.data[0] if insert_res.data else {"user_id": uid, "email": email, "display_name": None, "role": default_role}

    return UserProfile(
        user_id=row.get("user_id", uid),
        email=row.get("email", email),
        display_name=row.get("display_name"),
        role=row.get("role", user.get("role") or "rider"),
    )


# PUBLIC_INTERFACE
@router.post("/profile/sync", summary="Sync my profile from app to backend", response_model=UserProfile)
def sync_profile(payload: ProfileSyncRequest, user=Depends(get_current_user)):
    """Upsert user's profile with provided fields. Preserves server-managed fields."""
    sb = get_supabase_client()
    uid = str(user.get("sub"))
    email = user.get("email")

    updates: dict = {"user_id": uid}
    if payload.display_name is not None:
        updates["display_name"] = payload.display_name

    # Only allow role change to 'host' or 'rider' by the user themselves; 'admin' disallowed here
    if payload.role is not None:
        if payload.role not in ("rider", "host"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
        updates["role"] = payload.role

    # Upsert based on user_id unique key
    res = sb.table("user_profiles").upsert(
        {**updates, "email": email},
        on_conflict="user_id",
    ).execute()

    row = res.data[0] if res.data else {"user_id": uid, "email": email, **updates}
    return UserProfile(
        user_id=row.get("user_id", uid),
        email=row.get("email", email),
        display_name=row.get("display_name"),
        role=row.get("role", user.get("role") or "rider"),
    )


# PUBLIC_INTERFACE
@router.post("/role", summary="Assign my role (rider|host)", response_model=UserProfile)
def assign_role(payload: RoleAssignRequest, user=Depends(get_current_user)):
    """Allow a user to switch between rider and host. Admin role cannot be self-assigned."""
    if payload.role not in ("rider", "host"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Role must be rider or host")

    sb = get_supabase_client()
    uid = str(user.get("sub"))
    email = user.get("email")

    res = sb.table("user_profiles").upsert(
        {"user_id": uid, "email": email, "role": payload.role},
        on_conflict="user_id",
    ).execute()

    row = res.data[0] if res.data else {"user_id": uid, "email": email, "role": payload.role}
    return UserProfile(
        user_id=row.get("user_id", uid),
        email=row.get("email", email),
        display_name=row.get("display_name"),
        role=row.get("role", payload.role),
    )
