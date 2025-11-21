"""
TITICACA SENTINEL - Plataforma de Monitoreo de Calidad del Agua
Sistema de monitoreo del Lago Titicaca usando imágenes satelitales Sentinel-2
"""

import streamlit as st
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import modules
from frontend.utils.config import COLORS, DEFAULT_CLOUD_COVERAGE, DEFAULT_DAYS
from frontend.utils.api_client import api_client
from frontend.utils.styles import get_custom_css
from frontend.utils.helpers import transform_statistics
from frontend.components.ui import render_header, render_metric_card, render_info_card
from frontend.tabs import (
    render_risk_tab,
    render_water_quality_tab,
    render_temporal_tab,
    render_statistics_tab,
    render_documentation_tab
)

# Page configuration
st.set_page_config(
    page_title="Titicaca Sentinel | Monitoreo de Calidad del Agua",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)


def render_sidebar(latest_data):
    """Render sidebar with system info and latest data"""
    with st.sidebar:
        st.markdown("### 📊 Última Actualización")
        
        if latest_data:
            # Image info
            image_date = latest_data.get('image_date', 'N/A')
            if image_date != 'N/A':
                try:
                    dt = datetime.fromisoformat(image_date.replace('Z', '+00:00'))
                    image_date = dt.strftime('%Y-%m-%d %H:%M UTC')
                except:
                    pass
            
            render_info_card(f"""
            <strong>Fecha:</strong> {image_date}<br>
            <strong>Satélite:</strong> Sentinel-2<br>
            <strong>Cobertura:</strong> {latest_data.get('cloud_coverage', 0):.1f}% nubes
            """)
            
            # Quick stats
            st.markdown("### 📈 Métricas Rápidas")
            
            stats = latest_data.get('statistics', {})
            
            if 'ndci' in stats:
                mean_ndci = stats['ndci'].get('mean', 0)
                render_metric_card(
                    "NDCI Promedio",
                    f"{mean_ndci:.3f}",
                    "Clorofila",
                    COLORS['primary']
                )
            
            if 'ndwi' in stats:
                mean_ndwi = stats['ndwi'].get('mean', 0)
                render_metric_card(
                    "NDWI Promedio",
                    f"{mean_ndwi:.3f}",
                    "Agua",
                    COLORS['secondary']
                )
            
            if 'turbidity' in stats:
                mean_turb = stats['turbidity'].get('mean', 0)
                render_metric_card(
                    "Turbidez Promedio",
                    f"{mean_turb:.3f}",
                    "Sedimentos",
                    COLORS['accent']
                )
        
        else:
            st.warning("⚠️ No hay datos disponibles")
        
        # System info
        st.markdown("---")
        st.markdown("### ℹ️ Sistema")
        st.markdown("""
        **Titicaca Sentinel v2.0**
        
        Monitoreo satelital de calidad del agua del Lago Titicaca.
        
        - 🛰️ Sentinel-2 MSI
        - 🌍 Google Earth Engine
        - 📡 Actualización cada 5 días
        - 🔬 Procesamiento automático
        """)
        
        st.markdown("---")
        st.markdown("*Desarrollado con FastAPI + Streamlit*")


def main():
    """Main application"""
    
    # Render header
    render_header()
    
    # Sidebar: cache controls
    with st.sidebar:
        if st.button("🗑️ Limpiar Caché", key="sidebar_clear_cache_button"):
            # Clear Streamlit cache and API client cache and session stored data
            try:
                st.cache_data.clear()
            except Exception:
                pass
            try:
                api_client.clear_cache()
            except Exception:
                pass
            if "latest_data" in st.session_state:
                st.session_state.pop("latest_data")
            st.success("✅ Caché limpiado")
            st.rerun()

    # Ensure we only load latest data once per Streamlit session
    latest_data = st.session_state.get("latest_data")
    if not latest_data:
        max_retries = 2
        last_error = None

        for attempt in range(max_retries):
            try:
                spinner_msg = "⏳ Procesando imágenes satelitales de los últimos 7 días... (2-3 minutos)"
                if attempt > 0:
                    spinner_msg = f"🔄 Reintentando ({attempt + 1}/{max_retries})... (esto puede tardar 2-3 minutos)"

                with st.spinner(spinner_msg):
                    data = api_client.get_latest_data(
                        cloud_coverage=DEFAULT_CLOUD_COVERAGE,
                        days=DEFAULT_DAYS
                    )

                # Check if we got data
                if data:
                    # Transform statistics to frontend format
                    if 'statistics' in data and data['statistics']:
                        data['statistics'] = transform_statistics(data['statistics'])
                    
                    latest_data = data
                    st.session_state["latest_data"] = latest_data
                    break
                else:
                    last_error = "El servidor retornó respuesta vacía"
                    if attempt < max_retries - 1:
                        st.warning(f"⚠️ Intento {attempt + 1} falló, reintentando...")

            except Exception as e:
                last_error = str(e)
                if attempt < max_retries - 1:
                    st.warning(f"⚠️ Intento {attempt + 1} falló: {last_error}")
                else:
                    st.error(f"❌ Error después de {max_retries} intentos: {last_error}")
    
    # Render sidebar
    render_sidebar(latest_data)
    
    # Check if data loaded
    if not latest_data:
        st.error("❌ Error al cargar los datos del servidor. Por favor, verifique que el backend esté activo.")
        st.info("💡 Ejecute el backend con: `./start_backend.sh`")
        
        # Show backend status
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Reintentar", key="retry_load_data_button"):
                st.rerun()
        with col2:
            with st.spinner("Verificando backend..."):
                health = api_client.health_check()
                if health:
                    st.success(f"✅ Backend activo: {health.get('status')}")
                else:
                    st.error("❌ Backend no responde")
        return
    
    # Main tabs
    tabs = st.tabs([
        "🎯 Evaluación de Riesgo",
        "💧 Calidad del Agua",
        "📅 Análisis Temporal",
        "📊 Estadísticas",
        "📚 Documentación"
    ])
    
    with tabs[0]:
        render_risk_tab(api_client, latest_data)
    
    with tabs[1]:
        render_water_quality_tab(api_client, latest_data)
    
    with tabs[2]:
        render_temporal_tab(api_client, latest_data)
    
    with tabs[3]:
        render_statistics_tab(api_client, latest_data)
    
    with tabs[4]:
        render_documentation_tab(api_client, latest_data)


if __name__ == "__main__":
    main()
