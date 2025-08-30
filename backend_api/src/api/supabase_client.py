from typing import Optional

from supabase import create_client, Client  # type: ignore

from .config import get_settings

_supabase_client: Optional[Client] = None


def _init_client() -> Client:
    """Initialize the Supabase client using service role key."""
    settings = get_settings()
    url = settings.supabase.url
    key = settings.supabase.service_role_key
    if not url or not key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in the environment.")
    return create_client(url, key)


# PUBLIC_INTERFACE
def get_supabase_client() -> Client:
    """Get a singleton Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = _init_client()
    return _supabase_client
