# App configuration
# core/config.py
# 📦 Centralized configuration for the app using environment variables
from pydantic import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # 🗝️ Environment Variables
    database_url: str
    openai_api_key: str
    stripe_secret_key: str
    stripe_webhook_secret: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expiration_minutes: int = 60

    # 📧 Optional email settings (for future use)
    email_host: str = ""
    email_port: int = 587
    email_username: str = ""
    email_password: str = ""

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# ✅ Cached singleton so settings are loaded once
@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()
