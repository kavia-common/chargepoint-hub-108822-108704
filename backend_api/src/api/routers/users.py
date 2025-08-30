from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from ..auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


class UserSummary(BaseModel):
    user_id: str = Field(..., description="User ID")
    email: str | None = Field(default=None, description="User email")


# PUBLIC_INTERFACE
@router.get("/me", summary="Get my user summary", response_model=UserSummary)
def me(user=Depends(get_current_user)):
    """Return a simple user summary for the authenticated user."""
    return UserSummary(user_id=str(user.get("sub")), email=user.get("email"))
