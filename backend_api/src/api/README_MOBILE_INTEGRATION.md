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

Ensure your app .env has:
- SUPABASE_URL
- SUPABASE_ANON_KEY
- SITE_URL (used for email redirect links if applicable)
