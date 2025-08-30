from fastapi import APIRouter

router = APIRouter(prefix="/chargers", tags=["Chargers"])


# PUBLIC_INTERFACE
@router.get("/", summary="List chargers (placeholder)")
def list_chargers():
    """Placeholder endpoint for listing chargers."""
    return {"items": [], "total": 0}
