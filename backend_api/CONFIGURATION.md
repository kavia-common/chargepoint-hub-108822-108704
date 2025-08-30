ChargeMate Backend API Configuration

This document lists and explains all environment variables required by the FastAPI backend. Copy .env.example to .env and set values before running.

Core
- API_BASE_URL: Public URL of the backend (e.g., http://localhost:3001).
- ALLOWED_ORIGINS: Comma-separated list of allowed origins for CORS.
- ENV: Environment name (development|staging|production).
- PORT: Port the backend listens on.

Security
- JWT_SECRET: Long, random secret used for signing JWTs.
- JWT_ALGORITHM: JWT signing algorithm (default HS256).
- JWT_ACCESS_TOKEN_EXPIRES_MINUTES: Access token lifetime in minutes.
- JWT_REFRESH_TOKEN_EXPIRES_DAYS: Refresh token lifetime in days.

Supabase
- SUPABASE_URL: Supabase project URL.
- SUPABASE_ANON_KEY: Public anon key for client interactions (rarely used server-side).
- SUPABASE_SERVICE_ROLE_KEY: Service role key with elevated privileges (server-side only).
- SUPABASE_DB_URL: Postgres connection URL from Supabase.

Database
- POSTGRES_URL / POSTGRES_USER / POSTGRES_PASSWORD / POSTGRES_DB / POSTGRES_PORT:
  Direct DB connection (optional if using SUPABASE_DB_URL).

Stripe
- STRIPE_SECRET_KEY: Server-side secret key.
- STRIPE_WEBHOOK_SECRET: Webhook signing secret for validating Stripe webhooks.
- STRIPE_CURRENCY: Default currency (e.g., usd, eur).

Notifications (FCM)
- FCM_SERVER_KEY: Firebase Cloud Messaging server key for sending push notifications.
- FCM_DEFAULT_TOPIC: Optional default topic for broadcast messages.

Maps
- MAPS_API_KEY: Google Maps API key for server-side geocoding or validation.

Email (optional)
- SENDGRID_API_KEY: If using SendGrid.
- MAIL_FROM: Default sender email.
- MAIL_FROM_NAME: Default sender name.

Logging
- LOG_LEVEL: DEBUG, INFO, WARNING, ERROR.

Notes
- Never commit real secrets.
- For Docker/K8s, map these as environment variables via your orchestrator.
- Ensure ALLOWED_ORIGINS includes your mobile dev emulator origins (e.g., http://10.0.2.2:3000).
