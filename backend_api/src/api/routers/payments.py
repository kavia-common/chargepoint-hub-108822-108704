from fastapi import APIRouter

router = APIRouter(prefix="/payments", tags=["Payments"])


# PUBLIC_INTERFACE
@router.get("/health", summary="Payments health (placeholder)")
def payments_health():
    """Placeholder health endpoint for payments router."""
    return {"status": "ok"}
