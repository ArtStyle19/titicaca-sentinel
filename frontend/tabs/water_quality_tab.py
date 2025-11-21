"""
Water Quality Tab
"""
import streamlit as st
from streamlit_folium import st_folium
import folium
from frontend.components.maps import create_map, create_legend_html
from frontend.components.ui import render_metric_card, render_info_card, render_alert
from frontend.utils.config import COLORS, INDEX_PALETTES
from frontend.utils.helpers import get_ndci_status, get_ndwi_status, get_turbidity_status


def render_water_quality_tab(api_client, latest_data):
    """Render Water Quality tab"""
    
    st.markdown("### 💧 Calidad del Agua - Índices Espectrales")
    st.markdown("**Visualización de indicadores individuales de calidad del agua**")
    
    # Layer selector
    layer_type = st.selectbox(
        "Seleccionar índice espectral:",
        ["NDCI (Clorofila)", "NDWI (Agua)", "Turbidez"],
        help="Elija el indicador a visualizar en el mapa",
        key="water_quality_layer_selector"
    )
    
    # Map layer mapping
    layer_map = {
        "NDCI (Clorofila)": 'ndci',
        "NDWI (Agua)": 'ndwi',
        "Turbidez": 'turbidity'
    }
    
    selected_layer = layer_map[layer_type]
    
    # Get tile URL
    tile_url = latest_data.get('tile_urls', {}).get(selected_layer)
    
    if not tile_url:
        render_alert("⚠️ No se pudo cargar la capa seleccionada", "warning")
        return
    
    # Stats for selected layer
    stats = latest_data.get('statistics', {}).get(selected_layer, {})
    
    # Metrics Row
    st.markdown("#### Estadísticas del Índice")
    cols = st.columns(5)
    
    with cols[0]:
        mean_val = stats.get('mean', 0)
        render_metric_card("Media", f"{mean_val:.3f}", "Valor promedio", COLORS['primary'])
    
    with cols[1]:
        median_val = stats.get('median', 0)
        render_metric_card("Mediana", f"{median_val:.3f}", "Percentil 50", COLORS['secondary'])
    
    with cols[2]:
        std_val = stats.get('std', 0)
        render_metric_card("Desv. Est.", f"{std_val:.3f}", "Variabilidad", COLORS['info'])
    
    with cols[3]:
        min_val = stats.get('min', 0)
        render_metric_card("Mínimo", f"{min_val:.3f}", "Valor más bajo", COLORS['success'])
    
    with cols[4]:
        max_val = stats.get('max', 0)
        render_metric_card("Máximo", f"{max_val:.3f}", "Valor más alto", COLORS['accent'])
    
    st.markdown("---")
    
    # Map Section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"#### 🗺️ Mapa: {layer_type}")
        
        m = create_map()
        
        # Add selected layer
        folium.TileLayer(
            tiles=tile_url,
            attr='Google Earth Engine',
            name=layer_type,
            overlay=True,
            control=True,
            opacity=0.7
        ).add_to(m)
        
        # Add legend
        legend_html = create_legend_html(layer_type)
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Use unique key for st_folium based on selected layer
        st_folium(m, width=None, height=500, key=f"water_quality_map_{selected_layer}")
    
    with col2:
        st.markdown("#### 📊 Distribución")
        
        # Percentile info
        render_info_card(f"""
        <strong>Percentiles:</strong><br>
        P25: {stats.get('p25', 0):.3f}<br>
        P50: {stats.get('p50', 0):.3f}<br>
        P75: {stats.get('p75', 0):.3f}<br>
        P90: {stats.get('p90', 0):.3f}<br>
        P95: {stats.get('p95', 0):.3f}
        """)
        
        # Status interpretation
        if selected_layer == 'ndci':
            status, color = get_ndci_status(mean_val)
        elif selected_layer == 'ndwi':
            status, color = get_ndwi_status(mean_val)
        else:
            status, color = get_turbidity_status(mean_val)
        
        st.markdown(f"""
        <div style="margin-top: 1rem; padding: 1rem; background-color: {color}20; border-left: 4px solid {color}; border-radius: 4px;">
            <strong style="color: {color};">Estado Actual:</strong><br>
            <span style="font-size: 1.1rem;">{status}</span>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Index Information
    st.markdown("#### 📖 Información del Índice")
    
    if layer_type == "NDCI (Clorofila)":
        render_info_card("""
        <strong>Normalized Difference Chlorophyll Index (NDCI)</strong><br><br>
        El NDCI es un índice espectral diseñado para estimar la concentración de clorofila-a en cuerpos de agua. 
        Utiliza las bandas del rojo (665 nm) y rojo cercano (705 nm) para detectar la presencia de fitoplancton.<br><br>
        <strong>Fórmula:</strong> NDCI = (RE - Red) / (RE + Red)<br>
        <strong>Rango:</strong> -1 a 1<br>
        <strong>Interpretación:</strong>
        <ul>
            <li>< -0.2: Baja concentración de clorofila (oligotrófico)</li>
            <li>-0.2 a 0.2: Concentración moderada (mesotrófico)</li>
            <li>> 0.2: Alta concentración, posible eutrofización</li>
        </ul>
        """)
    
    elif layer_type == "NDWI (Agua)":
        render_info_card("""
        <strong>Normalized Difference Water Index (NDWI)</strong><br><br>
        El NDWI es utilizado para delinear y monitorear cuerpos de agua. Enfatiza la presencia de agua 
        mientras suprime la vegetación y el suelo.<br><br>
        <strong>Fórmula:</strong> NDWI = (Green - NIR) / (Green + NIR)<br>
        <strong>Rango:</strong> -1 a 1<br>
        <strong>Interpretación:</strong>
        <ul>
            <li>< 0: Tierra, vegetación o agua ausente</li>
            <li>0 a 0.3: Agua turbia o con sedimentos</li>
            <li>> 0.3: Agua clara, cuerpo de agua definido</li>
        </ul>
        """)
    
    else:  # Turbidity
        render_info_card("""
        <strong>Turbidity Index (Red/Green Ratio)</strong><br><br>
        Este índice estima la turbidez del agua basándose en la relación entre las bandas roja y verde. 
        Valores más altos indican mayor carga de sedimentos suspendidos.<br><br>
        <strong>Fórmula:</strong> Turbidity = Red / Green<br>
        <strong>Rango:</strong> 0 a >2<br>
        <strong>Interpretación:</strong>
        <ul>
            <li>< 0.5: Baja turbidez, buena claridad del agua</li>
            <li>0.5 a 1.5: Turbidez moderada</li>
            <li>> 1.5: Alta turbidez, alta carga de sedimentos</li>
        </ul>
        """)
