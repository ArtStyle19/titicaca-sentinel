"""
Automated Report Generator Tab - Generate executive reports with insights
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import json
from frontend.components.ui import render_metric_card, render_alert, render_info_card
from frontend.utils.config import COLORS, DEFAULT_CLOUD_COVERAGE


def render_report_tab(api_client, latest_data):
    """Render Automated Report Generator tab"""
    
    st.markdown("### 📊 Generador de Reportes Automáticos")
    st.markdown("**Cree reportes ejecutivos con análisis de tendencias y recomendaciones para tomadores de decisión**")
    
    st.markdown("---")
    
    # Report configuration
    st.markdown("#### ⚙️ Configuración del Reporte")
    
    col1, col2 = st.columns(2)
    
    with col1:
        report_type = st.selectbox(
            "Tipo de Reporte:",
            ["Reporte Semanal", "Reporte Mensual", "Reporte Trimestral", "Análisis de Evento"],
            help="Seleccione el tipo de reporte a generar",
            key="report_type_selector"
        )
    
    with col2:
        include_sections = st.multiselect(
            "Secciones a Incluir:",
            ["Resumen Ejecutivo", "Índices Espectrales", "Análisis de Riesgo", "Tendencias Temporales", "Recomendaciones"],
            default=["Resumen Ejecutivo", "Índices Espectrales", "Recomendaciones"],
            help="Seleccione las secciones del reporte",
            key="report_sections"
        )
    
    # Generate report button
    if st.button("📄 Generar Reporte", use_container_width=True, type="primary", key="generate_report_btn"):
        st.session_state["report_generated"] = True
        st.session_state["report_timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not st.session_state.get("report_generated", False):
        render_info_card("""
        <strong>💡 Sobre esta herramienta:</strong><br><br>
        El Generador de Reportes Automáticos crea informes ejecutivos profesionales que incluyen:<br><br>
        • <strong>Resumen Ejecutivo</strong>: Hallazgos clave y estado general de calidad del agua<br>
        • <strong>Análisis de Índices</strong>: Valores actuales y comparación con umbrales críticos<br>
        • <strong>Evaluación de Riesgo</strong>: Identificación de zonas críticas y alertas<br>
        • <strong>Tendencias</strong>: Análisis temporal para detectar patrones<br>
        • <strong>Recomendaciones</strong>: Acciones sugeridas basadas en los datos<br><br>
        <strong>Ideal para:</strong> Presentaciones a autoridades, informes mensuales, evaluación de impacto ambiental
        """)
        return
    
    # REPORT GENERATION
    st.markdown("---")
    st.markdown(f"### 📑 Reporte Generado - {report_type}")
    st.caption(f"Generado el: {st.session_state.get('report_timestamp', 'N/A')}")
    
    # Get current data
    if not latest_data:
        st.error("No hay datos disponibles para generar el reporte")
        return
    
    stats = latest_data.get('statistics', {})
    date = latest_data.get('date', 'N/A')
    
    # SECTION 1: Executive Summary
    if "Resumen Ejecutivo" in include_sections:
        st.markdown("#### 📋 Resumen Ejecutivo")
        
        # Determine overall status
        ndci_mean = stats.get('ndci', {}).get('mean', 0)
        ndwi_mean = stats.get('ndwi', {}).get('mean', 0)
        turbidity_mean = stats.get('turbidity', {}).get('mean', 0)
        
        # Risk assessment
        high_risk_count = 0
        medium_risk_count = 0
        
        if ndci_mean > 0.2:
            high_risk_count += 1
        elif ndci_mean > 0:
            medium_risk_count += 1
        
        if turbidity_mean > 1.5:
            high_risk_count += 1
        elif turbidity_mean > 0.5:
            medium_risk_count += 1
        
        # Overall status
        if high_risk_count >= 2:
            status = "🔴 CRÍTICO"
            status_color = COLORS['danger']
            status_msg = "Se han detectado múltiples indicadores en niveles críticos que requieren atención inmediata."
        elif high_risk_count == 1 or medium_risk_count >= 2:
            status = "🟡 ATENCIÓN REQUERIDA"
            status_color = COLORS['warning']
            status_msg = "Algunos indicadores muestran niveles elevados que requieren monitoreo continuo."
        else:
            status = "🟢 NORMAL"
            status_color = COLORS['success']
            status_msg = "Los indicadores de calidad de agua se encuentran dentro de rangos aceptables."
        
        st.markdown(f"**Estado General:** {status}")
        st.markdown(f"**Período de Análisis:** {date}")
        st.markdown(f"**Evaluación:** {status_msg}")
        
        # Key findings
        st.markdown("**Hallazgos Clave:**")
        findings = []
        
        if ndci_mean > 0.2:
            findings.append(f"- ⚠️ **Alta concentración de clorofila** detectada (NDCI: {ndci_mean:.3f}). Posible florecimiento algal.")
        elif ndci_mean > 0:
            findings.append(f"- ℹ️ Concentración moderada de clorofila (NDCI: {ndci_mean:.3f})")
        else:
            findings.append(f"- ✅ Concentración baja de clorofila (NDCI: {ndci_mean:.3f})")
        
        if turbidity_mean > 1.5:
            findings.append(f"- ⚠️ **Alta turbidez** observada ({turbidity_mean:.3f}). Revisar fuentes de sedimentación.")
        elif turbidity_mean > 0.5:
            findings.append(f"- ℹ️ Turbidez moderada detectada ({turbidity_mean:.3f})")
        else:
            findings.append(f"- ✅ Turbidez baja ({turbidity_mean:.3f})")
        
        if ndwi_mean > 0.3:
            findings.append(f"- ✅ Cuerpo de agua claramente definido (NDWI: {ndwi_mean:.3f})")
        elif ndwi_mean > 0:
            findings.append(f"- ℹ️ Presencia de sedimentos suspendidos (NDWI: {ndwi_mean:.3f})")
        else:
            findings.append(f"- ⚠️ Posible presencia de vegetación o tierra (NDWI: {ndwi_mean:.3f})")
        
        for finding in findings:
            st.markdown(finding)
        
        st.markdown("---")
    
    # SECTION 2: Spectral Indices
    if "Índices Espectrales" in include_sections:
        st.markdown("#### 📊 Análisis de Índices Espectrales")
        
        # Metrics cards
        cols = st.columns(4)
        
        indices = [
            ("NDCI", "ndci", "mean", "Clorofila", [-0.5, 0, 0.2, 0.5]),
            ("NDWI", "ndwi", "mean", "Agua", [-0.2, 0, 0.3, 0.5]),
            ("Turbidez", "turbidity", "mean", "Sedimentos", [0, 0.5, 1.5, 3.0]),
            ("Chl-a", "chla_approx", "mean", "µg/L", [0, 10, 30, 50])
        ]
        
        for idx, (name, key, stat_type, subtitle, thresholds) in enumerate(indices):
            with cols[idx]:
                if key in stats and stat_type in stats[key]:
                    value = stats[key][stat_type]
                    
                    # Determine status based on thresholds
                    if value > thresholds[2]:
                        color = COLORS['danger']
                        icon = "🔴"
                    elif value > thresholds[1]:
                        color = COLORS['warning']
                        icon = "🟡"
                    else:
                        color = COLORS['success']
                        icon = "🟢"
                    
                    render_metric_card(
                        name,
                        f"{icon} {value:.3f}",
                        subtitle,
                        color
                    )
        
        # Detailed table
        st.markdown("**Estadísticas Detalladas:**")
        
        table_data = []
        for name, key, _, subtitle, _ in indices:
            if key in stats:
                row = {
                    "Índice": name,
                    "Media": f"{stats[key].get('mean', 0):.4f}",
                    "Desv. Estd.": f"{stats[key].get('std', 0):.4f}",
                    "Mínimo": f"{stats[key].get('min', 0):.4f}",
                    "Máximo": f"{stats[key].get('max', 0):.4f}",
                }
                table_data.append(row)
        
        if table_data:
            df = pd.DataFrame(table_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
    
    # SECTION 3: Risk Analysis
    if "Análisis de Riesgo" in include_sections:
        st.markdown("#### ⚠️ Análisis de Riesgo Ambiental")
        
        risk_zones = []
        
        # Determine risk zones based on criteria
        if ndci_mean > 0.2:
            risk_zones.append({
                "Zona": "Toda la región analizada",
                "Riesgo": "Alto - Eutrofización",
                "Indicador": "NDCI",
                "Valor": f"{ndci_mean:.3f}",
                "Acción": "Muestreo inmediato de clorofila"
            })
        
        if turbidity_mean > 1.5:
            risk_zones.append({
                "Zona": "Áreas con alta reflectancia",
                "Riesgo": "Alto - Sedimentación",
                "Indicador": "Turbidez",
                "Valor": f"{turbidity_mean:.3f}",
                "Acción": "Identificar fuentes de erosión"
            })
        
        if ndwi_mean < 0:
            risk_zones.append({
                "Zona": "Bordes del cuerpo de agua",
                "Riesgo": "Medio - Vegetación/Tierra",
                "Indicador": "NDWI",
                "Valor": f"{ndwi_mean:.3f}",
                "Acción": "Verificar niveles de agua"
            })
        
        if risk_zones:
            df_risks = pd.DataFrame(risk_zones)
            st.dataframe(df_risks, use_container_width=True, hide_index=True)
        else:
            st.success("✅ No se identificaron zonas de riesgo crítico en el período analizado.")
        
        st.markdown("---")
    
    # SECTION 4: Recommendations
    if "Recomendaciones" in include_sections:
        st.markdown("#### 💡 Recomendaciones")
        
        st.markdown("**Acciones Sugeridas:**")
        
        recommendations = []
        
        if ndci_mean > 0.2:
            recommendations.append({
                "Prioridad": "🔴 Alta",
                "Acción": "Muestreo de Clorofila In-Situ",
                "Justificación": f"NDCI elevado ({ndci_mean:.3f}) indica posible florecimiento algal",
                "Plazo": "Inmediato (1-3 días)"
            })
            recommendations.append({
                "Prioridad": "🟡 Media",
                "Acción": "Análisis de Nutrientes",
                "Justificación": "Determinar fuentes de eutrofización (N, P)",
                "Plazo": "Corto plazo (1-2 semanas)"
            })
        
        if turbidity_mean > 1.5:
            recommendations.append({
                "Prioridad": "🔴 Alta",
                "Acción": "Inspección de Fuentes de Erosión",
                "Justificación": f"Alta turbidez ({turbidity_mean:.3f}) requiere identificar origen",
                "Plazo": "Inmediato (1-3 días)"
            })
        
        recommendations.append({
            "Prioridad": "🟢 Rutina",
            "Acción": "Continuar Monitoreo Satelital",
            "Justificación": "Mantener vigilancia de tendencias a largo plazo",
            "Plazo": "Semanal"
        })
        
        recommendations.append({
            "Prioridad": "🟢 Rutina",
            "Acción": "Actualizar Base de Datos Histórica",
            "Justificación": "Registrar valores actuales para análisis de series temporales",
            "Plazo": "Mensual"
        })
        
        df_recommendations = pd.DataFrame(recommendations)
        st.dataframe(df_recommendations, use_container_width=True, hide_index=True)
        
        st.markdown("---")
    
    # EXPORT OPTIONS
    st.markdown("#### 💾 Opciones de Exportación")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # JSON export
        report_data = {
            "metadata": {
                "report_type": report_type,
                "generated_at": st.session_state.get('report_timestamp'),
                "period": date
            },
            "executive_summary": {
                "status": status,
                "message": status_msg,
                "high_risk_indicators": high_risk_count,
                "medium_risk_indicators": medium_risk_count
            },
            "indices": {
                "ndci": stats.get('ndci', {}),
                "ndwi": stats.get('ndwi', {}),
                "turbidity": stats.get('turbidity', {}),
                "chla_approx": stats.get('chla_approx', {})
            },
            "findings": findings,
            "risk_zones": risk_zones,
            "recommendations": recommendations
        }
        
        json_str = json.dumps(report_data, indent=2, ensure_ascii=False)
        st.download_button(
            label="📥 Descargar JSON",
            data=json_str,
            file_name=f"reporte_titicaca_{datetime.now().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True,
            key="download_json"
        )
    
    with col2:
        # CSV export (statistics)
        csv_data = []
        for key in ['ndci', 'ndwi', 'turbidity', 'chla_approx']:
            if key in stats:
                row = {"indice": key}
                row.update(stats[key])
                csv_data.append(row)
        
        if csv_data:
            df_csv = pd.DataFrame(csv_data)
            csv_str = df_csv.to_csv(index=False)
            st.download_button(
                label="📊 Descargar CSV",
                data=csv_str,
                file_name=f"estadisticas_titicaca_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                use_container_width=True,
                key="download_csv"
            )
    
    with col3:
        # Markdown export
        md_content = f"""# {report_type} - Lago Titicaca
        
**Generado:** {st.session_state.get('report_timestamp')}  
**Período:** {date}

## Resumen Ejecutivo

**Estado:** {status}  
**Evaluación:** {status_msg}

### Hallazgos Clave

"""
        for finding in findings:
            md_content += finding + "\n"
        
        md_content += "\n## Índices Espectrales\n\n"
        for name, key, _, _, _ in indices:
            if key in stats:
                md_content += f"- **{name}**: {stats[key].get('mean', 0):.4f}\n"
        
        md_content += "\n## Recomendaciones\n\n"
        for rec in recommendations:
            md_content += f"- **{rec['Prioridad']}** - {rec['Acción']}: {rec['Justificación']} (Plazo: {rec['Plazo']})\n"
        
        st.download_button(
            label="📝 Descargar Markdown",
            data=md_content,
            file_name=f"reporte_titicaca_{datetime.now().strftime('%Y%m%d')}.md",
            mime="text/markdown",
            use_container_width=True,
            key="download_md"
        )
    
    st.success("✅ Reporte generado exitosamente. Use los botones arriba para exportar en diferentes formatos.")
