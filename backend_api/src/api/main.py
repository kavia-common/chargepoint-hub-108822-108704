from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import get_settings
from .routers import auth as auth_router
from .routers import users as users_router
from .routers import chargers as chargers_router
from .routers import bookings as bookings_router
from .routers import payments as payments_router
from .routers import notifications as notifications_router

settings = get_settings()

openapi_tags = [
    {"name": "Health", "description": "Service health and diagnostics"},
    {"name": "Auth", "description": "Authentication and user identity"},
    {"name": "Users", "description": "User profile and management"},
    {"name": "Chargers", "description": "Charger directory and details"},
    {"name": "Bookings", "description": "Booking creation and management"},
    {"name": "Payments", "description": "Payment intents and webhooks"},
    {"name": "Notifications", "description": "Push notifications and subscriptions"},
]

# Configure FastAPI app with metadata for OpenAPI
app = FastAPI(
    title="ChargeMate Backend API",
    description="Backend services for authentication, bookings, payments, notifications, and maps.",
    version="0.1.0",
    contact={"name": "ChargeMate Dev Team"},
    openapi_tags=openapi_tags,
)

# Load CORS origins from environment
allow_origins: List[str] = settings.allowed_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# PUBLIC_INTERFACE
@app.get("/", summary="Health Check", tags=["Health"])
def health_check():
    """Simple health check endpoint.

    Returns:
        dict: A message indicating the service is healthy.
    """
    return {"message": "Healthy"}


# PUBLIC_INTERFACE
@app.get("/websocket-usage", summary="WebSocket usage help", tags=["Health"])
def websocket_usage():
    """Provides instructions and usage notes for real-time WebSocket endpoints (future).

    Returns:
        dict: Usage information for connecting to any WebSocket endpoints.
    """
    return {
        "note": "WebSocket endpoints will be documented here when available.",
        "status": "planned",
    }


# Include routers
app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(chargers_router.router)
app.include_router(bookings_router.router)
app.include_router(payments_router.router)
app.include_router(notifications_router.router)
