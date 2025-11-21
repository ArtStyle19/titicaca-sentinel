"""
TITICACA SENTINEL - Panel Profesional
Plataforma avanzada de monitoreo de calidad del agua para el Lago Titicaca
"""

import streamlit as st
import requests
import folium
import folium.plugins
from streamlit_folium import st_folium
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
import json
from typing import Dict, List
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import utils modules
from frontend.utils.config import COLORS, API_BASE_URL, MAP_CENTER, MAP_DEFAULT_ZOOM
from frontend.utils.api_client import api_client
from frontend.utils.helpers import format_number, get_risk_interpretation

# Page configuration
st.set_page_config(
    page_title="Titicaca Sentinel | Monitoreo de Calidad del Agua",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Color Palette
COLORS = {
    'primary': '#0066CC',      # Deep Blue
    'secondary': '#00A3E0',    # Light Blue
    'accent': '#FF6B35',       # Coral
    'success': '#2ECC71',      # Green
    'warning': '#F39C12',      # Orange
    'danger': '#E74C3C',       # Red
    'dark': '#2C3E50',         # Dark Blue
    'light': '#ECF0F1',        # Light Gray
    'text': '#34495E',         # Dark Gray
    'background': '#F8F9FA',   # Off White
    
    # Risk levels
    'risk_low': '#27AE60',
    'risk_medium': '#F39C12',
    'risk_high': '#E74C3C',
    
    # Water quality
    'water_clean': '#3498DB',
    'water_moderate': '#1ABC9C',
    'water_turbid': '#95A5A6',
    
    # Chlorophyll
    'chl_low': '#3498DB',
    'chl_medium': '#2ECC71',
    'chl_high': '#E74C3C',
}

# Custom CSS
st.markdown(f"""
<style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Global Styles */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    
    /* Main Container */
    .main {{
        background-color: {COLORS['background']};
    }}
    
    /* Header Styles */
    .header-container {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }}
    
    .main-title {{
        font-size: 2.8rem;
        font-weight: 700;
        color: white;
        text-align: center;
        margin: 0;
        letter-spacing: -0.5px;
    }}
    
    .subtitle {{
        font-size: 1.1rem;
        font-weight: 400;
        color: rgba(255, 255, 255, 0.9);
        text-align: center;
        margin-top: 0.5rem;
    }}
    
    /* Card Styles */
    .metric-card {{
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        border-left: 4px solid {COLORS['primary']};
        margin-bottom: 1rem;
        transition: transform 0.2s, box-shadow 0.2s;
    }}
    
    .metric-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
    }}
    
    .metric-label {{
        font-size: 0.875rem;
        font-weight: 600;
        color: {COLORS['text']};
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.5rem;
    }}
    
    .metric-value {{
        font-size: 2rem;
        font-weight: 700;
        color: {COLORS['primary']};
        line-height: 1.2;
    }}
    
    .metric-delta {{
        font-size: 0.875rem;
        margin-top: 0.25rem;
    }}
    
    /* Info Cards */
    .info-card {{
        background: white;
        padding: 1.25rem;
        border-radius: 12px;
        border: 1px solid {COLORS['light']};
        margin-bottom: 1rem;
    }}
    
    .info-card-title {{
        font-size: 1rem;
        font-weight: 600;
        color: {COLORS['dark']};
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
    }}
    
    .info-card-content {{
        font-size: 0.9rem;
        color: {COLORS['text']};
        line-height: 1.6;
    }}
    
    /* Risk Badge */
    .risk-badge {{
        display: inline-block;
        padding: 0.4rem 1rem;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .risk-low {{
        background-color: rgba(46, 204, 113, 0.15);
        color: {COLORS['risk_low']};
    }}
    
    .risk-medium {{
        background-color: rgba(243, 156, 18, 0.15);
        color: {COLORS['risk_medium']};
    }}
    
    .risk-high {{
        background-color: rgba(231, 76, 60, 0.15);
        color: {COLORS['risk_high']};
    }}
    
    /* Sidebar Styles */
    section[data-testid="stSidebar"] {{
        background-color: {COLORS['dark']};
    }}
    
    section[data-testid="stSidebar"] > div {{
        background-color: {COLORS['dark']};
    }}
    
    section[data-testid="stSidebar"] .block-container {{
        padding-top: 2rem;
    }}
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] label,
    section[data-testid="stSidebar"] p {{
        color: white !important;
    }}
    
    section[data-testid="stSidebar"] hr {{
        border-color: rgba(255, 255, 255, 0.2);
    }}
    
    /* Button Styles */
    .stButton > button {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.9rem;
        letter-spacing: 0.3px;
        transition: all 0.3s;
        width: 100%;
    }}
    
    .stButton > button:hover {{
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 102, 204, 0.3);
    }}
    
    /* Tab Styles */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background-color: white;
        padding: 0.5rem;
        border-radius: 12px;
    }}
    
    .stTabs [data-baseweb="tab"] {{
        height: 50px;
        border-radius: 8px;
        padding: 0 24px;
        background-color: transparent;
        font-weight: 500;
        color: {COLORS['text']};
    }}
    
    .stTabs [aria-selected="true"] {{
        background: linear-gradient(135deg, {COLORS['primary']} 0%, {COLORS['secondary']} 100%);
        color: white;
    }}
    
    /* Legend Styles */
    .legend-container {{
        background: white;
        padding: 1rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        margin-top: 1rem;
    }}
    
    .legend-title {{
        font-size: 0.95rem;
        font-weight: 600;
        color: {COLORS['dark']};
        margin-bottom: 0.75rem;
    }}
    
    .legend-item {{
        display: flex;
        align-items: center;
        margin-bottom: 0.5rem;
    }}
    
    .legend-color {{
        width: 20px;
        height: 20px;
        border-radius: 4px;
        margin-right: 0.75rem;
    }}
    
    .legend-label {{
        font-size: 0.875rem;
        color: {COLORS['text']};
    }}
    
    /* Stats Table */
    .stats-table {{
        width: 100%;
        background: white;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
    }}
    
    .stats-table th {{
        background-color: {COLORS['primary']};
        color: white;
        padding: 1rem;
        text-align: left;
        font-weight: 600;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    
    .stats-table td {{
        padding: 0.875rem 1rem;
        border-bottom: 1px solid {COLORS['light']};
        font-size: 0.9rem;
        color: {COLORS['text']};
    }}
    
    .stats-table tr:hover {{
        background-color: {COLORS['background']};
    }}
    
    /* Alert Styles */
    .alert {{
        padding: 1rem 1.25rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        font-size: 0.9rem;
        line-height: 1.6;
    }}
    
    .alert-info {{
        background-color: rgba(0, 163, 224, 0.1);
        border-left: 4px solid {COLORS['secondary']};
        color: {COLORS['text']};
    }}
    
    .alert-success {{
        background-color: rgba(46, 204, 113, 0.1);
        border-left: 4px solid {COLORS['success']};
        color: {COLORS['text']};
    }}
    
    .alert-warning {{
        background-color: rgba(243, 156, 18, 0.1);
        border-left: 4px solid {COLORS['warning']};
        color: {COLORS['text']};
    }}
    
    /* Hide Streamlit Branding */
    #MainMenu {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {{
        width: 10px;
        height: 10px;
    }}
    
    ::-webkit-scrollbar-track {{
        background: {COLORS['light']};
    }}
    
    ::-webkit-scrollbar-thumb {{
        background: {COLORS['primary']};
        border-radius: 5px;
    }}
    
    ::-webkit-scrollbar-thumb:hover {{
        background: {COLORS['secondary']};
    }}
</style>
""", unsafe_allow_html=True)

# Helper functions
def create_map(center=MAP_CENTER, zoom=MAP_DEFAULT_ZOOM):
    """Create base Folium map with professional styling"""
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri',
        name='Satellite'
    )
    
    # Add additional base layers
    folium.TileLayer(
        'OpenStreetMap',
        name='Streets',
        control=True
    ).add_to(m)
    
    folium.TileLayer(
        'CartoDB positron',
        name='Light',
        control=True
    ).add_to(m)
    
    return m

