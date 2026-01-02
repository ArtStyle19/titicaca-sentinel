"""
Prediction Tab - ML-based time series forecasting with Prophet
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
from frontend.components.ui import render_metric_card, render_alert, render_info_card
from frontend.utils.config import COLORS, DEFAULT_CLOUD_COVERAGE


def render_prediction_tab(api_client, latest_data):
    """Render ML Prediction tab with Prophet forecasting"""
    
    st.markdown("### 🔮 Predicción con Machine Learning")
    st.markdown("**Predicción de series temporales usando Prophet para anticipar cambios en la calidad del agua**")
    
    st.markdown("---")
    
    # Configuration section
    st.markdown("#### ⚙️ Configuración de Predicción")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        metric = st.selectbox(
            "📊 Métrica a Predecir:",
            options=["ndci", "ndwi", "turbidity", "chla_approx"],
            format_func=lambda x: {
                "ndci": "NDCI - Clorofila (Blooms Algales)",
                "ndwi": "NDWI - Índice de Agua",
                "turbidity": "Turbidez (Sedimentos)",
                "chla_approx": "Clorofila-a (µg/L)"
            }[x],
            help="Seleccione la métrica que desea predecir",
            key="prediction_metric"
        )
    
    with col2:
        forecast_days = st.slider(
            "🔭 Días a Predecir:",
            min_value=1,
            max_value=14,
            value=7,
            help="Número de días hacia el futuro",
            key="prediction_forecast_days"
        )
    
    with col3:
        historical_days = st.slider(
            "📅 Datos Históricos (días):",
            min_value=30,
            max_value=180,
            value=60,  # Reducido de 90 a 60 para evitar timeouts
            step=30,
            help="Cantidad de datos históricos para entrenar el modelo. Más días = mejor precisión pero más tiempo de procesamiento",
            key="prediction_historical_days"
        )
    
    # Info about the configuration
    st.info(f"""
    **📌 Configuración actual:**
    - **Métrica:** {metric.upper()} 
    - **Histórico:** Últimos {historical_days} días
    - **Predicción:** Próximos {forecast_days} días
    - **Modelo:** Facebook Prophet (Series Temporales)
    """)
    
    # Generate prediction button
    if st.button("🤖 Generar Predicción", use_container_width=True, type="primary", key="run_prediction_button"):
        st.session_state.pop("prediction_data", None)  # Clear cache
    
    # Load prediction data
    prediction_data = st.session_state.get("prediction_data")
    
    if not prediction_data:
        # Calculate estimated time based on historical days
        estimated_samples = (historical_days // 14) if historical_days >= 60 else (historical_days // 7)
        estimated_minutes = max(5, estimated_samples * 1.5)  # ~1.5 min per GEE call
        
        with st.spinner(f"🧠 Procesando predicción... Esto puede tomar {int(estimated_minutes)} minutos\n\n"
                       f"📊 Recopilando ~{estimated_samples} muestras de datos históricos de GEE...\n"
                       f"🤖 Entrenando modelo Prophet...\n"
                       f"⏳ Por favor espere..."):
            try:
                prediction_data = api_client.get_prediction(
                    metric=metric,
                    historical_days=historical_days,
                    forecast_days=forecast_days,
                    cloud_coverage=DEFAULT_CLOUD_COVERAGE
                )
                
                if prediction_data:
                    st.session_state["prediction_data"] = prediction_data
                    st.success("✅ Predicción generada exitosamente!")
            except Exception as e:
                error_msg = str(e)
                if "TIMEOUT" in error_msg:
                    render_alert(
                        f"⏱️ **Timeout:** El procesamiento tomó más de 15 minutos.\n\n"
                        f"**💡 Sugerencias:**\n"
                        f"- Reducir días históricos a 60 o 30 días\n"
                        f"- Intentar nuevamente (puede usar datos en caché)\n"
                        f"- Verificar que el backend esté funcionando",
                        "danger"
                    )
                else:
                    render_alert(f"❌ Error al generar predicción: {error_msg}", "danger")
                st.info("💡 Asegúrese de que Prophet esté instalado: `pip install prophet`")
                return
    
    if not prediction_data:
        # Show info card
        render_info_card("""
        <strong>🔮 Sobre la Predicción con Machine Learning:</strong><br><br>
        
        Este sistema utiliza <strong>Facebook Prophet</strong>, un modelo de ML especializado en series temporales
        que puede detectar tendencias, estacionalidad y cambios de régimen.<br><br>
        
        <strong>¿Qué puede predecir?</strong><br>
        • Florecimientos algales con 7 días de anticipación<br>
        • Incremento de turbidez por eventos de lluvia<br>
        • Cambios en niveles de agua (NDWI)<br>
        • Concentración de clorofila-a (eutrofización)<br><br>
        
        <strong>Ventajas del modelo Prophet:</strong><br>
        ✅ Detecta tendencias automáticamente<br>
        ✅ Maneja datos faltantes (nubes, gaps)<br>
        ✅ Proporciona intervalos de confianza (95%)<br>
        ✅ No requiere datos etiquetados<br><br>
        
        <strong>Casos de uso prácticos:</strong><br>
        🎯 <strong>Gestión proactiva:</strong> Preparar equipos antes de eventos críticos<br>
        🎯 <strong>Alertas tempranas:</strong> Notificar autoridades con días de anticipación<br>
        🎯 <strong>Planificación:</strong> Optimizar muestreos in-situ según predicciones<br>
        🎯 <strong>Investigación:</strong> Validar modelos con observaciones futuras
        """)
        return
    
    # Extract prediction data
    historical = prediction_data.get('historical_data', [])
    predictions = prediction_data.get('predictions', [])
    model_metrics = prediction_data.get('model_metrics', {})
    alerts = prediction_data.get('alerts', [])
    
    # Warning for insufficient data
    data_points = model_metrics.get('data_points', 0)
    if data_points < 10:
        st.warning(f"""
        ⚠️ **Advertencia: Datos históricos limitados ({data_points} puntos)**
        
        El modelo fue entrenado con pocos datos, lo que puede afectar la precisión de las predicciones.
        
        **Recomendaciones:**
        - Aumentar los días históricos a 90 o 120
        - Las predicciones son orientativas, úselas con precaución
        - Considere esperar a que se acumulen más datos en el sistema
        """)
    
    # Display alerts if any
    if alerts:
        st.markdown("#### 🚨 Alertas Predictivas")
        st.warning(f"⚠️ Se detectaron **{len(alerts)}** alertas en las predicciones:")
        
        for alert in alerts:
            severity = alert.get('severity', 'medium')
            alert_type = "danger" if severity == "critical" else "warning"
            render_alert(
                f"**{alert.get('date')}**: {alert.get('message')}<br>"
                f"<small>💡 {alert.get('recommendation')}</small>",
                alert_type
            )
        
        st.markdown("---")
    
    # Model performance metrics
    st.markdown("#### 📈 Desempeño del Modelo")
    
    cols = st.columns(4)
    
    mae = model_metrics.get('mae', 0)
    rmse = model_metrics.get('rmse', 0)
    mape = model_metrics.get('mape', 0)
    data_points = model_metrics.get('data_points', 0)
    
    with cols[0]:
        # Calculate R² approximation from MAE and data variance
        # This gives a more intuitive "quality" metric
        if mae < 0.05:
            quality = "Excelente"
            quality_pct = 95
            color = COLORS['success']
        elif mae < 0.1:
            quality = "Buena"
            quality_pct = 85
            color = COLORS['success']
        elif mae < 0.2:
            quality = "Moderada"
            quality_pct = 70
            color = COLORS['warning']
        else:
            quality = "Baja"
            quality_pct = 50
            color = COLORS['danger']
        
        render_metric_card(
            "Calidad",
            f"{quality_pct}%",
            quality,
            color
        )
    
    with cols[1]:
        render_metric_card(
            "MAE",
            f"{mae:.4f}",
            "Error Promedio",
            COLORS['info']
        )
    
    with cols[2]:
        render_metric_card(
            "RMSE",
            f"{rmse:.4f}",
            "Desviación",
            COLORS['info']
        )
    
    with cols[3]:
        render_metric_card(
            "Datos",
            f"{data_points}",
            "Puntos de entrenamiento",
            COLORS['primary']
        )
    
    st.markdown("---")
    
    # Main prediction chart
    st.markdown("#### 📊 Gráfico de Predicción")
    
    # Prepare data for plotting
    hist_df = pd.DataFrame(historical)
    hist_df['date'] = pd.to_datetime(hist_df['date'])
    
    pred_df = pd.DataFrame(predictions)
    pred_df['date'] = pd.to_datetime(pred_df['date'])
    
    # Create interactive Plotly chart
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=hist_df['date'],
        y=hist_df['value'],
        mode='lines+markers',
        name='Datos Históricos',
        line=dict(color=COLORS['primary'], width=2),
        marker=dict(size=6),
        hovertemplate='<b>Fecha:</b> %{x|%Y-%m-%d}<br><b>Valor:</b> %{y:.4f}<extra></extra>'
    ))
    
    # Predicted values
    fig.add_trace(go.Scatter(
        x=pred_df['date'],
        y=pred_df['predicted_value'],
        mode='lines+markers',
        name='Predicción',
        line=dict(color=COLORS['warning'], width=3, dash='dash'),
        marker=dict(size=8, symbol='diamond'),
        hovertemplate='<b>Fecha:</b> %{x|%Y-%m-%d}<br><b>Predicción:</b> %{y:.4f}<extra></extra>'
    ))
    
    # Confidence interval (upper bound)
    fig.add_trace(go.Scatter(
        x=pred_df['date'],
        y=pred_df['upper_bound'],
        mode='lines',
        name='Límite Superior (95%)',
        line=dict(width=0),
        showlegend=False,
        hoverinfo='skip'
    ))
    
    # Confidence interval (lower bound + fill)
    fig.add_trace(go.Scatter(
        x=pred_df['date'],
        y=pred_df['lower_bound'],
        mode='lines',
        name='Intervalo de Confianza (95%)',
        line=dict(width=0),
        fill='tonexty',
        fillcolor='rgba(255, 193, 7, 0.2)',
        hovertemplate='<b>Intervalo:</b> %{y:.4f} - ' + pred_df['upper_bound'].apply(lambda x: f'{x:.4f}').iloc[0] + '<extra></extra>'
    ))
    
    # Update layout
    metric_names = {
        'ndci': 'NDCI (Índice de Clorofila)',
        'ndwi': 'NDWI (Índice de Agua)',
        'turbidity': 'Turbidez Relativa',
        'chla_approx': 'Clorofila-a (µg/L)'
    }
    
    fig.update_layout(
        title=f'Predicción de {metric_names.get(metric, metric.upper())} - Próximos {forecast_days} Días',
        xaxis_title='Fecha',
        yaxis_title='Valor',
        hovermode='x unified',
        template='plotly_white',
        height=500,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    # Add vertical line manually as shape (avoids Timestamp issues)
    if len(hist_df) > 0 and len(pred_df) > 0:
        # Get the last historical date as string
        last_hist = hist_df['date'].iloc[-1]
        first_pred = pred_df['date'].iloc[0]
        
        # Add shape between historical and prediction
        fig.add_shape(
            type="line",
            x0=last_hist, x1=last_hist,
            y0=0, y1=1,
            yref="paper",
            line=dict(color="gray", width=2, dash="dot"),
        )
        
        # Add annotation
        fig.add_annotation(
            x=last_hist,
            y=1,
            yref="paper",
            text="← Histórico | Predicción →",
            showarrow=False,
            yshift=10,
            font=dict(size=10, color="gray")
        )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.markdown("---")
    
    # Detailed predictions table
    st.markdown("#### 📅 Predicciones Detalladas")
    
    # Format predictions for table
    table_data = []
    for pred in predictions:
        table_data.append({
            'Fecha': pred['date'],
            'Valor Predicho': f"{pred['predicted_value']:.4f}",
            'Límite Inferior': f"{pred['lower_bound']:.4f}",
            'Límite Superior': f"{pred['upper_bound']:.4f}",
            'Confianza': f"{pred['confidence']*100:.0f}%"
        })
    
    if table_data:
        pred_table_df = pd.DataFrame(table_data)
        st.dataframe(pred_table_df, use_container_width=True, hide_index=True)
    
    st.markdown("---")
    
    # Interpretation and recommendations
    st.markdown("#### 💡 Interpretación y Uso")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 📊 Sobre las Predicciones")
        
        st.markdown(f"""
        **Modelo entrenado con:**
        - {data_points} puntos de datos históricos
        - Últimos {historical_days} días
        - Error promedio (MAE): {mae:.4f}
        
        **Intervalo de confianza:**
        - 95% de probabilidad de que el valor real esté dentro del rango sombreado
        - Rangos más amplios indican mayor incertidumbre
        
        **Limitaciones:**
        - Las predicciones asumen continuidad de patrones históricos
        - Eventos extremos (tormentas, contaminación súbita) pueden no ser capturados
        - Precisión disminuye con horizontes de predicción más largos
        """)
    
    with col2:
        st.markdown("##### 🎯 Cómo Usar estas Predicciones")
        
        if len(alerts) > 0:
            st.markdown("**⚠️ Acciones Recomendadas:**")
            for i, alert in enumerate(alerts[:3], 1):
                st.markdown(f"{i}. {alert.get('recommendation')}")
        else:
            st.markdown("""
            **✅ No se prevén eventos críticos**
            
            Recomendaciones de rutina:
            1. Continuar con monitoreo regular
            2. Validar predicciones con observaciones reales
            3. Actualizar modelo semanalmente con nuevos datos
            4. Documentar desviaciones para mejorar el modelo
            """)
        
        st.markdown("""
        **💡 Mejores prácticas:**
        - Combinar con muestreos in-situ para validación
        - Usar predicciones para planificar recursos
        - Activar alertas automáticas cuando se superen umbrales
        - Generar predicciones semanalmente
        """)
    
    st.markdown("---")
    
    # Export options
    st.markdown("#### 💾 Exportar Predicciones")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # CSV export
        if table_data:
            csv_df = pd.DataFrame(table_data)
            csv_str = csv_df.to_csv(index=False)
            st.download_button(
                label="📥 Descargar CSV",
                data=csv_str,
                file_name=f"prediccion_{metric}_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_prediction_csv"
            )
    
    with col2:
        # JSON export
        import json
        json_str = json.dumps(prediction_data, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Descargar JSON",
            data=json_str,
            file_name=f"prediccion_{metric}_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
            key="download_prediction_json"
        )
    
    with col3:
        # Report export
        report_md = f"""# Reporte de Predicción - {metric_names.get(metric, metric.upper())}

