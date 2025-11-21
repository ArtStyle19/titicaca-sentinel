"""
Configuration utilities for Titicaca Sentinel
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration"""
    
    # Google Earth Engine
    GOOGLE_CLOUD_PROJECT = os.getenv('GOOGLE_CLOUD_PROJECT')
    EE_SERVICE_ACCOUNT_EMAIL = os.getenv('EE_SERVICE_ACCOUNT_EMAIL')
    EE_PRIVATE_KEY_PATH = os.getenv('EE_PRIVATE_KEY_PATH')
    
    # API
    API_HOST = os.getenv('API_HOST', '0.0.0.0')
    API_PORT = int(os.getenv('API_PORT', 8000))
    API_RELOAD = os.getenv('API_RELOAD', 'True').lower() == 'true'
    
    # Streamlit
    STREAMLIT_PORT = int(os.getenv('STREAMLIT_PORT', 8501))
    
    # Data paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / 'data'
    EXPORT_DIR = DATA_DIR / 'exports'
    CONFIG_DIR = BASE_DIR / 'config'
    
    # Analysis parameters
    CLOUD_COVERAGE_MAX = int(os.getenv('CLOUD_COVERAGE_MAX', 20))
    ANALYSIS_MONTHS = int(os.getenv('ANALYSIS_MONTHS', 6))
    UPDATE_FREQUENCY_DAYS = int(os.getenv('UPDATE_FREQUENCY_DAYS', 7))
    
    # ROI
    ROI_GEOJSON_PATH = os.getenv(
        'ROI_GEOJSON_PATH',
        str(CONFIG_DIR / 'titicaca_roi.geojson')
    )
    
    # Lake Titicaca coordinates (approximate center)
    LAKE_CENTER = {
        'lat': -16.0,
        'lon': -69.0
    }
    
    # Bounding box
    LAKE_BBOX = [-70.3, -17.3, -68.4, -15.4]  # [west, south, east, north]
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.EXPORT_DIR.mkdir(exist_ok=True)
        cls.CONFIG_DIR.mkdir(exist_ok=True)
        
    @classmethod
    def validate(cls):
        """Validate configuration"""
        errors = []
        
        if not cls.GOOGLE_CLOUD_PROJECT:
            errors.append("GOOGLE_CLOUD_PROJECT not set")
        
        return errors


if __name__ == "__main__":
    Config.ensure_directories()
    errors = Config.validate()
    
    if errors:
        print("❌ Configuration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✓ Configuration valid")
        print(f"  Project: {Config.GOOGLE_CLOUD_PROJECT}")
        print(f"  Data dir: {Config.DATA_DIR}")
        print(f"  Export dir: {Config.EXPORT_DIR}")
