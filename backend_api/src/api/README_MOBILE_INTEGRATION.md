Mobile integration (Flutter supabase_flutter) - JWT forwarding

- After signIn/signUp, get session: final session = supabase.auth.currentSession;
- Extract token: final jwt = session?.accessToken;
- Call backend with header:
  Authorization: Bearer <jwt>

Example (Dart):
final jwt = supabase.auth.currentSession?.accessToken;
final resp = await http.get(
  Uri.parse('$API_BASE_URL/auth/validate-session'),
  headers: {'Authorization': 'Bearer $jwt'},
);

On app launch, call GET /users/profile to fetch or initialize profile. Use POST /users/role to switch between rider/host. Do not allow 'admin' from client.

Maps and charger discovery
- See README_MAPS_INTEGRATION.md in this folder for Google Maps integration and clustering notes.
- Backend endpoint: GET /chargers supports center/radius and viewport bounding box filters suitable for map panes.
- Always pass Authorization header to access protected endpoints.

Ensure your app .env has:
- SUPABASE_URL
- SUPABASE_ANON_KEY
- SITE_URL (used for email redirect links if applicable)
