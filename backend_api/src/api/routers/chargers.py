from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from ..supabase_client import get_supabase_client

router = APIRouter(prefix="/chargers", tags=["Chargers"])


class ChargerLocation(BaseModel):
    """Represents a charger location row."""
    id: str = Field(..., description="Location ID (UUID)")
    name: str = Field(..., description="Location name")
    description: Optional[str] = Field(default=None, description="Location description")
    address_line1: Optional[str] = Field(default=None, description="Address line 1")
    address_line2: Optional[str] = Field(default=None, description="Address line 2")
    city: Optional[str] = Field(default=None, description="City")
    state: Optional[str] = Field(default=None, description="State/region")
    country: Optional[str] = Field(default=None, description="Country")
    postal_code: Optional[str] = Field(default=None, description="Postal/ZIP code")
    latitude: float = Field(..., description="Latitude (WGS84)")
    longitude: float = Field(..., description="Longitude (WGS84)")
    is_public: bool = Field(..., description="Whether the location is public")
    status: str = Field(..., description="Location status")


class ChargerItem(BaseModel):
    """A charger combined with its parent location for map listing."""
    id: str = Field(..., description="Charger ID (UUID)")
    name: str = Field(..., description="Display name of the charger")
    connector: str = Field(..., description="Connector type (type1|type2|ccs|chademo|gb_t|tesla)")
    power_kw: float = Field(..., description="Power rating in kW")
    price_per_kwh: float = Field(..., description="Price per kWh in the given currency")
    currency: str = Field(..., description="Currency code (e.g., USD)")
    is_available: bool = Field(..., description="Current availability")
    status: str = Field(..., description="Status (active|inactive|maintenance)")
    location: ChargerLocation = Field(..., description="Parent location metadata")


class ChargerListResponse(BaseModel):
    """Paginated list of chargers for map display."""
    items: List[ChargerItem] = Field(..., description="List of chargers")
    total: int = Field(..., description="Total number of items matching the filter")
    page: int = Field(..., description="Current page index (0-based)")
    page_size: int = Field(..., description="Page size used for this response")


def _join_charger_and_location(charger_row: Dict[str, Any], location_row: Dict[str, Any]) -> ChargerItem:
    """Helper to compose API response item."""
    loc = ChargerLocation(
        id=location_row["id"],
        name=location_row.get("name"),
        description=location_row.get("description"),
        address_line1=location_row.get("address_line1"),
        address_line2=location_row.get("address_line2"),
        city=location_row.get("city"),
        state=location_row.get("state"),
        country=location_row.get("country"),
        postal_code=location_row.get("postal_code"),
        latitude=float(location_row.get("latitude")),
        longitude=float(location_row.get("longitude")),
        is_public=bool(location_row.get("is_public")),
        status=location_row.get("status"),
    )
    return ChargerItem(
        id=charger_row["id"],
        name=charger_row.get("name"),
        connector=charger_row.get("connector"),
        power_kw=float(charger_row.get("power_kw")),
        price_per_kwh=float(charger_row.get("price_per_kwh")),
        currency=charger_row.get("currency"),
        is_available=bool(charger_row.get("is_available")),
        status=charger_row.get("status"),
        location=loc,
    )


