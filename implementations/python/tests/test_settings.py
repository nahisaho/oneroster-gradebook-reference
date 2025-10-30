"""Tests for settings configuration."""
from unittest.mock import patch
import os


def test_settings_database_url_fallback():
    """Test database URL fallback when DATABASE_URL is not set."""
    from src.config.settings import Settings
    
    # Create settings without DATABASE_URL
    settings = Settings(
        database_url=None,
        db_user="testuser",
        db_password="testpass",
        db_host="testhost",
        db_port=5432,
        db_name="testdb"
    )
    url = settings.get_database_url()
    assert "testuser" in url
    assert "testpass" in url
    assert "testhost" in url
    assert "testdb" in url


def test_settings_cors_origins_wildcard():
    """Test CORS origins with wildcard."""
    from src.config.settings import Settings
    
    with patch.dict(os.environ, {"CORS_ORIGINS": "*"}, clear=False):
        settings = Settings()
        origins = settings.cors_origins_list
        assert origins == ["*"]


def test_settings_cors_origins_multiple():
    """Test CORS origins with multiple values."""
    from src.config.settings import Settings
    
    with patch.dict(os.environ, {
        "CORS_ORIGINS": "http://localhost:3000,https://example.com"
    }, clear=False):
        settings = Settings()
        origins = settings.cors_origins_list
        assert len(origins) == 2
        assert "http://localhost:3000" in origins
        assert "https://example.com" in origins
