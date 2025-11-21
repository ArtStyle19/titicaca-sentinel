"""
Utility functions for data formatting and validation
"""
from typing import Tuple, Dict, Any


def transform_statistics(backend_stats: Dict[str, float]) -> Dict[str, Dict[str, float]]:
    """Transform backend statistics format to frontend format
    
    Backend format: {"NDCI_mean": 0.5, "NDCI_p10": 0.3, ...}
    Frontend format: {"ndci": {"mean": 0.5, "p10": 0.3, ...}, ...}
    
    Args:
        backend_stats: Statistics from backend API
        
    Returns:
        Transformed statistics in nested format
    """
    result = {
        'ndci': {},
        'ndwi': {},
        'turbidity': {},
        'chlorophyll': {},
        'ci_green': {},
        'tsm': {}
    }
    
    # Mapping of backend keys to frontend keys
    index_mapping = {
        'NDCI': 'ndci',
        'NDWI': 'ndwi',
        'Turbidity': 'turbidity',
        'Chla_approx': 'chlorophyll',
        'CI_green': 'ci_green',
        'TSM': 'tsm'
    }
    
    stat_mapping = {
        'mean': 'mean',
        'p10': 'min',  # Approximation
        'p50': 'median',
        'p90': 'max',  # Approximation
        'stdDev': 'std'
    }
    
    # Transform each statistic
    for backend_key, value in backend_stats.items():
        # Parse the key (e.g., "NDCI_mean" -> "NDCI", "mean")
        parts = backend_key.rsplit('_', 1)
        if len(parts) == 2:
            index_name, stat_name = parts
            
            # Map to frontend keys
            frontend_index = index_mapping.get(index_name)
            frontend_stat = stat_mapping.get(stat_name, stat_name)
            
            if frontend_index and frontend_index in result:
                result[frontend_index][frontend_stat] = value
    
    return result


def format_number(value: float, decimals: int = 2) -> str:
    """Format number with appropriate precision"""
    if abs(value) < 0.01:
        return f"{value:.4f}"
    elif abs(value) < 1:
        return f"{value:.3f}"
    else:
        return f"{value:.{decimals}f}"


def get_risk_interpretation(percentage: float) -> Tuple[str, str]:
    """Get risk interpretation text and color
    
    Args:
        percentage: Percentage of high risk area
        
    Returns:
        Tuple of (interpretation, color_code)
    """
    from frontend.utils.config import COLORS
    
    if percentage < 15:
        return "Excellent", COLORS['success']
    elif percentage < 30:
        return "Good", COLORS['risk_low']
    elif percentage < 50:
        return "Moderate", COLORS['warning']
    else:
        return "Critical", COLORS['danger']


def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate if coordinates are within Lake Titicaca bounds"""
    from frontend.utils.config import LAKE_BOUNDS
    
    return (
        LAKE_BOUNDS['lat_min'] <= lat <= LAKE_BOUNDS['lat_max'] and
        LAKE_BOUNDS['lon_min'] <= lon <= LAKE_BOUNDS['lon_max']
    )


def get_ndci_status(ndci_value: float) -> Tuple[str, str]:
    """Get chlorophyll status from NDCI value
    
    Returns:
        Tuple of (status_text, color_code)
    """
    from frontend.utils.config import COLORS
    
    if ndci_value > 0.2:
        return "Alta Concentración (Posible Eutrofización)", COLORS['chl_high']
    elif ndci_value > -0.2:
        return "Concentración Moderada", COLORS['chl_medium']
    else:
        return "Baja Concentración", COLORS['chl_low']


def get_ndwi_status(ndwi_value: float) -> Tuple[str, str]:
    """Get water status from NDWI value
    
    Returns:
        Tuple of (status_text, color_code)
    """
    from frontend.utils.config import COLORS
    
    if ndwi_value > 0.3:
        return "Agua Clara (Cuerpo de Agua Definido)", COLORS['water_clean']
    elif ndwi_value > 0:
        return "Agua Turbia (Sedimentos Suspendidos)", COLORS['water_moderate']
    else:
        return "Tierra/Vegetación", COLORS['water_turbid']


def get_turbidity_status(turbidity_value: float) -> Tuple[str, str]:
    """Get turbidity status from turbidity ratio
    
    Returns:
        Tuple of (status_text, color_code)
    """
    from frontend.utils.config import COLORS
    
    if turbidity_value > 1.5:
        return "Alta Turbidez (Alta Carga de Sedimentos)", COLORS['danger']
    elif turbidity_value > 0.5:
        return "Turbidez Moderada", COLORS['warning']
    else:
        return "Baja Turbidez (Buena Claridad)", COLORS['success']


def get_chlorophyll_status(chl_value: float) -> Tuple[str, str]:
    """Get chlorophyll-a status
    
    Returns:
        Tuple of (status_text, color_code)
    """
    from frontend.utils.config import COLORS
    
    if chl_value > 10:
        return "Alta Concentración", COLORS['chl_high']
    elif chl_value > 5:
        return "Concentración Moderada", COLORS['chl_medium']
    else:
        return "Baja Concentración", COLORS['chl_low']


def get_status_color(value: float, low_threshold: float, high_threshold: float, reverse: bool = False) -> str:
    """Get color based on value thresholds
    
    Args:
        value: The value to evaluate
        low_threshold: Lower threshold
        high_threshold: Higher threshold
        reverse: If True, higher values are better (green)
        
    Returns:
        Color code
    """
    from frontend.utils.config import COLORS
    
    if reverse:
        if value >= high_threshold:
            return COLORS['success']
        elif value >= low_threshold:
            return COLORS['warning']
        else:
            return COLORS['danger']
    else:
        if value >= high_threshold:
            return COLORS['danger']
        elif value >= low_threshold:
            return COLORS['warning']
        else:
            return COLORS['success']
