# App configuration
# core/config.py
# 📦 Centralized configuration for the app using environment variables
import os
import secrets
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Allow unknown env vars to avoid failing on extras and load from .env by default
    model_config = SettingsConfigDict(env_file=".env", extra="allow")
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./contractguard.db")
    
    # Security (backwards compatible)
    secret_key: str = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "your-secret-key-change-in-production"))
    algorithm: str = os.getenv("JWT_ALGORITHM", os.getenv("ALGORITHM", "HS256"))
    access_token_expire_minutes: int = int(os.getenv("JWT_EXPIRATION_MINUTES", os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
    password_min_length: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    password_require_uppercase: bool = os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
    password_require_lowercase: bool = os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true"
    password_require_digits: bool = os.getenv("PASSWORD_REQUIRE_DIGITS", "true").lower() == "true"
    password_require_special: bool = os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"
    
    # Validate critical security settings
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._validate_security_settings()
    
    def _validate_security_settings(self):
        """Validate critical security settings."""
        if self.environment == "production":
            if self.secret_key in ["your-secret-key-change-in-production", "your-secret-key"]:
                raise ValueError("SECRET_KEY must be set to a secure value in production")
            
            if self.jwt_secret_key in ["your-secret-key"]:
                raise ValueError("JWT_SECRET_KEY must be set to a secure value in production")
            
            if not self.stripe_secret_key:
                raise ValueError("STRIPE_SECRET_KEY must be set in production")
            
            if not self.smtp_password:
                raise ValueError("SMTP_PASSWORD must be set in production")
    
    # OpenAI
    openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
    
    # Stripe
    stripe_secret_key: str = os.getenv("STRIPE_SECRET_KEY", "")
    stripe_webhook_secret: str = os.getenv("STRIPE_WEBHOOK_SECRET", "")
    
    # Email
    smtp_server: str = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_username: str = os.getenv("SMTP_USERNAME", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    
    # Environment
    environment: str = os.getenv("ENVIRONMENT", "development")
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # CORS
    cors_origins: List[str] = [
        "http://localhost:8501",  # Streamlit default
        "http://localhost:3001",  # React default
        "http://localhost:3001",  # Next.js frontend
        "http://localhost:8000",  # FastAPI default
    ]
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs/contractguard.log")
    
    # Rate limiting
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))
    
    # New fields for full backwards compatibility with AIncident .env files
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_minutes: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:8501")
    
    # Pydantic v2 uses model_config above; keeping compatibility field names intact


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def generate_secure_secret() -> str:
    """Generate a secure random secret key."""
    return secrets.token_urlsafe(32)