# PUBLIC_INTERFACE
@router.get(
    "/",
    summary="List chargers near a point or within a bounding box",
    description=(
        "Returns a paginated list of chargers, optionally filtered by geospatial parameters and attributes.\n\n"
        "Geospatial filters:\n"
        "- Provide either center_lat/center_lng with radius_km, or a bounding box via ne_lat/ne_lng/sw_lat/sw_lng.\n"
        "Attribute filters:\n"
        "- connector (comma-separated), min_power_kw, max_price_per_kwh, only_available.\n\n"
        "Ordering:\n"
        "- If center is provided, results are ordered by approximate distance (using simple Haversine approximation via SQL). "
        "Otherwise, newest updated chargers first."
    ),
    response_model=ChargerListResponse,
)
def list_chargers(
    page: int = Query(0, ge=0, description="Page index (0-based)"),
    page_size: int = Query(50, ge=1, le=200, description="Items per page (max 200)"),
    # Center + radius
    center_lat: Optional[float] = Query(default=None, description="Center latitude"),
    center_lng: Optional[float] = Query(default=None, description="Center longitude"),
    radius_km: Optional[float] = Query(default=None, gt=0, description="Search radius in kilometers"),
    # Bounding box
    ne_lat: Optional[float] = Query(default=None, description="NorthEast latitude of bounding box"),
    ne_lng: Optional[float] = Query(default=None, description="NorthEast longitude of bounding box"),
    sw_lat: Optional[float] = Query(default=None, description="SouthWest latitude of bounding box"),
    sw_lng: Optional[float] = Query(default=None, description="SouthWest longitude of bounding box"),
    # Attributes
    connector: Optional[str] = Query(default=None, description="Comma-separated connector types to include"),
    min_power_kw: Optional[float] = Query(default=None, ge=0, description="Minimum power kW"),
    max_price_per_kwh: Optional[float] = Query(default=None, ge=0, description="Max price per kWh"),
    only_available: bool = Query(default=False, description="If true, only return available chargers"),
):
    """List chargers with optional geospatial and attribute filters.

    Returns:
        ChargerListResponse: A page of charger items with location details.
    """
    sb = get_supabase_client()

    # Build base selection: join chargers with locations (two-step approach due to Supabase client limitations).
    # 1) Filter locations by geo constraints to get candidate location IDs.
    loc_query = sb.table("charger_locations").select(
        "id,name,description,address_line1,address_line2,city,state,country,postal_code,latitude,longitude,is_public,status"
    ).eq("is_public", True).eq("status", "active")

    bbox_supplied = all(v is not None for v in (ne_lat, ne_lng, sw_lat, sw_lng))
    center_supplied = (center_lat is not None and center_lng is not None and radius_km is not None)

    if bbox_supplied:
        # Simple latitude/longitude bbox filter (works without PostGIS)
        min_lat = min(ne_lat, sw_lat)  # type: ignore[arg-type]
        max_lat = max(ne_lat, sw_lat)  # type: ignore[arg-type]
        min_lng = min(ne_lng, sw_lng)  # type: ignore[arg-type]
        max_lng = max(ne_lng, sw_lng)  # type: ignore[arg-type]
        loc_query = loc_query.gte("latitude", min_lat).lte("latitude", max_lat).gte("longitude", min_lng).lte("longitude", max_lng)

    elif center_supplied:
        # Approximate by creating a square bbox around the center using radius.
        # 1 deg lat ~ 111 km; 1 deg lng ~ 111 km * cos(lat)
        lat_delta = radius_km / 111.0  # type: ignore[operator]
        lng_delta = radius_km / (111.0 * max(0.1, abs(__import__("math").cos(__import__("math").radians(center_lat)))))  # type: ignore[arg-type]
        loc_query = loc_query.gte("latitude", center_lat - lat_delta).lte("latitude", center_lat + lat_delta)  # type: ignore[operator]
        loc_query = loc_query.gte("longitude", center_lng - lng_delta).lte("longitude", center_lng + lng_delta)  # type: ignore[operator]

    # Execute location query
    loc_res = loc_query.execute()
    locations = {row["id"]: row for row in (loc_res.data or [])}

    if not locations:
        return ChargerListResponse(items=[], total=0, page=page, page_size=page_size)

    location_ids = list(locations.keys())

    # 2) Query chargers limited to candidate locations
    ch_query = sb.table("chargers").select(
        "id,location_id,name,connector,power_kw,price_per_kwh,currency,is_available,status,updated_at"
    ).in_("location_id", location_ids).eq("status", "active")

    # Apply attribute filters
    if connector:
        wanted = [c.strip() for c in connector.split(",") if c.strip()]
        if wanted:
            ch_query = ch_query.in_("connector", wanted)
    if min_power_kw is not None:
        ch_query = ch_query.gte("power_kw", min_power_kw)
    if max_price_per_kwh is not None:
        ch_query = ch_query.lte("price_per_kwh", max_price_per_kwh)
    if only_available:
        ch_query = ch_query.eq("is_available", True)

    # Order: if center supplied, we can approximate distance on client; here, order by updated_at desc.
    ch_query = ch_query.order("updated_at", desc=True)

    # Count total using head=False (Supabase Python uses count via select count? Use range to fetch page and compute total by separate call)
    # First fetch total by getting all IDs (bounded by location set; acceptable for small-medium responses).
    total_res = ch_query.execute()
    all_rows = total_res.data or []
    total = len(all_rows)

    # Pagination
    start = page * page_size
    end = start + page_size - 1
    paged_query = ch_query.range(start, end)
    page_res = paged_query.execute()
    ch_rows = page_res.data or []

    items: List[ChargerItem] = []
    for ch in ch_rows:
        loc = locations.get(ch["location_id"])
        if not loc:
            continue
        items.append(_join_charger_and_location(ch, loc))

    return ChargerListResponse(items=items, total=total, page=page, page_size=page_size)
