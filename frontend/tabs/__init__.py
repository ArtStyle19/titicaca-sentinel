"""
Frontend tabs package
"""
from .risk_tab import render_risk_tab
from .water_quality_tab import render_water_quality_tab
from .temporal_tab import render_temporal_tab
from .statistics_tab import render_statistics_tab
from .documentation_tab import render_documentation_tab
from .comparison_tab import render_comparison_tab
from .report_tab import render_report_tab
from .prediction_tab import render_prediction_tab

__all__ = [
    'render_risk_tab',
    'render_water_quality_tab',
    'render_temporal_tab',
    'render_statistics_tab',
    'render_documentation_tab',
    'render_comparison_tab',
    'render_report_tab',
    'render_prediction_tab'
]
