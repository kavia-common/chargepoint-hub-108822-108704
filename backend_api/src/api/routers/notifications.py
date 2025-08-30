from fastapi import APIRouter

router = APIRouter(prefix="/notifications", tags=["Notifications"])


# PUBLIC_INTERFACE
@router.get("/health", summary="Notifications health (placeholder)")
def notifications_health():
    """Placeholder health endpoint for notifications router."""
    return {"status": "ok"}
