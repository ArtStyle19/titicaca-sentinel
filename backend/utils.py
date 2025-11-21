"""
Utility functions for Titicaca Sentinel (Optimized)
Only contains actively used functions
"""

import numpy as np
from typing import Dict, List


def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate if coordinates are within Lake Titicaca bounds
    
    Args:
        lat: Latitude coordinate
        lon: Longitude coordinate
        
    Returns:
        bool: True if coordinates are within lake bounds
    """
    # Lake Titicaca approximate bounds
    lat_min, lat_max = -17.3, -15.4
    lon_min, lon_max = -70.3, -68.4
    
    return (lat_min <= lat <= lat_max) and (lon_min <= lon <= lon_max)


def calculate_statistics(values: List[float]) -> Dict:
    """Calculate basic statistics from a list of values
    
    Args:
        values: List of numeric values
        
    Returns:
        Dictionary with mean, std, min, max, and count
    """
    values_array = np.array(values)
    values_clean = values_array[~np.isnan(values_array)]
    
    if len(values_clean) == 0:
        return {
            'mean': None,
            'std': None,
            'min': None,
            'max': None,
            'count': 0
        }
    
    return {
        'mean': float(np.mean(values_clean)),
        'std': float(np.std(values_clean)),
        'min': float(np.min(values_clean)),
        'max': float(np.max(values_clean)),
        'count': len(values_clean)
    }
