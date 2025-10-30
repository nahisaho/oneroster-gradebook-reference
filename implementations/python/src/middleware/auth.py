"""
OAuth 2.0 Client Credentials Grant implementation.
"""

import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from src.config.settings import settings

# In-memory storage (replace with database in production)
tokens: Dict[str, Dict] = {}
clients: Dict[str, Dict] = {}

# JWT Configuration
SECRET_KEY = secrets.token_urlsafe(32)
ALGORITHM = "HS256"

# HTTP Bearer scheme
security = HTTPBearer()


def load_clients() -> None:
    """Load OAuth clients from settings."""
    client_id = settings.oauth_client_id
    client_secret = settings.oauth_client_secret
    scopes = settings.oauth_scopes_list

    if client_id and client_secret:
        clients[client_id] = {
            "client_id": client_id,
            "client_secret": client_secret,
            "grants": ["client_credentials"],
            "scopes": scopes,
        }


# Load clients on module import
load_clients()


def verify_client(client_id: str, client_secret: str) -> Optional[Dict]:
    """
    Verify client credentials.

    Args:
        client_id: OAuth client ID
        client_secret: OAuth client secret

    Returns:
        Client dict if valid, None otherwise
    """
    client = clients.get(client_id)
    if not client:
        return None
    if client["client_secret"] != client_secret:
        return None
    return client


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create JWT access token.

    Args:
        data: Data to encode in token
        expires_delta: Token expiration time

    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(seconds=settings.oauth_token_lifetime)

    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def save_token(token: str, client_id: str, scope: str, expires_at: datetime) -> Dict:
    """
    Save token to storage.

    Args:
        token: Access token
        client_id: OAuth client ID
        scope: Token scope
        expires_at: Token expiration datetime

    Returns:
        Token data dict
    """
    token_data = {
        "access_token": token,
        "client_id": client_id,
        "scope": scope,
        "expires_at": expires_at,
    }
    tokens[token] = token_data
    return token_data


def verify_token(token: str) -> Optional[Dict]:
    """
    Verify and decode access token.

    Args:
        token: JWT access token

    Returns:
        Decoded token data if valid, None otherwise
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        client_id: str = payload.get("sub")
        if client_id is None:
            return None

        # Check if token is still in storage
        if token not in tokens:
            return None

        return {
            "client_id": client_id,
            "scope": payload.get("scope"),
            "exp": payload.get("exp"),
        }
    except JWTError:
        return None


async def get_current_client(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict:
    """
    Dependency to get current authenticated client.

    Args:
        credentials: HTTP Bearer token credentials

    Returns:
        Client data dict

    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    token_data = verify_token(token)

    if token_data is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return token_data


def require_scope(required_scope: str):
    """
    Dependency factory to require specific OAuth scope.

    Args:
        required_scope: Required OAuth scope

    Returns:
        Dependency function
    """

    async def scope_checker(client: Dict = Depends(get_current_client)) -> Dict:
        scopes = client.get("scope", "").split()
        if required_scope not in scopes:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient scope. Required: {required_scope}",
            )
        return client

    return scope_checker
