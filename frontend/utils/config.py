"""
Frontend configuration and constants
Centralizes all configuration values for maintainability
"""

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_TIMEOUT = 300  # 5 minutos para procesamiento GEE (ajustado desde 120s)

# Cache Configuration
CACHE_TTL = 600  # 10 minutes in seconds

# Map Configuration
MAP_CENTER = [-16.0, -69.0]
MAP_DEFAULT_ZOOM = 9

# Lake Titicaca Bounds (for validation)
LAKE_BOUNDS = {
    'lat_min': -17.5,
    'lat_max': -15.0,
    'lon_min': -70.5,
    'lon_max': -68.0
}

# Default Processing Parameters
DEFAULT_DAYS = 7  # Procesar últimos 7 días
DEFAULT_MONTHS = None  # No usar meses por defecto
DEFAULT_CLOUD_COVERAGE = 20  # Reducido para imágenes más claras
MIN_CLOUD_COVERAGE = 20
MAX_CLOUD_COVERAGE = 50

# Professional Color Palette
COLORS = {
    # Primary Colors
    'primary': '#0066CC',
    'secondary': '#00A3E0',
    'accent': '#FF6B35',
    
    # Status Colors
    'success': '#2ECC71',
    'warning': '#F39C12',
    'danger': '#E74C3C',
    'info': '#3498DB',
    
    # UI Colors
    'dark': '#2C3E50',
    'light': '#ECF0F1',
    'text': '#34495E',
    'background': '#F8F9FA',
    
    # Risk Levels
    'risk_low': '#27AE60',
    'risk_medium': '#F39C12',
    'risk_high': '#E74C3C',
    
    # Water Quality
    'water_clean': '#3498DB',
    'water_moderate': '#1ABC9C',
    'water_turbid': '#95A5A6',
    
    # Chlorophyll
    'chl_low': '#3498DB',
    'chl_medium': '#2ECC71',
    'chl_high': '#E74C3C',
}

# Visualization Palettes for Indices
INDEX_PALETTES = {
    'NDWI': {
        'min': -1,
        'max': 1,
        'palette': ['red', 'yellow', 'green', 'cyan', 'blue']
    },
    'NDCI': {
        'min': -0.5,
        'max': 0.5,
        'palette': ['blue', 'cyan', 'yellow', 'orange', 'red']
    },
    'Turbidity': {
        'min': 0.5,
        'max': 2.0,
        'palette': ['blue', 'cyan', 'yellow', 'orange', 'brown']
    },
    'Risk': {
        'min': 1,
        'max': 3,
        'palette': ['green', 'yellow', 'red']
    }
}

# Chart Configuration
CHART_CONFIG = {
    'font_family': 'Inter',
    'plot_bgcolor': 'white',
    'paper_bgcolor': 'white',
    'gridcolor': COLORS['light']
}

# Lake Information
LAKE_INFO = {
    'name': 'Lago Titicaca',
    'area_km2': 7287,
    'max_depth_m': 281,
    'elevation_m': 3812,
    'location': 'Peru-Bolivia Border',
    'center': {
        'lat': -16.0,
        'lng': -69.0
    },
    'bounds': {
        'north': -15.0,
        'south': -17.5,
        'east': -68.0,
        'west': -70.5
    }
}

# System Information
SYSTEM_INFO = {
    'version': '1.0.0',
    'data_source': 'Sentinel-2 SR',
    'platform': 'Google Earth Engine',
    'resolution': '10-20m',
    'indices': ['NDWI', 'NDCI', 'Turbidity', 'Chlorophyll-a']
}
