"""
Frontend utilities package
"""
from frontend.utils.config import COLORS, API_BASE_URL, LAKE_BOUNDS
from frontend.utils.api_client import api_client
from frontend.utils.helpers import (
    format_number,
    get_risk_interpretation,
    validate_coordinates
)

__all__ = [
    'COLORS',
    'API_BASE_URL',
    'LAKE_BOUNDS',
    'api_client',
    'format_number',
    'get_risk_interpretation',
    'validate_coordinates'
]
