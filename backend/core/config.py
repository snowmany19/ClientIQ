# App configuration
# core/config.py
# 📦 Centralized configuration for the app using environment variables
import os
import secrets
from functools import lru_cache


class Settings:
    """Application settings with environment variable support."""
    
    def __init__(self):
        # 🗝️ Environment Variables
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./incidentiq.db")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.stripe_secret_key = os.getenv("STRIPE_SECRET_KEY", "")
        self.stripe_webhook_secret = os.getenv("STRIPE_WEBHOOK_SECRET", "")
        self.jwt_secret_key = os.getenv("SECRET_KEY", "")
        self.jwt_algorithm = os.getenv("ALGORITHM", "HS256")
        self.jwt_expiration_minutes = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

        # 🔒 Security Settings
        self.password_min_length = int(os.getenv("PASSWORD_MIN_LENGTH", "8"))
        self.password_require_uppercase = os.getenv("PASSWORD_REQUIRE_UPPERCASE", "true").lower() == "true"
        self.password_require_lowercase = os.getenv("PASSWORD_REQUIRE_LOWERCASE", "true").lower() == "true"
        self.password_require_digits = os.getenv("PASSWORD_REQUIRE_DIGITS", "true").lower() == "true"
        self.password_require_special = os.getenv("PASSWORD_REQUIRE_SPECIAL", "true").lower() == "true"
        
        # 🚦 Rate Limiting
        self.rate_limit_requests = int(os.getenv("RATE_LIMIT_REQUESTS", "100"))
        self.rate_limit_window = int(os.getenv("RATE_LIMIT_WINDOW", "60"))
        
        # 📧 Optional email settings
        self.email_host = os.getenv("EMAIL_HOST", "")
        self.email_port = int(os.getenv("EMAIL_PORT", "587"))
        self.email_username = os.getenv("EMAIL_USERNAME", "")
        self.email_password = os.getenv("EMAIL_PASSWORD", "")
        
        # 🔧 Environment
        self.environment = os.getenv("ENVIRONMENT", "development")
        self.debug = os.getenv("DEBUG", "false").lower() == "true"
        
        # 📊 Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        self.log_file = os.getenv("LOG_FILE", "logs/app.log")
        
        # Validate critical settings
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate critical security settings."""
        # Generate secure secret if not provided
        if not self.jwt_secret_key or self.jwt_secret_key == "super-secret-key" or len(self.jwt_secret_key) < 32:
            if self.environment == "production":
                raise ValueError("JWT secret key must be at least 32 characters and not the default value")
            else:
                # In development, generate a secure secret automatically
                self.jwt_secret_key = secrets.token_urlsafe(32)
                print("⚠️  WARNING: Generated secure JWT secret for development. Set SECRET_KEY in .env for production.")
        
        if self.environment not in ['development', 'staging', 'production']:
            raise ValueError("Environment must be development, staging, or production")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def generate_secure_secret() -> str:
    """Generate a secure random secret key."""
    return secrets.token_urlsafe(32)
