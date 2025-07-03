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
        self.database_url = os.getenv("DATABASE_URL", "sqlite:///./a_incident.db")
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
        
        # 🌐 CORS Configuration
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:8501")
        self.cors_origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else []
        
        # Default CORS origins for development
        if not self.cors_origins:
            self.cors_origins = [
                "http://localhost:8501",  # Streamlit default
                "http://127.0.0.1:8501",  # Alternative localhost
                "http://localhost:3000",  # React default
                "http://127.0.0.1:3000",  # Alternative React localhost
            ]
            # Add frontend URL if it's not already in the list
            if self.frontend_url not in self.cors_origins:
                self.cors_origins.append(self.frontend_url)
        
        # Validate critical settings
        self._validate_settings()
    
    def _validate_settings(self):
        """Validate critical security settings."""
        # Enhanced JWT secret validation and management
        if not self.jwt_secret_key or self.jwt_secret_key == "super-secret-key" or len(self.jwt_secret_key) < 32:
            if self.environment == "production":
                raise ValueError("JWT secret key must be at least 32 characters and not the default value. Use: openssl rand -hex 32")
            else:
                # In development, generate a secure secret automatically
                self.jwt_secret_key = secrets.token_urlsafe(32)
                print("⚠️  WARNING: Generated secure JWT secret for development. Set SECRET_KEY in .env for production.")
        
        # Additional security validations
        if self.environment == "production":
            # Ensure all critical secrets are set in production
            if not self.openai_api_key:
                raise ValueError("OPENAI_API_KEY must be set in production")
            if not self.stripe_secret_key:
                raise ValueError("STRIPE_SECRET_KEY must be set in production")
            if not self.stripe_webhook_secret:
                raise ValueError("STRIPE_WEBHOOK_SECRET must be set in production")
        
        if self.environment not in ['development', 'staging', 'production']:
            raise ValueError("Environment must be development, staging, or production")


@lru_cache()
def get_settings() -> Settings:
    return Settings()


def generate_secure_secret() -> str:
    """Generate a secure random secret key."""
    return secrets.token_urlsafe(32)
