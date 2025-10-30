"""
OneRoster Gradebook Service - FastAPI Application
Main application entry point.
"""

from datetime import datetime, timedelta

from fastapi import FastAPI, Form, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from src.config.settings import settings
from src.middleware.auth import create_access_token, save_token, verify_client
from src.routers import categories, line_items, results

# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="IMS Global OneRoster v1.2 Gradebook Service Reference Implementation",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_methods_list,
    allow_headers=["*"],
)

# Configure rate limiting
limiter = Limiter(key_func=get_remote_address)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


@app.get("/")
async def root():
    """API information endpoint."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "specification": "IMS Global OneRoster v1.2",
        "description": "Reference implementation of OneRoster Gradebook Service",
        "endpoints": {
            "token": "/oauth/token",
            "categories": "/ims/oneroster/v1p2/categories",
            "lineItems": "/ims/oneroster/v1p2/lineItems",
            "results": "/ims/oneroster/v1p2/results",
            "students": "/ims/oneroster/v1p2/students",
        },
        "documentation": "https://www.imsglobal.org/spec/oneroster/v1p2",
    }


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {
        "status": "ok",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "environment": settings.environment,
    }


@app.post("/oauth/token")
@limiter.limit(f"{settings.rate_limit_per_minute}/minute")
async def token(
    request: Request,
    grant_type: str = Form(...),
    client_id: str = Form(...),
    client_secret: str = Form(...),
    scope: str = Form(None),
):
    """
    OAuth 2.0 Token Endpoint
    Implements Client Credentials Grant.
    """
    # Validate grant type
    if grant_type != "client_credentials":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "unsupported_grant_type",
                "error_description": "Only client_credentials grant type is supported",
            },
        )

    # Verify client credentials
    client = verify_client(client_id, client_secret)
    if not client:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_client",
                "error_description": "Invalid client credentials",
            },
        )

    # Validate requested scope
    requested_scopes = scope.split() if scope else []
    client_scopes = client["scopes"]

    # Check if all requested scopes are allowed
    if requested_scopes:
        for requested_scope in requested_scopes:
            if requested_scope not in client_scopes:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": "invalid_scope",
                        "error_description": f"Scope '{requested_scope}' is not allowed for this client",
                    },
                )
        granted_scope = " ".join(requested_scopes)
    else:
        # Use default scope if none requested
        granted_scope = " ".join(client_scopes)

    # Create access token
    token_data = {
        "sub": client_id,
        "scope": granted_scope,
    }
    expires_delta = timedelta(seconds=settings.oauth_token_lifetime)
    access_token = create_access_token(token_data, expires_delta)

    # Save token
    expires_at = datetime.utcnow() + expires_delta
    save_token(access_token, client_id, granted_scope, expires_at)

    return {
        "access_token": access_token,
        "token_type": "Bearer",
        "expires_in": settings.oauth_token_lifetime,
        "scope": granted_scope,
    }


# Include routers
API_BASE = "/ims/oneroster/v1p2"
app.include_router(categories.router, prefix=f"{API_BASE}/categories", tags=["Categories"])
app.include_router(line_items.router, prefix=f"{API_BASE}/lineItems", tags=["Line Items"])
app.include_router(results.router, prefix=f"{API_BASE}/results", tags=["Results"])


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Convert HTTP exceptions to OneRoster error format."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "imsx_codeMajor": "failure",
            "imsx_severity": "error",
            "imsx_description": str(exc.detail),
            "imsx_codeMinor": "server_error",
        },
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "imsx_codeMajor": "failure",
            "imsx_severity": "error",
            "imsx_description": "An unexpected error occurred",
            "imsx_codeMinor": "internal_server_error",
        },
    )