**Generado:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Configuración
- **Métrica:** {metric.upper()}
- **Datos históricos:** {historical_days} días
- **Horizonte de predicción:** {forecast_days} días

## Desempeño del Modelo
- **MAE (Error Promedio):** {mae:.4f}
- **RMSE (Desviación):** {rmse:.4f}
- **Puntos de datos:** {data_points}
- **Calidad estimada:** {quality}

## Predicciones

| Fecha | Valor Predicho | Límite Inferior | Límite Superior |
|-------|----------------|-----------------|-----------------|
"""
        for pred in predictions:
            report_md += f"| {pred['date']} | {pred['predicted_value']:.4f} | {pred['lower_bound']:.4f} | {pred['upper_bound']:.4f} |\n"
        
        if alerts:
            report_md += "\n## Alertas\n\n"
            for alert in alerts:
                report_md += f"- **{alert['date']}** ({alert['severity']}): {alert['message']}\n"
                report_md += f"  - Recomendación: {alert['recommendation']}\n\n"
        
        st.download_button(
            label="📝 Descargar Reporte MD",
            data=report_md,
            file_name=f"reporte_prediccion_{metric}_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True,
            key="download_prediction_md"
        )
    
    st.success("✅ Predicción completada. Use los botones arriba para exportar los resultados.")
