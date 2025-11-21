"""
UI Components - Cards, Metrics, Alerts
"""
import streamlit as st
from frontend.utils.config import COLORS
from frontend.utils.helpers import format_number, get_risk_interpretation


def render_header():
    """Render application header"""
    st.markdown(f"""
    <div class="header-container">
        <h1 class="main-title">TITICACA SENTINEL</h1>
        <p class="subtitle">Sistema de Monitoreo de Calidad del Agua | Lago Titicaca</p>
    </div>
    """, unsafe_allow_html=True)


def render_metric_card(label, value, delta=None, color=COLORS['primary'], border_color=None):
    """Render a metric card"""
    border = border_color or color
    delta_html = f'<div class="metric-delta">{delta}</div>' if delta else ''
    
    st.markdown(f"""
    <div class="metric-card" style="border-left-color: {border};">
        <div class="metric-label">{label}</div>
        <div class="metric-value" style="color: {color};">{value}</div>
        {delta_html}
    </div>
    """, unsafe_allow_html=True)


def render_info_card(content):
    """Render an info card"""
    st.markdown(f"""
    <div class="info-card">
        <div class="info-card-content">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def render_alert(message, alert_type="info"):
    """Render an alert message"""
    st.markdown(f"""
    <div class="alert alert-{alert_type}">
        {message}
    </div>
    """, unsafe_allow_html=True)


def render_risk_badge(percentage):
    """Render risk badge with interpretation"""
    status, color = get_risk_interpretation(percentage)
    return f'<span class="risk-badge risk-{status.lower()}">{status}</span>'


def render_progress_bar(label, percentage, color):
    """Render a progress bar"""
    st.markdown(f"""
    <div style="margin-bottom: 0.75rem;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
            <span style="font-weight: 600; color: {COLORS['text']};">{label}</span>
            <span style="font-weight: 700; color: {color};">{percentage}%</span>
        </div>
        <div style="background-color: {COLORS['light']}; height: 8px; border-radius: 4px; overflow: hidden;">
            <div style="background-color: {color}; width: {percentage}%; height: 100%;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_statistics_table(stats_data):
    """Render statistics table"""
    rows = ""
    for metric, value in stats_data.items():
        rows += f"""
        <tr>
            <td><strong>{metric}</strong></td>
            <td>{format_number(value)}</td>
        </tr>
        """
    
    st.markdown(f"""
    <table class="stats-table">
        <thead>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
            {rows}
        </tbody>
    </table>
    """, unsafe_allow_html=True)
