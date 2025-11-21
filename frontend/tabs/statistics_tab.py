"""
Statistics Tab
"""
import streamlit as st
import pandas as pd
from frontend.components.charts import create_radar_chart, create_distribution_bar_chart
from frontend.components.ui import render_metric_card, render_info_card, render_statistics_table
from frontend.utils.config import COLORS


def render_statistics_tab(api_client, latest_data):
    """Render Statistics tab"""
    
    st.markdown("### 📊 Estadísticas Avanzadas")
    st.markdown("**Análisis estadístico completo de todos los índices espectrales**")
    
    stats = latest_data.get('statistics', {})
    
    if not stats:
        st.warning("⚠️ No hay estadísticas disponibles")
        return
    
    # Overall Metrics
    st.markdown("#### 🎯 Métricas Generales")
    
    cols = st.columns(4)
    
    for idx, (index_name, index_key) in enumerate([
        ("NDCI", "ndci"),
        ("NDWI", "ndwi"),
        ("Turbidez", "turbidity"),
        ("Área Total", "area")
    ]):
        with cols[idx]:
            if index_key in stats:
                if index_key == "area":
                    value = f"{stats[index_key]:,} px"
                else:
                    value = f"{stats[index_key].get('mean', 0):.3f}"
                
                render_metric_card(
                    index_name,
                    value,
                    "Valor medio" if index_key != "area" else "Pixels analizados",
                    COLORS['primary']
                )
    
    st.markdown("---")
    
    # Comparative Analysis
    st.markdown("#### 🔬 Análisis Comparativo")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("##### Comparación de Índices (Media vs Máximo)")
        
        # Prepare data for radar chart
        categories = []
        values_mean = []
        values_p90 = []
        
        for index_name, index_key in [("NDCI", "ndci"), ("NDWI", "ndwi"), ("Turbidez", "turbidity")]:
            if index_key in stats:
                categories.append(index_name)
                # Normalize to 0-1 range for radar chart
                mean_val = stats[index_key].get('mean', 0)
                max_val = stats[index_key].get('max', 0)  # Changed from p90 to max
                
                # Simple normalization (adjust based on typical ranges)
                if index_key == 'turbidity':
                    mean_norm = min(mean_val / 2.0, 1.0)
                    max_norm = min(max_val / 2.0, 1.0)
                else:
                    mean_norm = (mean_val + 1) / 2  # -1 to 1 -> 0 to 1
                    max_norm = (max_val + 1) / 2
                
                values_mean.append(mean_norm)
                values_p90.append(max_norm)  # Using max instead of p90
        
        if categories:
            fig = create_radar_chart(categories, values_mean, values_p90)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("##### Interpretación")
        render_info_card("""
        <strong>Gráfico de Radar:</strong><br><br>
        Compara los valores medios (azul) con los valores máximos (naranja).<br><br>
        <strong>Media:</strong> Representa el valor típico del índice.<br>
        <strong>Máximo:</strong> El valor más alto observado en el área.<br><br>
        Diferencias grandes indican alta variabilidad espacial.
        """)
    
    st.markdown("---")
    
    # Detailed Statistics Tables
    st.markdown("#### 📋 Tablas Estadísticas Detalladas")
    
    tabs = st.tabs(["NDCI", "NDWI", "Turbidez"])
    
    with tabs[0]:
        if 'ndci' in stats:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Estadísticas Descriptivas")
                # Create DataFrame for better display
                stats_df = pd.DataFrame({
                    'Métrica': ['Media', 'Mediana', 'Desv. Est.', 'Mínimo', 'Máximo'],
                    'Valor': [
                        f"{stats['ndci'].get('mean', 0):.4f}",
                        f"{stats['ndci'].get('median', 0):.4f}",
                        f"{stats['ndci'].get('std', 0):.4f}",
                        f"{stats['ndci'].get('min', 0):.4f}",
                        f"{stats['ndci'].get('max', 0):.4f}"
                    ]
                })
                st.dataframe(stats_df, hide_index=True, use_container_width=True)
            
            with col2:
                st.markdown("##### Distribución Percentil")
                # Only show available percentiles
                perc_df = pd.DataFrame({
                    'Percentil': ['P10 (Mínimo)', 'P50 (Mediana)', 'P90 (Máximo)'],
                    'Valor': [
                        f"{stats['ndci'].get('min', 0):.4f}",
                        f"{stats['ndci'].get('median', 0):.4f}",
                        f"{stats['ndci'].get('max', 0):.4f}"
                    ]
                })
                st.dataframe(perc_df, hide_index=True, use_container_width=True)
    
    with tabs[1]:
        if 'ndwi' in stats:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Estadísticas Descriptivas")
                stats_df = pd.DataFrame({
                    'Métrica': ['Media', 'Mediana', 'Desv. Est.', 'Mínimo', 'Máximo'],
                    'Valor': [
                        f"{stats['ndwi'].get('mean', 0):.4f}",
                        f"{stats['ndwi'].get('median', 0):.4f}",
                        f"{stats['ndwi'].get('std', 0):.4f}",
                        f"{stats['ndwi'].get('min', 0):.4f}",
                        f"{stats['ndwi'].get('max', 0):.4f}"
                    ]
                })
                st.dataframe(stats_df, hide_index=True, use_container_width=True)
            
            with col2:
                st.markdown("##### Distribución Percentil")
                perc_df = pd.DataFrame({
                    'Percentil': ['P10 (Mínimo)', 'P50 (Mediana)', 'P90 (Máximo)'],
                    'Valor': [
                        f"{stats['ndwi'].get('min', 0):.4f}",
                        f"{stats['ndwi'].get('median', 0):.4f}",
                        f"{stats['ndwi'].get('max', 0):.4f}"
                    ]
                })
                st.dataframe(perc_df, hide_index=True, use_container_width=True)
    
    with tabs[2]:
        if 'turbidity' in stats:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### Estadísticas Descriptivas")
                stats_df = pd.DataFrame({
                    'Métrica': ['Media', 'Mediana', 'Desv. Est.', 'Mínimo', 'Máximo'],
                    'Valor': [
                        f"{stats['turbidity'].get('mean', 0):.4f}",
                        f"{stats['turbidity'].get('median', 0):.4f}",
                        f"{stats['turbidity'].get('std', 0):.4f}",
                        f"{stats['turbidity'].get('min', 0):.4f}",
                        f"{stats['turbidity'].get('max', 0):.4f}"
                    ]
                })
                st.dataframe(stats_df, hide_index=True, use_container_width=True)
            
            with col2:
                st.markdown("##### Distribución Percentil")
                perc_df = pd.DataFrame({
                    'Percentil': ['P10 (Mínimo)', 'P50 (Mediana)', 'P90 (Máximo)'],
                    'Valor': [
                        f"{stats['turbidity'].get('min', 0):.4f}",
                        f"{stats['turbidity'].get('median', 0):.4f}",
                        f"{stats['turbidity'].get('max', 0):.4f}"
                    ]
                })
                st.dataframe(perc_df, hide_index=True, use_container_width=True)
    
    st.markdown("---")
    
    # Export options
    st.markdown("#### 💾 Exportar Estadísticas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Create CSV export
        export_data = []
        for index_key in ['ndci', 'ndwi', 'turbidity']:
            if index_key in stats:
                row = {'Index': index_key.upper()}
                row.update(stats[index_key])
                export_data.append(row)
        
        if export_data:
            df_export = pd.DataFrame(export_data)
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="⬇️ Descargar Estadísticas (CSV)",
                data=csv,
                file_name="titicaca_statistics.csv",
                mime="text/csv",
                use_container_width=True,
                key="stats_download_csv"
            )
    
    with col2:
        import json
        json_data = json.dumps(stats, indent=2)
        st.download_button(
            label="⬇️ Descargar Estadísticas (JSON)",
            data=json_data,
            file_name="titicaca_statistics.json",
            mime="application/json",
            use_container_width=True,
            key="stats_download_json"
        )
