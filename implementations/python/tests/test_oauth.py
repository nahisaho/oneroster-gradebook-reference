"""
Tests for OAuth 2.0 authentication endpoints.
"""


def test_token_endpoint_success(client):
    """Test successful token generation with valid credentials."""
    response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.readonly",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "Bearer"
    assert data["expires_in"] == 3600
    assert "roster-core.readonly" in data["scope"]


def test_token_endpoint_invalid_grant_type(client):
    """Test token endpoint with invalid grant type."""
    response = client.post(
        "/oauth/token",
        data={
            "grant_type": "password",
            "client_id": "test_client",
            "client_secret": "test_secret",
        },
    )

    assert response.status_code == 400


def test_token_endpoint_invalid_credentials(client):
    """Test token endpoint with invalid client credentials."""
    response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "invalid_client",
            "client_secret": "invalid_secret",
        },
    )

    assert response.status_code == 401


def test_token_endpoint_invalid_scope(client):
    """Test token endpoint with invalid scope."""
    response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "scope": "invalid.scope",
        },
    )

    assert response.status_code == 400


def test_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/ims/oneroster/v1p2/categories")

    # Should return 403 Forbidden (not authenticated)
    assert response.status_code == 403
    data = response.json()
    assert data["imsx_codeMajor"] == "failure"
    assert "authenticated" in data["imsx_description"].lower()


def test_protected_endpoint_with_invalid_token(client):
    """Test accessing protected endpoint with invalid token."""
    response = client.get(
        "/ims/oneroster/v1p2/categories",
        headers={"Authorization": "Bearer invalid_token"},
    )

    assert response.status_code == 401


def test_protected_endpoint_with_valid_token(client, oauth_token):
    """Test accessing protected endpoint with valid token."""
    response = client.get(
        "/ims/oneroster/v1p2/categories",
        headers={"Authorization": f"Bearer {oauth_token}"},
    )

    assert response.status_code == 200


def test_token_endpoint_missing_parameters(client):
    """Test token endpoint with missing required parameters."""
    response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            # Missing client_id and client_secret
        },
    )
    
    # FastAPI returns 422 for missing form fields
    assert response.status_code == 422
def test_protected_endpoint_without_bearer_prefix(client, oauth_token):
    """Test accessing protected endpoint without Bearer prefix."""
    response = client.get(
        "/ims/oneroster/v1p2/categories",
        headers={"Authorization": oauth_token},  # Missing "Bearer " prefix
    )
    
    # Implementation returns 403 when token format is invalid
    assert response.status_code == 403
def test_protected_endpoint_with_expired_scope(client):
    """Test accessing endpoint with token that has wrong scope."""
    # Get token with readonly scope
    token_response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "test_client",
            "client_secret": "test_secret",
            "scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.readonly",
        },
    )
    token = token_response.json()["access_token"]

    # Try to use createput endpoint with readonly token
    response = client.post(
        "/ims/oneroster/v1p2/categories",
        headers={"Authorization": f"Bearer {token}"},
        json={"sourcedId": "test", "title": "Test", "weight": 0.5},
    )

    assert response.status_code == 403


def test_protected_endpoint_with_invalid_jwt(client):
    """Test accessing protected endpoint with malformed JWT token."""
    # Use a clearly invalid token
    response = client.get(
        "/ims/oneroster/v1p2/categories",
        headers={"Authorization": "Bearer invalid.jwt.token"},
    )

    assert response.status_code == 401


def test_protected_endpoint_with_no_sub_claim(client):
    """Test token without sub claim."""
    from datetime import datetime, timedelta

    import jose.jwt as jwt

    # Create token without 'sub' claim
    payload = {
        "scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.readonly",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, "test_secret", algorithm="HS256")

    response = client.get(
        "/ims/oneroster/v1p2/categories",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401


def test_token_endpoint_with_invalid_client_secret(client):
    """Test token endpoint with wrong client secret."""
    response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "test_client",
            "client_secret": "wrong_secret",
            "scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.readonly",
        },
    )

    assert response.status_code == 401


def test_protected_endpoint_with_revoked_token(client, oauth_token):
    """Test accessing endpoint with token not in storage."""
    # Use a valid JWT but not in token storage
    from datetime import datetime, timedelta

    import jose.jwt as jwt

    payload = {
        "sub": "test_client",
        "scope": "https://purl.imsglobal.org/spec/or/v1p2/scope/roster-core.readonly",
        "exp": datetime.utcnow() + timedelta(hours=1),
        "iat": datetime.utcnow(),
    }
    # Use same secret but this token won't be in storage
    token = jwt.encode(payload, "your-secret-key-change-in-production", algorithm="HS256")

    response = client.get(
        "/ims/oneroster/v1p2/categories",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
