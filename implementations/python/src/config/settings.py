"""
Configuration module for OneRoster Gradebook Service.
Loads settings from environment variables.
"""

from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Application Settings
    app_name: str = "OneRoster Gradebook Service"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"

    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000

    # Database Settings
    database_url: str | None = None  # Override with DATABASE_URL env var
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "oneroster_gradebook"
    db_user: str = "postgres"
    db_password: str = "postgres"
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # OAuth 2.0 Settings
    oauth_client_id: str
    oauth_client_secret: str
    oauth_token_lifetime: int = 3600
    oauth_client_scopes: str

    # API Settings
    api_base_url: str = "http://localhost:8000"
    rostering_service_base_url: str = "http://localhost:8000"

    # CORS Settings
    cors_origins: str = "*"
    cors_allow_credentials: bool = True
    cors_allow_methods: str = "GET,POST,PUT,DELETE,OPTIONS"
    cors_allow_headers: str = "*"

    # Rate Limiting
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 100

    # Logging
    log_level: str = "INFO"
    log_format: str = "json"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    def get_database_url(self) -> str:
        """Get database URL from DATABASE_URL env var or construct from settings."""
        if self.database_url:
            return self.database_url
        return (
            f"postgresql://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        if self.cors_origins == "*":
            return ["*"]
        return [origin.strip() for origin in self.cors_origins.split(",")]

    @property
    def cors_methods_list(self) -> List[str]:
        """Parse CORS methods from comma-separated string."""
        return [method.strip() for method in self.cors_allow_methods.split(",")]

    @property
    def oauth_scopes_list(self) -> List[str]:
        """Parse OAuth scopes from comma-separated string."""
        return [scope.strip() for scope in self.oauth_client_scopes.split(",")]


# Global settings instance
settings = Settings()
