"""
PolarSync Platform - Backend Core Settings
"""
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "PolarSync API"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ]
    
    FRONTEND_URL: str = "http://localhost:5175"
    
    # Database
    DATABASE_URL: str = "postgresql://polarsync_user:polarsync_pass@localhost:5432/polarsync_db"
    
    # Secret
    SECRET_KEY: str = "polarsync-sih26062-secret-key-change-in-production"

    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
