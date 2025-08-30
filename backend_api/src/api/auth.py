from typing import Optional, Dict, Any

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError  # type: ignore

from .config import get_settings

security = HTTPBearer(auto_error=False)


def _decode_jwt(token: str) -> Dict[str, Any]:
    """Decode a JWT using configured algorithm and secret.

    Note:
        - For Supabase Auth JWT verification in production, you typically verify with the
          JWT secret (from Supabase project settings) or JWKs/Public Key if using GoTrue with
          external providers. Here we use HS256 + configured secret to allow future adaptation.
    """
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt.secret, algorithms=[settings.jwt.algorithm])
        return payload  # contains 'sub', 'email', 'role', etc. depending on issuer
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        ) from e


# PUBLIC_INTERFACE
def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """Authentication dependency to validate Bearer JWT and return user claims.

    Parameters:
        credentials: Extracted Authorization header credentials via HTTPBearer.

    Returns:
        dict: The decoded JWT claims representing the authenticated user.

    Raises:
        HTTPException(401): If the Authorization header is missing or token is invalid.
    """
    if credentials is None or not credentials.scheme.lower() == "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header missing or not using Bearer scheme",
        )

    token = credentials.credentials
    claims = _decode_jwt(token)
    # Ensure a subject is present
    if "sub" not in claims:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
        )
    return claims
