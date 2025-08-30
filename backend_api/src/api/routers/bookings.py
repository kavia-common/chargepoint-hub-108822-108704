from fastapi import APIRouter, Depends

from ..auth import get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings"])


# PUBLIC_INTERFACE
@router.get("/", summary="List my bookings (placeholder)")
def list_my_bookings(user=Depends(get_current_user)):
    """Placeholder endpoint for listing bookings of the authenticated user."""
    return {"items": [], "total": 0, "user": str(user.get("sub"))}
