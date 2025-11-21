"""
Temporal Analysis Tab
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
from frontend.components.charts import create_time_series_chart, create_single_metric_chart
from frontend.components.ui import render_metric_card, render_info_card, render_alert
from frontend.utils.config import COLORS, LAKE_INFO


def render_temporal_tab(api_client, latest_data):
    """Render Temporal Analysis tab"""
    
    st.markdown("### 📅 Análisis Temporal")
    st.markdown("**Evolución de indicadores de calidad del agua en el tiempo**")
    
    # Date range selector
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        start_date = st.date_input(
            "Fecha inicial:",
            value=datetime.now() - timedelta(days=365),
            max_value=datetime.now(),
            help="Seleccione la fecha de inicio del análisis",
            key="temporal_start_date"
        )
    
    with col2:
        end_date = st.date_input(
            "Fecha final:",
            value=datetime.now(),
            max_value=datetime.now(),
            help="Seleccione la fecha de fin del análisis",
            key="temporal_end_date"
        )
    
    with col3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🔄 Actualizar", use_container_width=True, key="temporal_update_button"):
            st.rerun()
    
    # Location selector
    st.markdown("#### 📍 Ubicación del Punto de Muestreo")
    
    col1, col2 = st.columns(2)
    
    with col1:
        lat = st.number_input(
            "Latitud:",
            min_value=LAKE_INFO['bounds']['south'],
            max_value=LAKE_INFO['bounds']['north'],
            value=LAKE_INFO['center']['lat'],
            step=0.01,
            format="%.4f",
            help="Latitud del punto a analizar",
            key="temporal_latitude"
        )
    
    with col2:
        lon = st.number_input(
            "Longitud:",
            min_value=LAKE_INFO['bounds']['west'],
            max_value=LAKE_INFO['bounds']['east'],
            value=LAKE_INFO['center']['lng'],
            step=0.01,
            format="%.4f",
            help="Longitud del punto a analizar",
            key="temporal_longitude"
        )
    
    st.markdown("---")
    
    # Load time series data
    with st.spinner("Cargando serie temporal..."):
        ts_data = api_client.get_time_series(
            start_date=start_date.isoformat(),
            end_date=end_date.isoformat(),
            lat=lat,
            lon=lon
        )
    
    if not ts_data or 'data' not in ts_data:
        render_alert("⚠️ No se encontraron datos para el período y ubicación seleccionados", "warning")
        return
    
    # Parse time series
    ts_list = ts_data['data']
    
    if not ts_list:
        render_alert("📭 No hay datos disponibles para este rango de fechas", "info")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame(ts_list)
    df['Date'] = pd.to_datetime(df['date'])
    df = df.sort_values('Date')
    
    # Summary statistics
    st.markdown("#### 📊 Resumen del Período")
    
    cols = st.columns(4)
    
    with cols[0]:
        n_images = len(df)
        render_metric_card("Imágenes", str(n_images), "Escenas analizadas", COLORS['primary'])
    
    with cols[1]:
        days_span = (df['Date'].max() - df['Date'].min()).days
        render_metric_card("Período", f"{days_span} días", "Rango temporal", COLORS['secondary'])
    
    with cols[2]:
        mean_ndci = df['ndci'].mean()
        render_metric_card("NDCI Promedio", f"{mean_ndci:.3f}", "Clorofila media", COLORS['success'])
    
    with cols[3]:
        mean_turb = df['turbidity'].mean()
        render_metric_card("Turbidez Promedio", f"{mean_turb:.3f}", "Turbidez media", COLORS['accent'])
    
    st.markdown("---")
    
    # Multi-index chart
    st.markdown("#### 📈 Evolución de Índices")
    
    if len(df) > 0:
        fig = create_time_series_chart(df, lat, lon)
        st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Individual metric trends
    st.markdown("#### 🔍 Análisis Individual")
    
    tabs = st.tabs(["NDCI", "NDWI", "Turbidez"])
    
    with tabs[0]:
        if 'ndci' in df.columns:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                fig = create_single_metric_chart(df, 'ndci', COLORS['primary'])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Estadísticas NDCI:**")
                render_info_card(f"""
                Media: {df['ndci'].mean():.3f}<br>
                Mediana: {df['ndci'].median():.3f}<br>
                Desv. Est.: {df['ndci'].std():.3f}<br>
                Mínimo: {df['ndci'].min():.3f}<br>
                Máximo: {df['ndci'].max():.3f}
                """)
    
    with tabs[1]:
        if 'ndwi' in df.columns:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                fig = create_single_metric_chart(df, 'ndwi', COLORS['secondary'])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Estadísticas NDWI:**")
                render_info_card(f"""
                Media: {df['ndwi'].mean():.3f}<br>
                Mediana: {df['ndwi'].median():.3f}<br>
                Desv. Est.: {df['ndwi'].std():.3f}<br>
                Mínimo: {df['ndwi'].min():.3f}<br>
                Máximo: {df['ndwi'].max():.3f}
                """)
    
    with tabs[2]:
        if 'turbidity' in df.columns:
            col1, col2 = st.columns([3, 1])
            
            with col1:
                fig = create_single_metric_chart(df, 'turbidity', COLORS['accent'])
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Estadísticas Turbidez:**")
                render_info_card(f"""
                Media: {df['turbidity'].mean():.3f}<br>
                Mediana: {df['turbidity'].median():.3f}<br>
                Desv. Est.: {df['turbidity'].std():.3f}<br>
                Mínimo: {df['turbidity'].min():.3f}<br>
                Máximo: {df['turbidity'].max():.3f}
                """)
    
    st.markdown("---")
    
    # Data table
    with st.expander("📋 Ver Datos Tabulares"):
        st.dataframe(
            df[['Date', 'ndci', 'ndwi', 'turbidity']].style.format({
                'ndci': '{:.4f}',
                'ndwi': '{:.4f}',
                'turbidity': '{:.4f}'
            }),
            use_container_width=True,
            height=400
        )
        
        # Download button
        csv = df.to_csv(index=False)
        st.download_button(
            label="⬇️ Descargar CSV",
            data=csv,
            file_name=f"titicaca_timeseries_{start_date}_{end_date}.csv",
            mime="text/csv"
        )
