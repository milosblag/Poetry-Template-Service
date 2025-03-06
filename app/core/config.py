from functools import lru_cache
from typing import List

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation."""

    # Server settings
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)
    RELOAD: bool = Field(default=False)
    WORKERS: int = Field(default=4)

    # Environment settings
    ENVIRONMENT: str = Field(default="development")
    LOG_LEVEL: str = Field(default="INFO")
    LOG_FILE: str = Field(default="app.log")
    LOG_MAX_SIZE: int = Field(default=10485760)  # 10MB
    LOG_BACKUP_COUNT: int = Field(default=5)

    # CORS settings
    ALLOWED_ORIGINS: str = Field(default="*")

    # API settings
    API_VERSION: str = Field(default="v1")
    API_KEY: str = Field(default="test_api_key")  # Replace with a secure key in production

    # Rate limiting
    RATE_LIMIT_GENERAL: str = Field(default="100/minute")

    # Application version
    VERSION: str = Field(default="1.0.0")

    # Configuration using class variable
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=True
    )

    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from string to list."""
        origins = self.ALLOWED_ORIGINS.split(",")

        # Restrict allowed origins in production
        if self.ENVIRONMENT == "production" and "*" in origins:
            return ["https://yourdomain.com"]

        return origins

    @field_validator("LOG_LEVEL")
    def uppercase_log_level(cls, v: str) -> str:
        """Ensure LOG_LEVEL is uppercase."""
        return v.upper()


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
