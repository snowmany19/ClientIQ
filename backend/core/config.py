# App configuration
# core/config.py
# 📦 Centralized configuration for the app using environment variables
import os
import secrets
from functools import lru_cache
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./civicloghoa.db")
    
    # Security (backwards compatible)
    secret_key: str = os.getenv("JWT_SECRET_KEY", os.getenv("SECRET_KEY", "your-secret-key-change-in-production"))
    algorithm: str = os.getenv("JWT_ALGORITHM", os.getenv("ALGORITHM", "HS256"))
    access_token_expire_minutes: int = int(os.getenv("JWT_EXPIRATION_MINUTES", os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")))
    password_min_length: int = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
    password_require_uppercase: bool = os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
    password_require_lowercase: bool = os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true"
    password_require_digits: bool = os.getenv("PASSWORD_REQUIRE_DIGITS", "true").lower() == "true"
    password_require_special: bool = os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"
    
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
        "http://localhost:3000",  # React default
        "http://localhost:8000",  # FastAPI default
    ]
    
    # Logging
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    log_file: str = os.getenv("LOG_FILE", "logs/civicloghoa.log")
    
    # Rate limiting
    rate_limit_requests: int = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
    rate_limit_window: int = int(os.getenv("RATE_LIMIT_WINDOW", "3600"))
    
    # New fields for full backwards compatibility with AIncident .env files
    jwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "your-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_minutes: int = int(os.getenv("JWT_EXPIRATION_MINUTES", "60"))
    frontend_url: str = os.getenv("FRONTEND_URL", "http://localhost:8501")
    
    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def generate_secure_secret() -> str:
    """Generate a secure random secret key."""
    return secrets.token_urlsafe(32)
