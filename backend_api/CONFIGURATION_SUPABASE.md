ChargeMate Supabase Auth Integration Notes

Tables (create in Supabase SQL editor)
- public.user_profiles
  - user_id text primary key
  - email text
  - display_name text null
  - role text not null default 'rider' check (role in ('rider','host','admin'))

Auth/JWT
- Mobile app authenticates via Supabase (email/password, magic link, or Google).
- Mobile retrieves session access_token and forwards it to this backend via Authorization: Bearer <access_token>.
- Backend validates token using configured JWT settings (see CONFIGURATION.md -> JWT_*). For production, set JWT_SECRET to your Supabase project's JWT secret.

Endpoints
- GET /auth/validate-session: Validates JWT and returns { valid, user_id, email, role }.
- GET /users/profile: Returns profile from user_profiles (auto-creates default).
- POST /users/profile/sync: Upserts display_name and optionally role (rider|host).
- POST /users/role: Self-assign role rider|host (admin reserved).

Env Vars Required
- SUPABASE_URL
- SUPABASE_SERVICE_ROLE_KEY
- JWT_SECRET (set to Supabase JWT secret)
