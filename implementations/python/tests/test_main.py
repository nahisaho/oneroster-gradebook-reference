"""Tests for main application endpoints."""


def test_root_endpoint(client):
    """Test root endpoint returns API information."""
    response = client.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "specification" in data
    assert data["specification"] == "IMS Global OneRoster v1.2"
    assert "endpoints" in data


def test_health_endpoint(client):
    """Test health check endpoint."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "timestamp" in data
    assert "environment" in data


def test_token_endpoint_with_default_scope(client):
    """Test token endpoint uses default scope when none specified."""
    response = client.post(
        "/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": "test_client",
            "client_secret": "test_secret",
            # No scope specified - should use default
        },
    )
    
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "scope" in data
    # Should have default scopes
    assert "roster-core.readonly" in data["scope"]
