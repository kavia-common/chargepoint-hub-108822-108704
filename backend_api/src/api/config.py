import os
from functools import lru_cache
from typing import List, Optional

from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()


class JwtSettings(BaseModel):
    """JWT security settings."""
    secret: str = Field(..., description="Long, random secret used for signing JWTs", alias="JWT_SECRET")
    algorithm: str = Field(default="HS256", description="JWT signing algorithm", alias="JWT_ALGORITHM")
    access_expires_minutes: int = Field(default=60, description="Access token lifetime in minutes", alias="JWT_ACCESS_TOKEN_EXPIRES_MINUTES")
    refresh_expires_days: int = Field(default=30, description="Refresh token lifetime in days", alias="JWT_REFRESH_TOKEN_EXPIRES_DAYS")


class SupabaseSettings(BaseModel):
    """Supabase configuration settings."""
    url: str = Field(..., description="Supabase project URL", alias="SUPABASE_URL")
    anon_key: Optional[str] = Field(default=None, description="Public anon key (rarely used server-side)", alias="SUPABASE_ANON_KEY")
    service_role_key: str = Field(..., description="Service role key with elevated privileges", alias="SUPABASE_SERVICE_ROLE_KEY")
    db_url: Optional[str] = Field(default=None, description="Postgres connection URL from Supabase", alias="SUPABASE_DB_URL")


class StripeSettings(BaseModel):
    """Stripe configuration settings."""
    secret_key: Optional[str] = Field(default=None, alias="STRIPE_SECRET_KEY")
    webhook_secret: Optional[str] = Field(default=None, alias="STRIPE_WEBHOOK_SECRET")
    currency: str = Field(default="usd", alias="STRIPE_CURRENCY")


class EmailSettings(BaseModel):
    """Email provider settings."""
    sendgrid_api_key: Optional[str] = Field(default=None, alias="SENDGRID_API_KEY")
    mail_from: Optional[str] = Field(default=None, alias="MAIL_FROM")
    mail_from_name: Optional[str] = Field(default=None, alias="MAIL_FROM_NAME")


class NotificationSettings(BaseModel):
    """Notification settings (FCM)."""
    fcm_server_key: Optional[str] = Field(default=None, alias="FCM_SERVER_KEY")
    fcm_default_topic: Optional[str] = Field(default=None, alias="FCM_DEFAULT_TOPIC")


class AppSettings(BaseModel):
    """Application-level settings loaded from environment variables."""
    env: str = Field(default="development", description="Environment name (development|staging|production)", alias="ENV")
    api_base_url: Optional[str] = Field(default=None, description="Public URL of the backend", alias="API_BASE_URL")
    port: int = Field(default=3001, description="Port the backend listens on", alias="PORT")
    log_level: str = Field(default="INFO", description="Log level", alias="LOG_LEVEL")

    # CORS
    allowed_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:3001",
            "http://localhost:3000",
            "http://10.0.2.2:3001",
            "http://127.0.0.1:3000",
        ],
        description="Allowed origins for CORS",
        alias="ALLOWED_ORIGINS",
    )

    # Nested configs
    jwt: JwtSettings = Field(default_factory=lambda: JwtSettings(
        JWT_SECRET=os.getenv("JWT_SECRET", "please-set-a-strong-secret"),
        JWT_ALGORITHM=os.getenv("JWT_ALGORITHM", "HS256"),
        JWT_ACCESS_TOKEN_EXPIRES_MINUTES=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_MINUTES", "60")),
        JWT_REFRESH_TOKEN_EXPIRES_DAYS=int(os.getenv("JWT_REFRESH_TOKEN_EXPIRES_DAYS", "30")),
    ))
    supabase: SupabaseSettings = Field(default_factory=lambda: SupabaseSettings(
        SUPABASE_URL=os.getenv("SUPABASE_URL", "") or "",
        SUPABASE_ANON_KEY=os.getenv("SUPABASE_ANON_KEY"),
        SUPABASE_SERVICE_ROLE_KEY=os.getenv("SUPABASE_SERVICE_ROLE_KEY", "") or "",
        SUPABASE_DB_URL=os.getenv("SUPABASE_DB_URL"),
    ))
    stripe: StripeSettings = Field(default_factory=lambda: StripeSettings(
        STRIPE_SECRET_KEY=os.getenv("STRIPE_SECRET_KEY"),
        STRIPE_WEBHOOK_SECRET=os.getenv("STRIPE_WEBHOOK_SECRET"),
        STRIPE_CURRENCY=os.getenv("STRIPE_CURRENCY", "usd"),
    ))
    email: EmailSettings = Field(default_factory=lambda: EmailSettings(
        SENDGRID_API_KEY=os.getenv("SENDGRID_API_KEY"),
        MAIL_FROM=os.getenv("MAIL_FROM"),
        MAIL_FROM_NAME=os.getenv("MAIL_FROM_NAME"),
    ))
    notifications: NotificationSettings = Field(default_factory=lambda: NotificationSettings(
        FCM_SERVER_KEY=os.getenv("FCM_SERVER_KEY"),
        FCM_DEFAULT_TOPIC=os.getenv("FCM_DEFAULT_TOPIC"),
    ))


# PUBLIC_INTERFACE
@lru_cache()
def get_settings() -> AppSettings:
    """Return cached application settings loaded from environment variables."""
    # Handle ALLOWED_ORIGINS as comma-separated
    raw_origins = os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3001,http://localhost:3000,http://10.0.2.2:3001,http://127.0.0.1:3000",
    )
    origins = [o.strip() for o in raw_origins.split(",") if o.strip()]
    settings = AppSettings(
        ENV=os.getenv("ENV", "development"),
        API_BASE_URL=os.getenv("API_BASE_URL"),
        PORT=int(os.getenv("PORT", "3001")),
        LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
        ALLOWED_ORIGINS=origins,
    )
    return settings
