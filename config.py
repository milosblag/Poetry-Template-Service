import os
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from typing import List, Optional
from functools import lru_cache

class Settings(BaseSettings):
    """Application settings with validation."""
    # Server settings
    HOST: str = Field("0.0.0.0")
    PORT: int = Field(8000)
    RELOAD: bool = Field(False)
    WORKERS: int = Field(4)
    
    # Environment settings
    ENVIRONMENT: str = Field("development")
    LOG_LEVEL: str = Field("INFO")
    LOG_FILE: str = Field("app.log")
    LOG_MAX_SIZE: int = Field(10485760)  # 10MB
    LOG_BACKUP_COUNT: int = Field(5)
    
    # CORS settings
    ALLOWED_ORIGINS: str = Field("*")
    
    # API settings
    API_VERSION: str = Field("v1")
    
    # Rate limiting
    RATE_LIMIT_GENERAL: str = Field("100/minute")
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse ALLOWED_ORIGINS from string to list."""
        origins = self.ALLOWED_ORIGINS.split(",")
        
        # Restrict allowed origins in production
        if self.ENVIRONMENT == "production" and "*" in origins:
            return ["https://yourdomain.com"]
        
        return origins
        
    @field_validator("LOG_LEVEL")
    def uppercase_log_level(cls, v):
        """Ensure LOG_LEVEL is uppercase."""
        return v.upper()

@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings() 