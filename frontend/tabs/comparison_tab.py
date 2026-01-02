"""
Temporal Comparison Tab - Compare two periods to detect changes
"""
import streamlit as st
from streamlit_folium import st_folium
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
from frontend.components.maps import create_map
from frontend.components.ui import render_metric_card, render_alert, render_info_card
from frontend.utils.config import COLORS, DEFAULT_CLOUD_COVERAGE
from frontend.utils.helpers import transform_statistics
import folium


def render_comparison_tab(api_client, latest_data):
    """Render Temporal Comparison tab"""
    
    st.markdown("### 🔄 Comparación Temporal")
    st.markdown("**Compare dos períodos para detectar cambios significativos en la calidad del agua**")
    
    st.markdown("---")
    
    # Period selectors with presets and calendar
    st.markdown("#### ⚙️ Configuración de Períodos")
    
    # Selection mode
    selection_mode = st.radio(
        "Modo de Selección:",
        ["🗓️ Usar Calendario (Fechas Específicas)", "📊 Usar Presets Rápidos", "⚙️ Configuración Manual"],
        key="comparison_selection_mode",
        horizontal=True
    )
    
    st.markdown("---")
    
    # Initialize today's date
    today = datetime.now().date()
    
    if selection_mode == "🗓️ Usar Calendario (Fechas Específicas)":
        st.markdown("**📅 Seleccione los rangos de fechas a comparar:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 🟢 Período Reciente")
            
            period1_end = st.date_input(
                "Fecha Final (más reciente):",
                value=today,
                max_value=today,
                min_value=today - timedelta(days=365),
                help="Último día del período reciente",
                key="period1_end_date"
            )
            
            period1_start = st.date_input(
                "Fecha Inicial:",
                value=period1_end - timedelta(days=7),
                max_value=period1_end,
                min_value=today - timedelta(days=365),
                help="Primer día del período reciente",
                key="period1_start_date"
            )
            
            period1_days_calc = (period1_end - period1_start).days + 1
            st.info(f"📊 Duración: **{period1_days_calc} días**")
        
        with col2:
            st.markdown("##### 🔵 Período Anterior")
            
            period2_end = st.date_input(
                "Fecha Final:",
                value=today - timedelta(days=30),
                max_value=today,
                min_value=today - timedelta(days=365),
                help="Último día del período anterior",
                key="period2_end_date"
            )
            
            period2_start = st.date_input(
                "Fecha Inicial:",
                value=period2_end - timedelta(days=7),
                max_value=period2_end,
                min_value=today - timedelta(days=365),
                help="Primer día del período anterior",
                key="period2_start_date"
            )
            
            period2_days_calc = (period2_end - period2_start).days + 1
            st.info(f"📊 Duración: **{period2_days_calc} días**")
        
        # Calculate parameters for API
        period1_days = period1_days_calc
        period2_days = period2_days_calc
        offset_days = (today - period2_end).days
        
        # Visual timeline
        st.markdown("---")
        st.markdown("**📈 Línea de Tiempo de Comparación:**")
        
        col_timeline = st.columns([1, 1, 1])
        with col_timeline[0]:
            st.markdown(f"""
            <div style="background-color: #e3f2fd; padding: 15px; border-radius: 10px; text-align: center;">
                <strong>🔵 Período Anterior</strong><br>
                {period2_start.strftime('%d/%m/%Y')} → {period2_end.strftime('%d/%m/%Y')}<br>
                <small>{period2_days} días</small>
            </div>
            """, unsafe_allow_html=True)
        
        with col_timeline[1]:
            gap_days = (period1_start - period2_end).days
            st.markdown(f"""
            <div style="background-color: #fff3e0; padding: 15px; border-radius: 10px; text-align: center;">
                <strong>⏸️ Separación</strong><br>
                {gap_days} días entre períodos
            </div>
            """, unsafe_allow_html=True)
        
        with col_timeline[2]:
            st.markdown(f"""
            <div style="background-color: #e8f5e9; padding: 15px; border-radius: 10px; text-align: center;">
                <strong>🟢 Período Reciente</strong><br>
                {period1_start.strftime('%d/%m/%Y')} → {period1_end.strftime('%d/%m/%Y')}<br>
                <small>{period1_days} días</small>
            </div>
            """, unsafe_allow_html=True)
    
    elif selection_mode == "📊 Usar Presets Rápidos":
        # Preset buttons for common comparisons
        st.markdown("**Seleccione una comparación predefinida:**")
        preset_cols = st.columns(4)
        
        with preset_cols[0]:
            if st.button("📅 Esta semana vs Hace 1 mes", use_container_width=True, key="preset_week_month"):
                st.session_state.comparison_period1_days = 7
                st.session_state.comparison_period2_days = 7
                st.session_state.comparison_offset_days = 30
                st.session_state.pop("comparison_data", None)
                st.rerun()
        
        with preset_cols[1]:
            if st.button("📊 Últimos 7 vs 14 días", use_container_width=True, key="preset_7_14"):
                st.session_state.comparison_period1_days = 7
                st.session_state.comparison_period2_days = 7
                st.session_state.comparison_offset_days = 14
                st.session_state.pop("comparison_data", None)
                st.rerun()
        
        with preset_cols[2]:
            if st.button("🔄 Mes actual vs anterior", use_container_width=True, key="preset_month_month"):
                st.session_state.comparison_period1_days = 30
                st.session_state.comparison_period2_days = 30
                st.session_state.comparison_offset_days = 60
                st.session_state.pop("comparison_data", None)
                st.rerun()
        
        with preset_cols[3]:
            if st.button("📈 Trimestral (3 meses)", use_container_width=True, key="preset_quarterly"):
                st.session_state.comparison_period1_days = 30
                st.session_state.comparison_period2_days = 30
                st.session_state.comparison_offset_days = 90
                st.session_state.pop("comparison_data", None)
                st.rerun()
        
        # Use session state values or defaults
        period1_days = st.session_state.get("comparison_period1_days", 7)
        period2_days = st.session_state.get("comparison_period2_days", 7)
        offset_days = st.session_state.get("comparison_offset_days", 30)
        
        # Show current selection
        st.info(f"""
        **📌 Comparación configurada:**
        - **Período Reciente**: Últimos {period1_days} días (hoy hacia atrás)
        - **Período Anterior**: {period2_days} días comenzando hace {offset_days} días
        - **Separación temporal**: ~{offset_days - period2_days} días entre períodos
        """)
    
    else:  # Manual configuration
        st.markdown("**Configuración Personalizada (días):**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            period1_days = st.number_input(
                "📍 Período Reciente (días):",
                min_value=3,
                max_value=30,
                value=st.session_state.get("comparison_period1_days", 7),
                help="Número de días para el período más reciente",
                key="comparison_period1_days"
            )
        
        with col2:
            period2_days = st.number_input(
                "📍 Período Anterior (días):",
                min_value=3,
                max_value=30,
                value=st.session_state.get("comparison_period2_days", 7),
                help="Número de días para el período de comparación",
                key="comparison_period2_days"
            )
        
        with col3:
            offset_days = st.number_input(
                "⏪ Desplazamiento (días atrás):",
                min_value=7,
                max_value=365,
                value=st.session_state.get("comparison_offset_days", 30),
                help="Cuántos días atrás comenzar el período anterior",
                key="comparison_offset_days"
            )
        
        # Visual explanation
        st.info(f"""
        **📌 Comparación configurada:**
        - **Período Reciente**: Últimos {period1_days} días (hoy hacia atrás)
        - **Período Anterior**: {period2_days} días comenzando hace {offset_days} días
        - **Separación temporal**: ~{offset_days - period2_days} días entre períodos
        """)
    
    st.markdown("---")
    
    # Load comparison data button
    if st.button("🔍 Ejecutar Comparación", use_container_width=True, key="run_comparison_button"):
        st.session_state.pop("comparison_data", None)  # Clear cache
    
    # Load comparison data
    comparison_data = st.session_state.get("comparison_data")
    
    if not comparison_data:
        with st.spinner(f"Comparando períodos... (procesando {period1_days + period2_days} días de datos, puede tardar 3-5 minutos)"):
            try:
                comparison_data = api_client.get_comparison(
                    period1_days=period1_days,
                    period2_days=period2_days,
                    period2_offset=offset_days,
                    cloud_coverage=DEFAULT_CLOUD_COVERAGE
                )
                
                if comparison_data:
                    # Transform statistics
                    if 'period1' in comparison_data and 'statistics' in comparison_data['period1']:
                        comparison_data['period1']['statistics'] = transform_statistics(
                            comparison_data['period1']['statistics']
                        )
                    if 'period2' in comparison_data and 'statistics' in comparison_data['period2']:
                        comparison_data['period2']['statistics'] = transform_statistics(
                            comparison_data['period2']['statistics']
                        )
                    
                    st.session_state["comparison_data"] = comparison_data
            except Exception as e:
                render_alert(f"❌ Error al comparar períodos: {str(e)}", "danger")
                return
    
    if not comparison_data:
        render_info_card("""
        <strong>Instrucciones:</strong><br><br>
        1. Configure los períodos a comparar (ej: últimos 7 días vs hace 30 días)<br>
        2. Haga clic en "Ejecutar Comparación"<br>
        3. Revise las alertas, cambios y mapas comparativos<br><br>
        <strong>Casos de uso:</strong><br>
        - Detectar florecimientos algales estacionales<br>
        - Monitorear impacto de eventos climáticos<br>
        - Evaluar tendencias de turbidez<br>
        - Identificar áreas con cambios críticos
        """)
        return
    
    # Extract data
    period1 = comparison_data.get('period1', {})
    period2 = comparison_data.get('period2', {})
    changes = comparison_data.get('changes', {})
    percent_changes = comparison_data.get('percent_changes', {})
    alerts = comparison_data.get('alerts', [])
    
    # Show alerts if any
    if alerts:
        st.markdown("#### 🚨 Alertas de Cambios Significativos")
        
        for alert in alerts:
            severity = alert.get('severity', 'medium')
            color = COLORS['danger'] if severity == 'high' else COLORS['warning']
            render_alert(
                f"**{alert.get('index')}**: {alert.get('message')} ({alert.get('change')})",
                "danger" if severity == 'high' else "warning"
            )
        
        st.markdown("---")
    
    # Period headers
    st.markdown("#### 📊 Comparación de Períodos")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"##### 🟢 Período Reciente")
        st.markdown(f"**Fecha:** {period1.get('date', 'N/A')}")
    
    with col2:
        st.markdown(f"##### 🔵 Período Anterior")
        st.markdown(f"**Fecha:** {period2.get('date', 'N/A')}")
    
    # Metrics comparison
    st.markdown("##### Cambios en Índices Clave")
    
    cols = st.columns(4)
    
    metrics = [
        ("NDCI", "NDCI_mean", "Clorofila"),
        ("NDWI", "NDWI_mean", "Agua"),
        ("Turbidez", "Turbidity_mean", "Sedimentos"),
        ("Chl-a", "Chla_approx_mean", "Clorofila-a")
    ]
    
    for idx, (name, key, subtitle) in enumerate(metrics):
        with cols[idx]:
            if key in percent_changes:
                pct_change = percent_changes[key]
                change_val = changes.get(key, 0)
                
                # Determine color based on change direction
                if abs(pct_change) < 10:
                    color = COLORS['success']
                    icon = "↔️"
                elif pct_change > 0:
                    color = COLORS['warning']
                    icon = "↗️"
                else:
                    color = COLORS['info']
                    icon = "↘️"
                
                render_metric_card(
                    name,
                    f"{icon} {pct_change:+.1f}%",
                    f"{subtitle} ({change_val:+.4f})",
                    color
                )
    
    st.markdown("---")
    
    # Side-by-side maps
    st.markdown("#### 🗺️ Mapas Comparativos")
    
    # Index selector for maps
    map_index = st.selectbox(
        "Seleccionar índice para visualizar:",
        ["NDCI (Clorofila)", "NDWI (Agua)", "Turbidez"],
        help="Elija el índice a comparar visualmente",
        key="comparison_map_selector"
    )
    
    index_mapping = {
        "NDCI (Clorofila)": 'ndci',
        "NDWI (Agua)": 'ndwi',
        "Turbidez": 'turbidity'
    }
    
    selected_index = index_mapping[map_index]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"##### {map_index} - Período Reciente")
        tile_url1 = period1.get('tile_urls', {}).get(selected_index)
        
        if tile_url1:
            m1 = create_map()
            folium.TileLayer(
                tiles=tile_url1,
                attr='Google Earth Engine',
                name=f"{map_index} - Reciente",
                overlay=True,
                control=True,
                opacity=0.7
            ).add_to(m1)
            st_folium(m1, width=None, height=400, key=f"comparison_map1_{selected_index}")
        else:
            st.warning("No hay datos de tile disponibles para este índice")
    
    with col2:
        st.markdown(f"##### {map_index} - Período Anterior")
        tile_url2 = period2.get('tile_urls', {}).get(selected_index)
        
        if tile_url2:
            m2 = create_map()
            folium.TileLayer(
                tiles=tile_url2,
                attr='Google Earth Engine',
                name=f"{map_index} - Anterior",
                overlay=True,
                control=True,
                opacity=0.7
            ).add_to(m2)
            st_folium(m2, width=None, height=400, key=f"comparison_map2_{selected_index}")
        else:
            st.warning("No hay datos de tile disponibles para este índice")
    
    st.markdown("---")
    
    # Detailed statistics comparison chart
    st.markdown("#### 📈 Gráfico de Cambios Detallado")
    
    # Prepare data for chart
    stats1 = period1.get('statistics', {})
    stats2 = period2.get('statistics', {})
    
    indices_to_plot = ['ndci', 'ndwi', 'turbidity']
    index_names = ['NDCI', 'NDWI', 'Turbidez']
    
    values_period1 = []
    values_period2 = []
    
    for idx_key in indices_to_plot:
        if idx_key in stats1:
            values_period1.append(stats1[idx_key].get('mean', 0))
        else:
            values_period1.append(0)
        
        if idx_key in stats2:
            values_period2.append(stats2[idx_key].get('mean', 0))
        else:
            values_period2.append(0)
    
    # Create grouped bar chart
    fig = go.Figure(data=[
        go.Bar(
            name=f'Reciente ({period1.get("date", "")})',
            x=index_names,
            y=values_period1,
            marker_color=COLORS['primary']
        ),
        go.Bar(
            name=f'Anterior ({period2.get("date", "")})',
            x=index_names,
            y=values_period2,
            marker_color=COLORS['secondary']
        )
    ])
    
    fig.update_layout(
        title='Comparación de Valores Medios por Índice',
        xaxis_title='Índice Espectral',
        yaxis_title='Valor',
        barmode='group',
        template='plotly_white',
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Interpretation and recommendations
    st.markdown("#### 💡 Interpretación y Recomendaciones")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Cambios Detectados")
        
        if not alerts:
            st.success("✅ No se detectaron cambios significativos (>20%) en los índices monitoreados.")
        else:
            st.warning(f"⚠️ Se detectaron **{len(alerts)}** cambios significativos que requieren atención.")
            
            for alert in alerts[:3]:  # Show top 3
                st.markdown(f"- **{alert.get('index')}**: {alert.get('change')}")
    
    with col2:
        st.markdown("##### Recomendaciones")
        
        # Generate recommendations based on alerts
        if any(alert.get('index') == 'NDCI' for alert in alerts):
            st.markdown("🔬 **NDCI**: Considere muestreo de clorofila en campo")
        
        if any(alert.get('index') == 'Turbidity' for alert in alerts):
            st.markdown("🌊 **Turbidez**: Revisar fuentes de sedimentación")
        
        if any(alert.get('index') == 'NDWI' for alert in alerts):
            st.markdown("💧 **NDWI**: Verificar niveles de agua y vegetación")
        
        if not alerts:
            st.markdown("📊 Continuar con monitoreo de rutina")
            st.markdown("📅 Próxima comparación sugerida: 7-14 días")
