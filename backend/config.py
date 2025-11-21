"""
Backend configuration settings
"""
import os
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_TITLE: str = "Titicaca Sentinel API"
    API_DESCRIPTION: str = "Water quality monitoring API for Lake Titicaca using Sentinel-2 data"
    API_VERSION: str = "1.0.0"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    API_RELOAD: bool = True
    
    # CORS Configuration
    CORS_ORIGINS: list = ["*"]  # In production, specify exact origins
    
    # Google Earth Engine Configuration
    GOOGLE_CLOUD_PROJECT: Optional[str] = None
    EE_SERVICE_ACCOUNT_EMAIL: Optional[str] = None
    EE_PRIVATE_KEY_PATH: Optional[str] = None
    
    # Processing Parameters
    DEFAULT_MONTHS: int = 6
    DEFAULT_DAYS: int = 7
    DEFAULT_CLOUD_COVERAGE: int = 20
    MAX_CLOUD_COVERAGE: int = 50
    
    # Cache Settings
    CACHE_TTL: int = 600  # 10 minutes
    
    # Legacy settings (from original .env - optional, ignored if not used)
    STREAMLIT_PORT: Optional[int] = 8501
    DATA_DIR: Optional[str] = "./data"
    EXPORT_DIR: Optional[str] = "./data/exports"
    CLOUD_COVERAGE_MAX: Optional[int] = None
    ANALYSIS_MONTHS: Optional[int] = None
    UPDATE_FREQUENCY_DAYS: Optional[int] = None
    ROI_GEOJSON_PATH: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()
