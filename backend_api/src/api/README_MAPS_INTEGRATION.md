Mobile map integration guide (Google Maps + clustering)

Overview
- The backend exposes /chargers with geospatial filters suitable for Google Maps or Apple Maps.
- Use either center + radius (preferred for "search this area" flows) or a viewport bounding box.
- Results include charger + parent location fields (coordinates on location).

Endpoints
- GET /chargers
  Query parameters:
  - page (int, default 0)
  - page_size (int, default 50, max 200)
  - center_lat, center_lng, radius_km (float): search around a center within a radius
  - OR ne_lat, ne_lng, sw_lat, sw_lng (float): bounding box filter
  - connector (string): comma-separated connector types: type1,type2,ccs,chademo,gb_t,tesla
  - min_power_kw (float)
  - max_price_per_kwh (float)
  - only_available (bool)

Response shape
{
  "items": [
    {
      "id": "charger-uuid",
      "name": "Charger A",
      "connector": "ccs",
      "power_kw": 50.0,
      "price_per_kwh": 0.25,
      "currency": "USD",
      "is_available": true,
      "status": "active",
      "location": {
        "id": "location-uuid",
        "name": "Garage 101",
        "latitude": 37.78,
        "longitude": -122.41,
        "is_public": true,
        "status": "active"
      }
    }
  ],
  "total": 123,
  "page": 0,
  "page_size": 50
}

Flutter integration (pseudo)
- Use google_maps_flutter and a marker clustering plugin (e.g., supercluster_dart on the data, or a platform-specific cluster manager).
- On camera idle:
  1. Get camera target and zoom; compute radius_km from visible region or use bounding box parameters.
  2. Call backend:
     final resp = await http.get(Uri.parse('$API_BASE_URL/chargers?center_lat=$lat&center_lng=$lng&radius_km=$r'),
       headers: {'Authorization': 'Bearer ${supabase.auth.currentSession?.accessToken}'});
  3. Convert items into markers using item.location.latitude/longitude.
  4. Apply clustering offline on-device for performance; the payload is paginated (default 50).

Clustering suggestions
- At zoom <= 12, query larger radius_km (e.g., 10–25 km) and cluster on-device.
- At zoom > 15, reduce radius to show individual pins.
- For very dense regions, prefer viewport-based (ne/sw) queries tied to the visible region to minimize network payload.

Caching & pagination
- Cache last response keyed by tile/zoom to avoid flicker.
- Use page/page_size to fetch more when needed (e.g., if total > items.length).

Notes
- For production, consider implementing server-side clustering (e.g., via PostGIS ST_ClusterWithin) behind a dedicated endpoint. Current implementation prepares for this by cleanly separating location and charger data.
- If PostGIS is available, a future enhancement can add precise radius filtering by ST_DWithin(geom, center, meters) while retaining the same API.