def create_legend_html(layer_type):
    """Create custom legend HTML"""
    legends = {
        "Mapa de Riesgo": {
            "title": "Nivel de Riesgo Ambiental",
            "items": [
                (COLORS['risk_low'], "Condiciones Normales", "Indicadores bajo percentil 70"),
                (COLORS['risk_medium'], "Atención Requerida", "Indicadores entre percentil 70-90"),
                (COLORS['risk_high'], "Zona Crítica", "Indicadores sobre percentil 90"),
            ]
        },
        "NDCI (Clorofila)": {
            "title": "Índice de Clorofila Normalizado",
            "items": [
                ("#3498DB", "Baja Concentración", "NDCI < -0.2 | Aguas oligotróficas"),
                ("#2ECC71", "Concentración Moderada", "-0.2 ≤ NDCI ≤ 0.2 | Aguas mesotróficas"),
                ("#E74C3C", "Alta Concentración", "NDCI > 0.2 | Posible eutrofización"),
            ]
        },
        "NDWI (Agua)": {
            "title": "Índice Normalizado de Agua",
            "items": [
                ("#E74C3C", "Tierra/Vegetación", "NDWI < 0 | Áreas terrestres"),
                ("#F39C12", "Agua Turbia", "0 ≤ NDWI ≤ 0.3 | Sedimentos suspendidos"),
                ("#3498DB", "Agua Clara", "NDWI > 0.3 | Cuerpo de agua definido"),
            ]
        },
        "Turbidez": {
            "title": "Nivel de Turbidez Relativa",
            "items": [
                ("#3498DB", "Baja Turbidez", "Ratio < 0.5 | Buena claridad"),
                ("#F39C12", "Turbidez Moderada", "0.5 ≤ Ratio ≤ 1.5 | Sedimentos moderados"),
                ("#8B4513", "Alta Turbidez", "Ratio > 1.5 | Alta carga de sedimentos"),
            ]
        }
    }
    
    legend = legends.get(layer_type, legends["Mapa de Riesgo"])
    
    html = f"""
    <div class="legend-container">
        <div class="legend-title">{legend['title']}</div>
    """
    
    for color, label, description in legend['items']:
        html += f"""
        <div class="legend-item">
            <div class="legend-color" style="background-color: {color};"></div>
            <div>
                <strong class="legend-label">{label}</strong>
                <div style="font-size: 0.75rem; color: #7f8c8d;">{description}</div>
            </div>
        </div>
        """
    
    html += "</div>"
    return html

