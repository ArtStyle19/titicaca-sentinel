"""
Risk Assessment Tab
"""
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
from frontend.components.maps import create_map, create_legend_html
from frontend.components.charts import create_risk_donut_chart, create_distribution_bar_chart
from frontend.components.ui import render_metric_card, render_info_card, render_alert, render_risk_badge, render_progress_bar
from frontend.utils.config import COLORS, LAKE_INFO, DEFAULT_CLOUD_COVERAGE, DEFAULT_DAYS
from frontend.utils.helpers import format_number


def render_risk_tab(api_client, latest_data):
    """Render Risk Assessment tab"""
    
    # Header
    st.markdown("### 🎯 Evaluación de Riesgo Ambiental")
    st.markdown("**Análisis integrado de indicadores de calidad del agua basado en datos satelitales Sentinel-2**")
    
    # Load risk map data
    risk_data = None
    try:
        with st.spinner("Cargando mapa de riesgo... (2-3 minutos, procesamiento en Earth Engine)"):
            risk_data = api_client.get_risk_map(
                cloud_coverage=DEFAULT_CLOUD_COVERAGE,
                days=DEFAULT_DAYS
            )
    except Exception as e:
        render_alert(f"❌ Error al cargar mapa de riesgo: {str(e)}", "danger")
        return
    
    if not risk_data or 'risk_zones' not in risk_data:
        render_alert("⚠️ No se pudo cargar el mapa de riesgo. Intente recargar la página.", "warning")
        return
    
    # Calculate statistics from risk_zones
    risk_zones = risk_data['risk_zones']
    total_pixels = sum(risk_zones.values())
    
    if total_pixels == 0:
        render_alert("⚠️ No hay datos de zonas de riesgo disponibles.", "warning")
        return
    
    stats = {
        'low_risk_percentage': (risk_zones.get('1', 0) / total_pixels) * 100,
        'medium_risk_percentage': (risk_zones.get('2', 0) / total_pixels) * 100,
        'high_risk_percentage': (risk_zones.get('3', 0) / total_pixels) * 100,
        'total_pixels': total_pixels
    }
    
    # Risk Overview Cards
    st.markdown("#### Resumen de Condiciones")
    cols = st.columns(4)
    
    with cols[0]:
        high_pct = stats.get('high_risk_percentage', 0)
        render_metric_card(
            "Zona Crítica",
            f"{high_pct:.1f}%",
            "Alta prioridad",
            COLORS['risk_high'],
            COLORS['risk_high']
        )
    
    with cols[1]:
        medium_pct = stats.get('medium_risk_percentage', 0)
        render_metric_card(
            "Atención",
            f"{medium_pct:.1f}%",
            "Monitoreo requerido",
            COLORS['risk_medium'],
            COLORS['risk_medium']
        )
    
    with cols[2]:
        low_pct = stats.get('low_risk_percentage', 0)
        render_metric_card(
            "Condiciones Normales",
            f"{low_pct:.1f}%",
            "Estado óptimo",
            COLORS['risk_low'],
            COLORS['risk_low']
        )
    
    with cols[3]:
        total_pixels = stats.get('total_pixels', 0)
        render_metric_card(
            "Área Analizada",
            f"{total_pixels:,}",
            "pixels evaluados",
            COLORS['info']
        )
    
    st.markdown("---")
    
    # Map and Chart Section
    col1, col2 = st.columns([3, 2])
    
    with col1:
        st.markdown("#### 🗺️ Mapa de Riesgo")
        
        # Create map
        m = create_map()
        
        # Add risk layer
        if 'tile_url' in risk_data:
            import folium
            folium.TileLayer(
                tiles=risk_data['tile_url'],
                attr='Google Earth Engine',
                name='Risk Map',
                overlay=True,
                control=True,
                opacity=0.7
            ).add_to(m)
        
        # Add legend
        legend_html = create_legend_html("Mapa de Riesgo")
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Display map with unique key
        st_folium(m, width=None, height=450, key="risk_assessment_map")
    
    with col2:
        st.markdown("#### 📊 Distribución de Riesgo")
        
        # Prepare data for donut chart
        risk_df = pd.DataFrame({
            'Level': ['Zona Crítica', 'Atención', 'Normal'],
            'Pixels': [
                stats.get('high_risk_pixels', 0),
                stats.get('medium_risk_pixels', 0),
                stats.get('low_risk_pixels', 0)
            ],
            'Color': [COLORS['risk_high'], COLORS['risk_medium'], COLORS['risk_low']]
        })
        
        fig = create_risk_donut_chart(risk_df)
        st.plotly_chart(fig, use_container_width=True)
        
        # Progress bars
        st.markdown("##### Desglose por Nivel")
        render_progress_bar("Crítico", high_pct, COLORS['risk_high'])
        render_progress_bar("Atención", medium_pct, COLORS['risk_medium'])
        render_progress_bar("Normal", low_pct, COLORS['risk_low'])
    
    st.markdown("---")
    
    # Detailed Statistics
    st.markdown("#### 📈 Estadísticas Detalladas")
    
    cols = st.columns(3)
    
    with cols[0]:
        st.markdown("##### NDCI (Clorofila)")
        if 'ndci' in stats:
            ndci_stats = stats['ndci']
            perc_data = pd.DataFrame({
                'Percentile': ['P25', 'P50', 'P75', 'P90'],
                'Value': [
                    ndci_stats.get('p25', 0),
                    ndci_stats.get('p50', 0),
                    ndci_stats.get('p75', 0),
                    ndci_stats.get('p90', 0)
                ]
            })
            fig = create_distribution_bar_chart(perc_data, "", "NDCI Value")
            st.plotly_chart(fig, use_container_width=True)
    
    with cols[1]:
        st.markdown("##### NDWI (Agua)")
        if 'ndwi' in stats:
            ndwi_stats = stats['ndwi']
            perc_data = pd.DataFrame({
                'Percentile': ['P25', 'P50', 'P75', 'P90'],
                'Value': [
                    ndwi_stats.get('p25', 0),
                    ndwi_stats.get('p50', 0),
                    ndwi_stats.get('p75', 0),
                    ndwi_stats.get('p90', 0)
                ]
            })
            fig = create_distribution_bar_chart(perc_data, "", "NDWI Value")
            st.plotly_chart(fig, use_container_width=True)
    
    with cols[2]:
        st.markdown("##### Turbidez")
        if 'turbidity' in stats:
            turb_stats = stats['turbidity']
            perc_data = pd.DataFrame({
                'Percentile': ['P25', 'P50', 'P75', 'P90'],
                'Value': [
                    turb_stats.get('p25', 0),
                    turb_stats.get('p50', 0),
                    turb_stats.get('p75', 0),
                    turb_stats.get('p90', 0)
                ]
            })
            fig = create_distribution_bar_chart(perc_data, "", "Turbidity Ratio")
            st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations
    st.markdown("---")
    st.markdown("#### 💡 Recomendaciones")
    
    if high_pct > 10:
        render_alert(
            "⚠️ <strong>Alerta:</strong> Más del 10% del área presenta condiciones críticas. "
            "Se recomienda intensificar el monitoreo en zonas de alta turbidez y concentración de clorofila.",
            "danger"
        )
    elif medium_pct > 20:
        render_alert(
            "⚡ <strong>Atención:</strong> Áreas significativas requieren monitoreo continuo. "
            "Considere análisis adicionales en regiones con valores elevados.",
            "warning"
        )
    else:
        render_alert(
            "✅ <strong>Estado Favorable:</strong> Las condiciones generales del lago son estables. "
            "Mantener el monitoreo regular.",
            "success"
        )
