from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Literal
import os


class BaseSettingsClass(BaseSettings):
    """Base configuration shared across all environments"""

    # App
    app_name: str = "Spotly API"
    app_env: Literal["development", "production", "staging"] = "production"
    debug: bool = False

    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    workers: int = 2
    log_level: str = "info"

    # MongoDB
    mongodb_url: str
    mongodb_db_name: str = "spotly"
    mongodb_max_connections: int = 100
    mongodb_min_connections: int = 10

    # Email (Resend)
    resend_api_key: str

    # Security
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    allowed_hosts: list[str] = [
        "spotly.work",
        "www.spotly.work",
        "localhost",
        "127.0.0.1",
    ]

    # CORS
    cors_origins: list[str] = [
        "https://spotly.work",
        "https://www.spotly.work",
    ]
    cors_allow_credentials: bool = True
    cors_allow_methods: list[str] = [
        "GET",
        "POST",
        "PUT",
        "DELETE",
        "PATCH",
        "OPTIONS",
    ]
    cors_allow_headers: list[str] = ["*"]

    # Rate Limiting
    rate_limit_per_minute: int = 60

    # Pagination
    default_page_size: int = 10
    max_page_size: int = 20

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra variables in .env


class DevelopmentSettings(BaseSettingsClass):
    """Configuration for local development"""

    app_env: Literal["development"] = "development"
    debug: bool = True
    log_level: str = "debug"

    # More permissive CORS in development
    cors_origins: list[str] = [
        "http://localhost:3000",
        "http://localhost:5173",  # Vite
        "http://localhost:8080",
        "https://spotly.work",
        "https://www.spotly.work",
    ]

    # Relaxed rate limiting in dev
    rate_limit_per_minute: int = 1000


class ProductionSettings(BaseSettingsClass):
    """Configuration for production"""

    app_env: Literal["production"] = "production"
    debug: bool = False
    log_level: str = "info"

    # Strict CORS in production
    cors_origins: list[str] = [
        "https://spotly.work",
        "https://www.spotly.work",
    ]

    # Stricter security
    rate_limit_per_minute: int = 60


class StagingSettings(BaseSettingsClass):
    """Configuration for staging (optional)"""

    app_env: Literal["staging"] = "staging"
    debug: bool = True
    log_level: str = "debug"

    cors_origins: list[str] = [
        "https://staging.spotly.work",
        "https://www.staging.spotly.work",
    ]


def get_settings() -> BaseSettingsClass:
    """
    Factory function that returns the correct configuration based on APP_ENV.
    Uses @lru_cache internally to instantiate only once.
    """
    env = os.getenv("APP_ENV", "production").lower()

    settings_map = {
        "development": DevelopmentSettings,
        "production": ProductionSettings,
        "staging": StagingSettings,
    }

    settings_class = settings_map.get(env, ProductionSettings)
    return settings_class()


# Global instance (created only once thanks to internal lru_cache)
@lru_cache()
def get_cached_settings() -> BaseSettingsClass:
    """
    Cached version of get_settings for use as a FastAPI dependency.
    """
    return get_settings()


# For direct import in other modules
settings = get_cached_settings()
