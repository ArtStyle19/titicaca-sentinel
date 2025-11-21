"""
Frontend tabs package
"""
from .risk_tab import render_risk_tab
from .water_quality_tab import render_water_quality_tab
from .temporal_tab import render_temporal_tab
from .statistics_tab import render_statistics_tab
from .documentation_tab import render_documentation_tab

__all__ = [
    'render_risk_tab',
    'render_water_quality_tab',
    'render_temporal_tab',
    'render_statistics_tab',
    'render_documentation_tab'
]