# Main App
def main():
    # Professional Header
    st.markdown(f"""
    <div class="header-container">
        <h1 class="main-title">TITICACA SENTINEL</h1>
        <p class="subtitle">Sistema de Monitoreo de Calidad del Agua | Lago Titicaca</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar Configuration
    with st.sidebar:
        st.markdown("## Configuración")
        st.markdown("---")
        
        # Time period selector
        time_unit = st.radio(
            "Período de Análisis",
            options=["Días (Rápido)", "Meses (Completo)"],
            index=0,
            help="Días: Procesamiento más rápido (~90s), ideal para análisis rápido\nMeses: Más datos, mejor para investigación (~180s)"
        )
        
        # Date range selector based on unit
        if "Días" in time_unit:
            time_value = st.slider(
                "Número de Días",
                min_value=3,
                max_value=30,
                value=7,
                help="Mínimo 3 días requeridos para datos suficientes"
            )
            days = time_value
            months = None
            time_display = f"{days} days"
            est_time = 90 if days <= 7 else 120
        else:
            time_value = st.slider(
                "Número de Meses",
                min_value=1,
                max_value=12,
                value=3,
                help="Más meses = más datos pero procesamiento más largo"
            )
            months = time_value
            days = None
            time_display = f"{months} months"
            est_time = 150 + months * 10
        
        # Cloud coverage
        cloud_coverage = st.slider(
            "Cobertura de Nubes Máx. (%)",
            min_value=20,
            max_value=50,
            value=40 if days else 30,
            help="Valores más altos incluyen más imágenes pero pueden reducir la calidad"
        )
        
        # Processing info
        st.markdown("---")
        st.markdown("### Información de Procesamiento")
        st.markdown(f"""
        <div class="info-card">
            <div style="font-size: 0.85rem;">
                <strong>Período:</strong> {time_display}<br>
                <strong>Filtro de Nubes:</strong> {cloud_coverage}%<br>
                <strong>Tiempo Est.:</strong> ~{est_time}s<br>
                <strong>Caché TTL:</strong> 10 minutes
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Refresh button
        if st.button("Actualizar Datos", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        
        st.markdown("---")
        
        # Information
        st.markdown("### Acerca del Sistema")
        st.markdown("""
        <div class="info-card-content">
            <strong>Fuente de Datos:</strong> Sentinel-2 SR<br>
            <strong>Plataforma:</strong> Google Earth Engine<br>
            <strong>Resolución:</strong> 10-20m<br>
            <strong>Cobertura:</strong> Lago Titicaca<br>
            <strong>Índices:</strong> NDWI, NDCI, Turbidez, Clorofila-a
        </div>
        """, unsafe_allow_html=True)
    
    # Main content tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Evaluación de Riesgo",
        "Calidad del Agua", 
        "Análisis Temporal",
        "Estadísticas",
        "Documentación Técnica"
    ])
    
    # TAB 1: RISK ASSESSMENT
    with tab1:
        st.markdown("## Mapa de Evaluación de Riesgo Ambiental")
        
        # Processing info alert
        if days:
            st.markdown(f"""
            <div class="alert alert-info">
                <strong>Modo Rápido:</strong> Procesando últimos {days} días (~{est_time}s primera carga). Resultados en caché por 10 minutos.
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="alert alert-warning">
                <strong>Modo Completo:</strong> Procesando últimos {months} meses (~{est_time}s primera carga). Resultados en caché por 10 minutos.
            </div>
            """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            # Load risk map data
            with st.spinner("Procesando imágenes Sentinel-2..."):
                risk_data = api_client.get_risk_map(cloud_coverage=cloud_coverage, days=days, months=months)
            
            if risk_data:
                # Date display
                st.markdown(f"""
                <div class="alert alert-success">
                    <strong>Última Imagen Procesada:</strong> {risk_data['date']} | <strong>Procesamiento Completo</strong>
                </div>
                """, unsafe_allow_html=True)
                
                # Layer selector
                st.markdown("### 🎨 Layer Selection")
                layer_type = st.selectbox(
                    "Select visualization layer:",
                    ["Mapa de Riesgo", "NDCI (Clorofila)", "NDWI (Agua)", "Turbidez"],
                    key="layer_selector",
                    label_visibility="collapsed"
                )
                
                # Get additional data if needed for other layers
                if layer_type != "Mapa de Riesgo":
                    with st.spinner(f"Loading {layer_type}..."):
                        latest_data = api_client.get_latest_data(cloud_coverage=cloud_coverage, days=days, months=months)
                else:
                    latest_data = None
                
                # Create map
                m = create_map()
                
                # Add ROI
                roi_data = api_client.get_roi()
                if roi_data:
                    folium.GeoJson(
                        roi_data,
                        name='Lake Titicaca',
                        style_function=lambda x: {
                            'fillColor': 'transparent',
                            'color': '#00A3E0',
                            'weight': 3,
                            'opacity': 0.8
                        },
                        tooltip='Lake Titicaca (7,286.56 km²)'
                    ).add_to(m)
                
                # Add selected layer
                if layer_type == "Mapa de Riesgo":
                    risk_url = risk_data['tile_url']
                    folium.TileLayer(
                        tiles=risk_url,
                        attr='Google Earth Engine',
                        name='Environmental Risk',
                        overlay=True,
                        control=True,
                        opacity=0.7
                    ).add_to(m)
                    
                elif layer_type == "NDCI (Clorofila)" and latest_data:
                    ndci_url = latest_data['tile_urls'].get('ndci', '')
                    if ndci_url:
                        folium.TileLayer(
                            tiles=ndci_url,
                            attr='Google Earth Engine',
                            name='NDCI (Chlorophyll)',
                            overlay=True,
                            control=True,
                            opacity=0.7
                        ).add_to(m)
                    else:
                        st.warning("Capa NDCI no disponible para esta fecha")
                        
                elif layer_type == "NDWI (Agua)" and latest_data:
                    ndwi_url = latest_data['tile_urls'].get('ndwi', '')
                    if ndwi_url:
                        folium.TileLayer(
                            tiles=ndwi_url,
                            attr='Google Earth Engine',
                            name='NDWI (Water)',
                            overlay=True,
                            control=True,
                            opacity=0.7
                        ).add_to(m)
                    else:
                        st.warning("Capa NDWI no disponible para esta fecha")
                        
                elif layer_type == "Turbidez" and latest_data:
                    turbidity_url = latest_data['tile_urls'].get('turbidity', '')
                    if turbidity_url:
                        folium.TileLayer(
                            tiles=turbidity_url,
                            attr='Google Earth Engine',
                            name='Turbidity',
                            overlay=True,
                            control=True,
                            opacity=0.7
                        ).add_to(m)
                    else:
                        st.warning("Capa de Turbidez no disponible para esta fecha")
                
                # Add layer control
                folium.LayerControl(position='topright').add_to(m)
                
                # Add scale
                folium.plugins.MeasureControl(position='topleft', primary_length_unit='kilometers').add_to(m)
                
                # Display map
                st_folium(m, width=None, height=600, key=f"map_{layer_type}")
                
                # Legend
                st.markdown(create_legend_html(layer_type), unsafe_allow_html=True)
        
        with col2:
            st.markdown("### Distribución de Riesgo")
            
            if risk_data and 'risk_zones' in risk_data:
                risk_zones = risk_data['risk_zones']
                
                # Convert to DataFrame
                risk_df = pd.DataFrame([
                    {'Level': 'Low', 'Pixels': int(risk_zones.get('1', 0)), 'Color': COLORS['risk_low']},
                    {'Level': 'Medium', 'Pixels': int(risk_zones.get('2', 0)), 'Color': COLORS['risk_medium']},
                    {'Level': 'High', 'Pixels': int(risk_zones.get('3', 0)), 'Color': COLORS['risk_high']}
                ])
                
                # Calculate percentages
                total_pixels = risk_df['Pixels'].sum()
                if total_pixels > 0:
                    risk_df['Percentage'] = (risk_df['Pixels'] / total_pixels * 100).round(1)
                    
                    # Donut chart
                    fig = go.Figure(data=[go.Pie(
                        labels=risk_df['Level'],
                        values=risk_df['Pixels'],
                        hole=0.4,
                        marker=dict(colors=risk_df['Color']),
                        textinfo='label+percent',
                        textfont=dict(size=14, color='white', family='Inter'),
                        hovertemplate='<b>%{label}</b><br>Pixels: %{value:,}<br>Percentage: %{percent}<extra></extra>'
                    )])
                    
                    fig.update_layout(
                        showlegend=False,
                        height=300,
                        margin=dict(t=0, b=0, l=0, r=0),
                        paper_bgcolor='rgba(0,0,0,0)',
                        plot_bgcolor='rgba(0,0,0,0)'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # Key metrics
                    high_risk_pct = risk_df[risk_df['Level']=='High']['Percentage'].values[0]
                    status, color = get_risk_interpretation(high_risk_pct)
                    
                    st.markdown(f"""
                    <div class="metric-card" style="border-left-color: {color};">
                        <div class="metric-label">High Risk Area</div>
                        <div class="metric-value" style="color: {color};">{high_risk_pct}%</div>
                        <div class="metric-delta">
                            <span class="risk-badge risk-{status.lower()}">{status}</span>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Risk breakdown
                    st.markdown("### Desglose por Nivel")
                    for _, row in risk_df.iterrows():
                        st.markdown(f"""
                        <div style="margin-bottom: 0.75rem;">
                            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.25rem;">
                                <span style="font-weight: 600; color: {COLORS['text']};">{row['Level']}</span>
                                <span style="font-weight: 700; color: {row['Color']};">{row['Percentage']}%</span>
                            </div>
                            <div style="background-color: {COLORS['light']}; height: 8px; border-radius: 4px; overflow: hidden;">
                                <div style="background-color: {row['Color']}; width: {row['Percentage']}%; height: 100%;"></div>
                            </div>
                            <div style="font-size: 0.75rem; color: #7f8c8d; margin-top: 0.25rem;">{row['Pixels']:,} pixels</div>
                        </div>
                        """, unsafe_allow_html=True)
            else:
                st.info("No risk zone data available")
    
    # TAB 2: WATER QUALITY ANALYTICS
    with tab2:
        st.markdown("## Water Quality Indicators Analysis")
        
        with st.spinner("Loading water quality data..."):
            latest_data = api_client.get_latest_data(cloud_coverage=cloud_coverage, days=days, months=months)
        
        if latest_data:
            stats = latest_data.get('statistics', {})
            
            # Key indicators grid
            st.markdown("### 🔬 Key Indicators")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                ndci_mean = stats.get('NDCI_mean', 0)
                ndci_status = "High" if ndci_mean > 0.2 else "Medium" if ndci_mean > -0.2 else "Low"
                ndci_color = COLORS['chl_high'] if ndci_mean > 0.2 else COLORS['chl_medium'] if ndci_mean > -0.2 else COLORS['chl_low']
                
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: {ndci_color};">
                    <div class="metric-label">NDCI Mean</div>
                    <div class="metric-value" style="color: {ndci_color}; font-size: 1.5rem;">{format_number(ndci_mean)}</div>
                    <div class="metric-delta">
                        <span style="color: {COLORS['text']};">Chlorophyll: {ndci_status}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                ndwi_mean = stats.get('NDWI_mean', 0)
                ndwi_status = "Clear" if ndwi_mean > 0.3 else "Moderate" if ndwi_mean > 0 else "Turbid"
                ndwi_color = COLORS['water_clean'] if ndwi_mean > 0.3 else COLORS['water_moderate'] if ndwi_mean > 0 else COLORS['water_turbid']
                
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: {ndwi_color};">
                    <div class="metric-label">NDWI Mean</div>
                    <div class="metric-value" style="color: {ndwi_color}; font-size: 1.5rem;">{format_number(ndwi_mean)}</div>
                    <div class="metric-delta">
                        <span style="color: {COLORS['text']};">Water: {ndwi_status}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                turb_mean = stats.get('Turbidity_mean', 0)
                turb_status = "Low" if turb_mean < 0.5 else "Medium" if turb_mean < 1.5 else "High"
                turb_color = COLORS['success'] if turb_mean < 0.5 else COLORS['warning'] if turb_mean < 1.5 else COLORS['danger']
                
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: {turb_color};">
                    <div class="metric-label">Turbidity Mean</div>
                    <div class="metric-value" style="color: {turb_color}; font-size: 1.5rem;">{format_number(turb_mean)}</div>
                    <div class="metric-delta">
                        <span style="color: {COLORS['text']};">Level: {turb_status}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                chl_mean = stats.get('Chla_approx_mean', 0)
                chl_status = "High" if chl_mean > 10 else "Medium" if chl_mean > 5 else "Low"
                chl_color = COLORS['chl_high'] if chl_mean > 10 else COLORS['chl_medium'] if chl_mean > 5 else COLORS['chl_low']
                
                st.markdown(f"""
                <div class="metric-card" style="border-left-color: {chl_color};">
                    <div class="metric-label">Chlorophyll-a</div>
                    <div class="metric-value" style="color: {chl_color}; font-size: 1.5rem;">{format_number(chl_mean)}</div>
                    <div class="metric-delta">
                        <span style="color: {COLORS['text']};">mg/m³ ({chl_status})</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Distribution charts
            st.markdown("### Distribución Estadística")
            
            col1, col2 = st.columns(2)
            
            with col1:
                # NDCI distribution
                ndci_data = {
                    'Percentile': ['P10', 'P50 (Median)', 'P90', 'Mean'],
                    'Value': [
                        stats.get('NDCI_p10', 0),
                        stats.get('NDCI_p50', 0),
                        stats.get('NDCI_p90', 0),
                        stats.get('NDCI_mean', 0)
                    ]
                }
                
                fig_ndci = go.Figure(data=[
                    go.Bar(
                        x=ndci_data['Percentile'],
                        y=ndci_data['Value'],
                        marker_color=[COLORS['primary'], COLORS['secondary'], COLORS['accent'], COLORS['success']],
                        text=[format_number(v) for v in ndci_data['Value']],
                        textposition='outside',
                        textfont=dict(size=12, family='Inter')
                    )
                ])
                
                fig_ndci.update_layout(
                    title=dict(text='NDCI Distribution', font=dict(size=16, family='Inter', color=COLORS['dark'])),
                    xaxis_title='',
                    yaxis_title='NDCI Value',
                    height=350,
                    margin=dict(t=50, b=50, l=50, r=50),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family='Inter', color=COLORS['text'])
                )
                
                st.plotly_chart(fig_ndci, use_container_width=True)
            
            with col2:
                # Turbidity distribution
                turb_data = {
                    'Percentile': ['P10', 'P50 (Median)', 'P90', 'Mean'],
                    'Value': [
                        stats.get('Turbidity_p10', 0),
                        stats.get('Turbidity_p50', 0),
                        stats.get('Turbidity_p90', 0),
                        stats.get('Turbidity_mean', 0)
                    ]
                }
                
                fig_turb = go.Figure(data=[
                    go.Bar(
                        x=turb_data['Percentile'],
                        y=turb_data['Value'],
                        marker_color=[COLORS['primary'], COLORS['secondary'], COLORS['accent'], COLORS['success']],
                        text=[format_number(v) for v in turb_data['Value']],
                        textposition='outside',
                        textfont=dict(size=12, family='Inter')
                    )
                ])
                
                fig_turb.update_layout(
                    title=dict(text='Turbidity Distribution', font=dict(size=16, family='Inter', color=COLORS['dark'])),
                    xaxis_title='',
                    yaxis_title='Turbidity Value',
                    height=350,
                    margin=dict(t=50, b=50, l=50, r=50),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family='Inter', color=COLORS['text'])
                )
                
                st.plotly_chart(fig_turb, use_container_width=True)
            
            # Comparison radar chart
            st.markdown("### Comparación de Índices")
            
            categories = ['NDCI', 'NDWI', 'Turbidity', 'CI-green', 'TSM']
            
            # Normalize values to 0-1 range for comparison
            values_mean = [
                (stats.get('NDCI_mean', 0) + 1) / 2,  # NDCI: -1 to 1 → 0 to 1
                (stats.get('NDWI_mean', 0) + 1) / 2,  # NDWI: -1 to 1 → 0 to 1
                min(stats.get('Turbidity_mean', 0) / 2, 1),  # Turbidity: 0 to 2 → 0 to 1
                (stats.get('CI_green_mean', 0) + 1) / 2 if stats.get('CI_green_mean', 0) > -1 else 0,
                min(stats.get('TSM_mean', 0) / 100, 1)  # TSM: 0 to 100 → 0 to 1
            ]
            
            values_p90 = [
                (stats.get('NDCI_p90', 0) + 1) / 2,
                (stats.get('NDWI_p90', 0) + 1) / 2,
                min(stats.get('Turbidity_p90', 0) / 2, 1),
                (stats.get('CI_green_p90', 0) + 1) / 2 if stats.get('CI_green_p90', 0) > -1 else 0,
                min(stats.get('TSM_p90', 0) / 100, 1)
            ]
            
            fig_radar = go.Figure()
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values_mean,
                theta=categories,
                fill='toself',
                name='Mean',
                line=dict(color=COLORS['primary'], width=2),
                fillcolor=f"rgba{tuple(list(int(COLORS['primary'][i:i+2], 16) for i in (1, 3, 5)) + [0.2])}"
            ))
            
            fig_radar.add_trace(go.Scatterpolar(
                r=values_p90,
                theta=categories,
                fill='toself',
                name='P90',
                line=dict(color=COLORS['accent'], width=2),
                fillcolor=f"rgba(255, 107, 53, 0.2)"
            ))
            
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 1],
                        gridcolor=COLORS['light']
                    ),
                    angularaxis=dict(gridcolor=COLORS['light'])
                ),
                showlegend=True,
                height=400,
                paper_bgcolor='white',
                plot_bgcolor='white',
                font=dict(family='Inter', color=COLORS['text'])
            )
            
            st.plotly_chart(fig_radar, use_container_width=True)
            
        else:
            st.error("Failed to load water quality data")
    
    # TAB 3: TEMPORAL ANALYSIS
    with tab3:
        st.markdown("## Temporal Trend Analysis")
        
        st.markdown("""
        <div class="alert alert-info">
            <strong>Selección de Punto:</strong> Haz clic en el mapa o ingresa coordenadas para analizar tendencias temporales en un punto específico.
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 1, 1])
        with col1:
            st.markdown("### Coordenadas")
        with col2:
            selected_lat = st.number_input("Latitud", value=-16.0, format="%.4f", min_value=-17.5, max_value=-15.0)
        with col3:
            selected_lon = st.number_input("Longitud", value=-69.0, format="%.4f", min_value=-70.5, max_value=-68.0)
        
        if st.button("Generar Análisis Temporal", use_container_width=True, type="primary"):
            with st.spinner("Generating temporal analysis..."):
                ts_data = api_client.get_time_series(selected_lat, selected_lon, cloud_coverage=cloud_coverage, days=days, months=months)
            
            if ts_data and ts_data.get('data'):
                # Convert to DataFrame
                df = pd.DataFrame([
                    {
                        'Date': pd.to_datetime(d['date']),
                        'NDCI': d['ndci'],
                        'Chlorophyll-a': d['chla_approx'],
                        'Turbidity': d['turbidity'],
                        'NDWI': d['ndwi']
                    }
                    for d in ts_data['data']
                ])
                
                df = df.sort_values('Date')
                
                # Multi-line time series
                st.markdown("### Evolución de Indicadores")
                
                fig_multi = go.Figure()
                
                fig_multi.add_trace(go.Scatter(
                    x=df['Date'], y=df['NDCI'],
                    mode='lines+markers',
                    name='NDCI',
                    line=dict(color=COLORS['primary'], width=2),
                    marker=dict(size=6)
                ))
                
                fig_multi.add_trace(go.Scatter(
                    x=df['Date'], y=df['NDWI'],
                    mode='lines+markers',
                    name='NDWI',
                    line=dict(color=COLORS['secondary'], width=2),
                    marker=dict(size=6)
                ))
                
                fig_multi.add_trace(go.Scatter(
                    x=df['Date'], y=df['Turbidity'],
                    mode='lines+markers',
                    name='Turbidity',
                    line=dict(color=COLORS['accent'], width=2),
                    marker=dict(size=6)
                ))
                
                fig_multi.update_layout(
                    title=dict(text=f'Water Quality Trends at ({selected_lat:.4f}, {selected_lon:.4f})', 
                              font=dict(size=18, family='Inter', color=COLORS['dark'])),
                    xaxis_title='Date',
                    yaxis_title='Index Value',
                    hovermode='x unified',
                    height=450,
                    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
                    plot_bgcolor='white',
                    paper_bgcolor='white',
                    font=dict(family='Inter', color=COLORS['text']),
                    xaxis=dict(gridcolor=COLORS['light']),
                    yaxis=dict(gridcolor=COLORS['light'])
                )
                
                st.plotly_chart(fig_multi, use_container_width=True)
                
                # Individual detailed charts
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("### 🌿 Chlorophyll-a Concentration")
                    
                    fig_chl = go.Figure()
                    fig_chl.add_trace(go.Scatter(
                        x=df['Date'],
                        y=df['Chlorophyll-a'],
                        mode='lines+markers',
                        name='Chlorophyll-a',
                        line=dict(color=COLORS['success'], width=3),
                        marker=dict(size=8, symbol='circle'),
                        fill='tonexty',
                        fillcolor=f"rgba{tuple(list(int(COLORS['success'][i:i+2], 16) for i in (1, 3, 5)) + [0.2])}"
                    ))
                    
                    fig_chl.update_layout(
                        xaxis_title='Date',
                        yaxis_title='Chlorophyll-a (mg/m³)',
                        hovermode='x',
                        height=350,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(family='Inter', color=COLORS['text']),
                        xaxis=dict(gridcolor=COLORS['light']),
                        yaxis=dict(gridcolor=COLORS['light'])
                    )
                    
                    st.plotly_chart(fig_chl, use_container_width=True)
                    
                    # Statistics
                    st.markdown(f"""
                    <div class="info-card">
                        <strong>Statistics:</strong><br>
                        Mean: {df['Chlorophyll-a'].mean():.2f} mg/m³<br>
                        Min: {df['Chlorophyll-a'].min():.2f} mg/m³<br>
                        Max: {df['Chlorophyll-a'].max():.2f} mg/m³<br>
                        Std Dev: {df['Chlorophyll-a'].std():.2f} mg/m³
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("### Turbidez")
                    
                    fig_turb = go.Figure()
                    fig_turb.add_trace(go.Scatter(
                        x=df['Date'],
                        y=df['Turbidity'],
                        mode='lines+markers',
                        name='Turbidity',
                        line=dict(color=COLORS['warning'], width=3),
                        marker=dict(size=8, symbol='diamond'),
                        fill='tonexty',
                        fillcolor=f"rgba{tuple(list(int(COLORS['warning'][i:i+2], 16) for i in (1, 3, 5)) + [0.2])}"
                    ))
                    
                    fig_turb.update_layout(
                        xaxis_title='Date',
                        yaxis_title='Turbidity Index',
                        hovermode='x',
                        height=350,
                        plot_bgcolor='white',
                        paper_bgcolor='white',
                        font=dict(family='Inter', color=COLORS['text']),
                        xaxis=dict(gridcolor=COLORS['light']),
                        yaxis=dict(gridcolor=COLORS['light'])
                    )
                    
                    st.plotly_chart(fig_turb, use_container_width=True)
                    
                    # Statistics
                    st.markdown(f"""
                    <div class="info-card">
                        <strong>Statistics:</strong><br>
                        Mean: {df['Turbidity'].mean():.3f}<br>
                        Min: {df['Turbidity'].min():.3f}<br>
                        Max: {df['Turbidity'].max():.3f}<br>
                        Std Dev: {df['Turbidity'].std():.3f}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Data table
                st.markdown("### Datos Procesados")
                
                # Format dataframe for display
                display_df = df.copy()
                display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
                display_df = display_df.round(4)
                
                st.dataframe(
                    display_df,
                    use_container_width=True,
                    hide_index=True
                )
                
                # Download button
                csv = display_df.to_csv(index=False)
                st.download_button(
                    label="Descargar Datos (CSV)",
                    data=csv,
                    file_name=f"titicaca_timeseries_{selected_lat}_{selected_lon}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
            else:
                st.warning("No se encontraron datos para esta ubicación. Seleccione un punto dentro del Lago Titicaca.")
    
    # TAB 4: DETAILED STATISTICS
    with tab4:
        st.markdown("## Comprehensive Statistical Analysis")
        
        with st.spinner("Loading comprehensive statistics..."):
            latest_data = api_client.get_latest_data(cloud_coverage=cloud_coverage, days=days, months=months)
        
        if latest_data:
            stats = latest_data.get('statistics', {})
            
            # Organize statistics by indicator
            indicators = {
                'NDCI (Chlorophyll Index)': ['NDCI_mean', 'NDCI_p10', 'NDCI_p50', 'NDCI_p90', 'NDCI_stdDev'],
                'NDWI (Water Index)': ['NDWI_mean', 'NDWI_p10', 'NDWI_p50', 'NDWI_p90', 'NDWI_stdDev'],
                'Turbidity': ['Turbidity_mean', 'Turbidity_p10', 'Turbidity_p50', 'Turbidity_p90', 'Turbidity_stdDev'],
                'CI-green': ['CI_green_mean', 'CI_green_p10', 'CI_green_p50', 'CI_green_p90', 'CI_green_stdDev'],
                'TSM (Total Suspended Matter)': ['TSM_mean', 'TSM_p10', 'TSM_p50', 'TSM_p90', 'TSM_stdDev'],
                'Chlorophyll-a (Approx.)': ['Chla_approx_mean', 'Chla_approx_p10', 'Chla_approx_p50', 'Chla_approx_p90', 'Chla_approx_stdDev']
            }
            
            # Create tabs for each indicator
            indicator_tabs = st.tabs(list(indicators.keys()))
            
            for idx, (indicator_name, indicator_keys) in enumerate(indicators.items()):
                with indicator_tabs[idx]:
                    # Extract values
                    values = {key.split('_')[-1]: stats.get(key, 0) for key in indicator_keys}
                    
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        # Box plot visualization
                        box_data = [
                            values.get('p10', 0),
                            values.get('p50', 0),
                            values.get('p90', 0)
                        ]
                        
                        fig_box = go.Figure()
                        fig_box.add_trace(go.Box(
                            y=box_data,
                            name=indicator_name,
                            marker_color=COLORS['primary'],
                            boxmean='sd'
                        ))
                        
                        fig_box.update_layout(
                            title=f'{indicator_name} Distribution',
                            yaxis_title='Value',
                            height=350,
                            showlegend=False,
                            plot_bgcolor='white',
                            paper_bgcolor='white',
                            font=dict(family='Inter', color=COLORS['text'])
                        )
                        
                        st.plotly_chart(fig_box, use_container_width=True)
                    
                    with col2:
                        # Statistics table
                        st.markdown("### 📊 Statistical Metrics")
                        
                        st.markdown(f"""
                        <table class="stats-table">
                            <thead>
                                <tr>
                                    <th>Metric</th>
                                    <th>Value</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>Mean (Average)</strong></td>
                                    <td>{format_number(values.get('mean', 0))}</td>
                                </tr>
                                <tr>
                                    <td><strong>10th Percentile</strong></td>
                                    <td>{format_number(values.get('p10', 0))}</td>
                                </tr>
                                <tr>
                                    <td><strong>Median (50th Percentile)</strong></td>
                                    <td>{format_number(values.get('p50', 0))}</td>
                                </tr>
                                <tr>
                                    <td><strong>90th Percentile</strong></td>
                                    <td>{format_number(values.get('p90', 0))}</td>
                                </tr>
                                <tr>
                                    <td><strong>Standard Deviation</strong></td>
                                    <td>{format_number(values.get('stdDev', 0))}</td>
                                </tr>
                                <tr>
                                    <td><strong>Range (P10-P90)</strong></td>
                                    <td>{format_number(values.get('p90', 0) - values.get('p10', 0))}</td>
                                </tr>
                            </tbody>
                        </table>
                        """, unsafe_allow_html=True)
                        
                        # Interpretation
                        st.markdown("### 💡 Interpretation")
                        
                        interpretations = {
                            'NDCI (Chlorophyll Index)': f"""
                                <div class="info-card">
                                    The mean NDCI value of <strong>{format_number(values.get('mean', 0))}</strong> indicates 
                                    {'high' if values.get('mean', 0) > 0.2 else 'moderate' if values.get('mean', 0) > -0.2 else 'low'} 
                                    chlorophyll concentration. Values closer to 1 indicate higher chlorophyll presence, 
                                    which may suggest eutrophication or algal blooms.
                                </div>
                            """,
                            'NDWI (Water Index)': f"""
                                <div class="info-card">
                                    The mean NDWI value of <strong>{format_number(values.get('mean', 0))}</strong> suggests 
                                    {'clear water conditions' if values.get('mean', 0) > 0.3 else 'moderate water quality' if values.get('mean', 0) > 0 else 'turbid or vegetated areas'}. 
                                    Higher NDWI values (>0.3) typically indicate clear, deep water.
                                </div>
                            """,
                            'Turbidity': f"""
                                <div class="info-card">
                                    Average turbidity of <strong>{format_number(values.get('mean', 0))}</strong> indicates 
                                    {'low' if values.get('mean', 0) < 0.5 else 'moderate' if values.get('mean', 0) < 1.5 else 'high'} 
                                    sediment concentration. Lower values suggest clearer water with less suspended particles.
                                </div>
                            """,
                            'CI-green': f"""
                                <div class="info-card">
                                    The CI-green index value of <strong>{format_number(values.get('mean', 0))}</strong> 
                                    helps detect aquatic vegetation. Positive values may indicate presence of algae or aquatic plants.
                                </div>
                            """,
                            'TSM (Total Suspended Matter)': f"""
                                <div class="info-card">
                                    TSM mean value of <strong>{format_number(values.get('mean', 0))}</strong> represents 
                                    the concentration of suspended particles. Higher values may indicate erosion, pollution, 
                                    or resuspension of sediments.
                                </div>
                            """,
                            'Chlorophyll-a (Approx.)': f"""
                                <div class="info-card">
                                    Estimated chlorophyll-a concentration of <strong>{format_number(values.get('mean', 0))} mg/m³</strong> 
                                    provides an approximation of algal biomass. Values >10 mg/m³ may indicate eutrophic conditions.
                                </div>
                            """
                        }
                        
                        st.markdown(interpretations.get(indicator_name, ""), unsafe_allow_html=True)
            
            # Summary comparison
            st.markdown("---")
            st.markdown("## 📈 Cross-Indicator Summary")
            
            # Create summary dataframe
            summary_data = []
            for indicator_name, indicator_keys in indicators.items():
                mean_key = [k for k in indicator_keys if 'mean' in k][0]
                std_key = [k for k in indicator_keys if 'stdDev' in k][0]
                p50_key = [k for k in indicator_keys if 'p50' in k][0]
                
                summary_data.append({
                    'Indicator': indicator_name.split(' (')[0],
                    'Mean': format_number(stats.get(mean_key, 0)),
                    'Median': format_number(stats.get(p50_key, 0)),
                    'Std Dev': format_number(stats.get(std_key, 0)),
                    'CV (%)': format_number(abs(stats.get(std_key, 0) / stats.get(mean_key, 1) * 100) if stats.get(mean_key, 0) != 0 else 0, 1)
                })
            
            summary_df = pd.DataFrame(summary_data)
            
            st.dataframe(
                summary_df,
                use_container_width=True,
                hide_index=True
            )
            
            st.markdown("""
            <div class="alert alert-info">
                <strong>Note:</strong> CV (Coefficient of Variation) indicates the relative variability. 
                Higher CV suggests greater spatial heterogeneity in the lake.
            </div>
            """, unsafe_allow_html=True)
            
        else:
            st.error("Failed to load statistics data")
    
    # TAB 5: DOCUMENTATION
    with tab5:
        st.markdown("## Documentación del Proyecto")
        
        # Project overview
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("""
            ### Titicaca Sentinel
            
            **Sistema de Monitoreo de Calidad del Agua mediante Teledetección Satelital**
            
            Este sistema utiliza imágenes multiespectrales del satélite Sentinel-2 (ESA) para evaluar la calidad 
            del agua en el Lago Titicaca. El procesamiento se realiza mediante Google Earth Engine, calculando 
            índices espectrales que permiten identificar concentraciones de clorofila, turbidez y delimitar 
            cuerpos de agua.
            
            ---
            
            ### Objetivos del Sistema
            
            1. **Monitoreo Sistemático**: Evaluación periódica de indicadores de calidad del agua
            2. **Detección de Anomalías**: Identificación temprana de zonas con condiciones atípicas
            3. **Análisis de Tendencias**: Seguimiento de la evolución temporal de los indicadores
            4. **Soporte a la Gestión**: Información geoespacial para la toma de decisiones ambientales
            5. **Acceso Abierto**: Plataforma web para consulta de datos procesados
            
            ---
            
            ### Datos y Tecnología
            
            #### Fuente de Datos Satelitales
            - **Misión**: Copernicus Sentinel-2
            - **Agencia**: European Space Agency (ESA)
            - **Colección**: COPERNICUS/S2_SR_HARMONIZED
            - **Resolución Espacial**: 10-20 metros
            - **Frecuencia Temporal**: 5 días (2 satélites)
            - **Bandas Espectrales**: 13 bandas (443nm - 2190nm)
            
            #### Plataforma de Procesamiento
            - **Motor de Cálculo**: Google Earth Engine
            - **API Backend**: FastAPI (Python)
            - **Interfaz Web**: Streamlit
            - **Visualización**: Folium (mapas), Plotly (gráficos)
            - **Análisis Numérico**: Pandas, NumPy
            
            ---
            
            ### Índices Espectrales Calculados
            """)
            
            # Indicators details
            indicators_doc = [
                {
                    'name': 'NDCI (Índice Normalizado de Clorofila)',
                    'formula': '(Red Edge - Red) / (Red Edge + Red)',
                    'bands': 'Banda 5 (705nm) y Banda 4 (665nm)',
                    'range': '-1 a +1',
                    'interpretation': 'Estima concentración de clorofila-a. Valores altos (>0.2) pueden indicar floraciones algales o condiciones eutróficas.'
                },
                {
                    'name': 'NDWI (Índice Normalizado de Agua)',
                    'formula': '(Green - NIR) / (Green + NIR)',
                    'bands': 'Banda 3 (560nm) y Banda 8 (842nm)',
                    'range': '-1 a +1',
                    'interpretation': 'Detecta cuerpos de agua. Valores >0.3 indican agua abierta, mientras que valores menores sugieren vegetación o tierra.'
                },
                {
                    'name': 'Índice de Turbidez',
                    'formula': 'Red / Blue',
                    'bands': 'Banda 4 (665nm) y Banda 2 (490nm)',
                    'range': '0 a ∞',
                    'interpretation': 'Aproxima concentración de sedimentos suspendidos. Valores altos (>1.5) indican agua turbia con alta carga de partículas.'
                },
                {
                    'name': 'CI-green (Índice de Clorofila Verde)',
                    'formula': '(NIR / Green) - 1',
                    'bands': 'Banda 8 (842nm) y Banda 3 (560nm)',
                    'range': '-1 a ∞',
                    'interpretation': 'Indicador alternativo de clorofila. Valores positivos sugieren presencia de vegetación acuática o algas.'
                },
                {
                    'name': 'TSM (Materia Suspendida Total)',
                    'formula': 'Modelo empírico complejo',
                    'bands': 'Múltiples bandas (Red, NIR)',
                    'range': '0 a 100+ mg/L',
                    'interpretation': 'Estima concentración total de partículas en suspensión. Útil para evaluar carga de sedimentos.'
                },
                {
                    'name': 'Concentración de Clorofila-a',
                    'formula': 'Derivada de correlación con NDCI',
                    'bands': 'Banda 5 y Banda 4',
                    'range': '0 a 100+ mg/m³',
                    'interpretation': 'Concentración aproximada de clorofila-a. Valores >10 mg/m³ pueden indicar condiciones eutróficas.'
                }
            ]
            
            for ind in indicators_doc:
                st.markdown(f"""
                <div class="info-card">
                    <h4 style="color: {COLORS['primary']}; margin-bottom: 0.5rem;">{ind['name']}</h4>
                    <p style="margin-bottom: 0.5rem;">
                        <strong>Formula:</strong> <code>{ind['formula']}</code><br>
                        <strong>Bands:</strong> {ind['bands']}<br>
                        <strong>Range:</strong> {ind['range']}
                    </p>
                    <p style="margin-bottom: 0; font-size: 0.9rem;">
                        <strong>Interpretation:</strong> {ind['interpretation']}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            # Quick facts
            st.markdown(f"""
            <div class="metric-card" style="border-left-color: {COLORS['primary']};">
                <div class="metric-label">Lake Area</div>
                <div class="metric-value" style="font-size: 1.8rem;">7,287 km²</div>
            </div>
            
            <div class="metric-card" style="border-left-color: {COLORS['secondary']};">
                <div class="metric-label">Max Depth</div>
                <div class="metric-value" style="font-size: 1.8rem;">281 m</div>
            </div>
            
            <div class="metric-card" style="border-left-color: {COLORS['accent']};">
                <div class="metric-label">Elevation</div>
                <div class="metric-value" style="font-size: 1.8rem;">3,812 m</div>
            </div>
            
            <div class="metric-card" style="border-left-color: {COLORS['success']};">
                <div class="metric-label">Location</div>
                <div class="metric-value" style="font-size: 1.2rem;">Peru-Bolivia</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("""
            ### 🎨 Risk Classification
            
            <div class="info-card">
                <div style="margin-bottom: 0.75rem;">
                    <div class="risk-badge risk-low">LOW RISK</div>
                    <div style="font-size: 0.85rem; margin-top: 0.25rem;">
                        Values below 70th percentile
                    </div>
                </div>
                
                <div style="margin-bottom: 0.75rem;">
                    <div class="risk-badge risk-medium">MEDIUM RISK</div>
                    <div style="font-size: 0.85rem; margin-top: 0.25rem;">
                        Values between 70th-90th percentile
                    </div>
                </div>
                
                <div>
                    <div class="risk-badge risk-high">HIGH RISK</div>
                    <div style="font-size: 0.85rem; margin-top: 0.25rem;">
                        Values above 90th percentile
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("""
            ### ⚙️ System Info
            
            <div class="info-card-content">
                <strong>Version:</strong> 1.0.0<br>
                <strong>Last Update:</strong> Nov 2025<br>
                <strong>Caché TTL:</strong> 10 minutes<br>
                <strong>Processing Scale:</strong> 100m<br>
                <strong>API Timeout:</strong> 180s
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Methodology
        st.markdown("""
        ### 🔬 Methodology
        
        #### 1. Image Acquisition & Preprocessing
        - Sentinel-2 images are filtered by date range and cloud coverage
        - Cloud masking using QA60 band to remove cloudy pixels
        - Atmospheric correction already applied in SR products
        
        #### 2. Index Calculation
        - Spectral indices computed using band math operations
        - Normalized indices scaled to [-1, 1] range
        - Statistical aggregation across the region of interest
        
        #### 3. Risk Classification
        - Percentile-based relative assessment
        - Thresholds calculated from current data distribution
        - Three-level classification: Low, Medium, High
        
        #### 4. Visualization & Export
        - Interactive maps using Folium with EE tiles
        - Statistical charts with Plotly
        - Exportable data in CSV format
        
        ---
        
        ### ⚠️ Limitations & Considerations
        
        <div class="alert alert-warning">
            <strong>Important Notes:</strong>
            <ul style="margin-bottom: 0;">
                <li>Chlorophyll-a values are approximations based on empirical correlations</li>
                <li>Cloud coverage may limit data availability</li>
                <li>Risk thresholds are relative to current conditions, not absolute standards</li>
                <li>In-situ validation recommended for precise measurements</li>
                <li>Spatial resolution (10-20m) may not capture small-scale features</li>
            </ul>
        </div>
        
        ---
        
        ### 📖 References
        
        1. Mishra, S., & Mishra, D. R. (2012). Normalized difference chlorophyll index
        2. McFeeters, S. K. (1996). The use of the Normalized Difference Water Index (NDWI)
        3. Gitelson, A. A., et al. (2008). A simple semi-analytical model for remote estimation of chlorophyll-a
        4. Nechad, B., et al. (2010). Calibration and validation of a generic multisensor algorithm for mapping of total suspended matter
        
        ---
        
        ### 👥 Development Team
        
        Titicaca Sentinel is developed as an open-source environmental monitoring platform.
        Contributions and feedback are welcome to improve water quality assessment capabilities.
        
        ---
        
        ### 📧 Contact & Support
        
        For questions, suggestions, or collaboration opportunities, please refer to the project repository.
        """)

if __name__ == "__main__":
    main()
