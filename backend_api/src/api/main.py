import os
from typing import List

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


# Configure FastAPI app with metadata for OpenAPI
app = FastAPI(
    title="ChargeMate Backend API",
    description="Backend services for authentication, bookings, payments, notifications, and maps.",
    version="0.1.0",
    contact={"name": "ChargeMate Dev Team"},
)

# Load CORS origins from environment, fallback to common dev defaults
raw_origins = os.getenv(
    "ALLOWED_ORIGINS",
    "http://localhost:3001,http://localhost:3000,http://10.0.2.2:3001",
)
allow_origins: List[str] = [o.strip() for o in raw_origins.split(",") if o.strip()]

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
