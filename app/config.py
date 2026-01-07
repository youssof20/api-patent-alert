"""
Configuration management for the Patent Alert API
"""
from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Application
    app_name: str = "Patent Alert API"
    app_version: str = "1.0.0"
    debug: bool = False
    environment: str = "production"
    
    # Database
    database_url: str = "sqlite:///./patent_alert.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379/0"
    redis_cache_ttl: int = 86400  # 24 hours in seconds
    
    # USPTO API
    uspto_api_key: str = ""
    uspto_patentsview_url: str = "https://api.patentsview.org/patents/query"
    uspto_bulk_data_url: str = "https://bulkdata.uspto.gov/data/patent"
    
    # Hugging Face
    hf_api_key: str = ""
    hf_model_name: str = "facebook/bart-large-cnn"
    
    # Security
    secret_key: str = "change-this-secret-key-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # API Settings
    api_rate_limit_per_minute: int = 60
    api_rate_limit_per_day: int = 10000
    default_branding: bool = True
    
    # Stripe
    stripe_secret_key: str = ""
    stripe_publishable_key: str = ""
    stripe_webhook_secret: str = ""
    
    # Webhooks
    webhook_retry_attempts: int = 3
    webhook_retry_delay: int = 5
    webhook_timeout: int = 30
    
    # Admin
    admin_username: str = "admin"
    admin_password: str = "change_this_password"
    
    # CORS
    allowed_origins: str = "http://localhost:3000,http://localhost:8000"
    
    # Email (SMTP)
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = ""
    
    # Monitoring
    sentry_dsn: str = ""  # Sentry error tracking
    enable_metrics: bool = True
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse allowed origins string into list"""
        return [origin.strip() for origin in self.allowed_origins.split(",")]
    
    @property
    def contact(self) -> dict:
        """Contact information"""
        return {
            "name": "API Support",
            "email": "betterappsstudio@gmail.com"
        }
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

