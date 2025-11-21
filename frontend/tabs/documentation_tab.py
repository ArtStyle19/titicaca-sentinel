"""
Documentation Tab
"""
import streamlit as st
from frontend.components.ui import render_info_card
from frontend.utils.config import COLORS, LAKE_INFO, SYSTEM_INFO


def render_documentation_tab(api_client, latest_data):
    """Render Documentation tab"""
    
    st.markdown("### 📚 Documentación del Sistema")
    st.markdown("**Información técnica y guía de uso de Titicaca Sentinel**")
    
    # Quick Info Cards
    cols = st.columns(3)
    
    with cols[0]:
        render_info_card(f"""
        <strong>📡 Fuente de Datos:</strong><br>
        Sentinel-2 MSI<br>
        Nivel: L2A<br>
        Resolución: 10-20m
        """)
    
    with cols[1]:
        render_info_card(f"""
        <strong>🌍 Área de Estudio:</strong><br>
        Lago Titicaca<br>
        Bolivia-Perú<br>
        8,562 km²
        """)
    
    with cols[2]:
        render_info_card(f"""
        <strong>🔄 Actualización:</strong><br>
        Cada 5 días<br>
        (Sentinel-2 A+B)<br>
        Nubosidad < 20%
        """)
    
    st.markdown("---")
    
    # Tabs for different documentation sections
    tabs = st.tabs([
        "🚀 Inicio Rápido",
        "📊 Índices Espectrales",
        "🎯 Metodología",
        "⚙️ Configuración",
        "❓ FAQ"
    ])
    
    with tabs[0]:
        st.markdown("## 🚀 Guía de Inicio Rápido")
        
        st.markdown("""
        ### Bienvenido a Titicaca Sentinel
        
        Este sistema proporciona monitoreo continuo de la calidad del agua del Lago Titicaca utilizando 
        imágenes satelitales Sentinel-2 procesadas con Google Earth Engine.
        
        #### Cómo usar el sistema:
        
        **1. Evaluación de Riesgo** (Pestaña 1)
        - Visualice el mapa de riesgo ambiental integrado
        - Identifique zonas críticas que requieren atención
        - Revise las estadísticas de distribución de riesgo
        
        **2. Calidad del Agua** (Pestaña 2)
        - Seleccione un índice espectral específico (NDCI, NDWI, Turbidez)
        - Analice los mapas de cada indicador
        - Interprete los valores según las escalas proporcionadas
        
        **3. Análisis Temporal** (Pestaña 3)
        - Seleccione un rango de fechas
        - Elija una ubicación específica en el lago
        - Observe la evolución de los indicadores en el tiempo
        - Descargue los datos en formato CSV
        
        **4. Estadísticas** (Pestaña 4)
        - Revise estadísticas descriptivas detalladas
        - Compare distribuciones de diferentes índices
        - Exporte datos estadísticos en CSV o JSON
        
        **5. Documentación** (Esta pestaña)
        - Consulte información técnica
        - Entienda la metodología aplicada
        - Resuelva dudas frecuentes
        """)
        
        st.info("💡 **Tip:** Use la barra lateral para ver información de la última imagen procesada y el estado del sistema.")
    
    with tabs[1]:
        st.markdown("## 📊 Índices Espectrales")
        
        st.markdown("### NDCI - Normalized Difference Chlorophyll Index")
        st.markdown("""
        **Propósito:** Estimación de concentración de clorofila-a en el agua.
        
        **Fórmula:** `NDCI = (RE - Red) / (RE + Red)`
        - **RE:** Red Edge (banda 5, ~705 nm)
        - **Red:** Rojo (banda 4, ~665 nm)
        
        **Rango de valores:** -1 a 1
        
        **Interpretación:**
        - **< -0.2:** Baja concentración de clorofila (oligotrófico)
        - **-0.2 a 0.2:** Concentración moderada (mesotrófico)
        - **> 0.2:** Alta concentración, posible eutrofización
        
        **Aplicaciones:**
        - Detección de floraciones algales
        - Monitoreo de eutrofización
        - Evaluación de productividad primaria
        
        **Limitaciones:**
        - Sensible a la turbidez del agua
        - Requiere corrección atmosférica precisa
        - Puede saturarse en concentraciones muy altas
        """)
        
        st.markdown("---")
        
        st.markdown("### NDWI - Normalized Difference Water Index")
        st.markdown("""
        **Propósito:** Delineación de cuerpos de agua y evaluación de claridad.
        
        **Fórmula:** `NDWI = (Green - NIR) / (Green + NIR)`
        - **Green:** Verde (banda 3, ~560 nm)
        - **NIR:** Infrarrojo cercano (banda 8, ~842 nm)
        
        **Rango de valores:** -1 a 1
        
        **Interpretación:**
        - **< 0:** Tierra, vegetación o ausencia de agua
        - **0 a 0.3:** Agua turbia o con sedimentos suspendidos
        - **> 0.3:** Agua clara, cuerpo de agua bien definido
        
        **Aplicaciones:**
        - Mapeo de extensión de agua
        - Detección de cambios en el nivel del lago
        - Identificación de agua turbia vs clara
        
        **Limitaciones:**
        - Puede confundirse con sombras en terreno montañoso
        - Sensible a la reflectancia de la superficie
        """)
        
        st.markdown("---")
        
        st.markdown("### Turbidity - Índice de Turbidez (Red/Green Ratio)")
        st.markdown("""
        **Propósito:** Estimación de la carga de sedimentos suspendidos.
        
        **Fórmula:** `Turbidity = Red / Green`
        - **Red:** Rojo (banda 4, ~665 nm)
        - **Green:** Verde (banda 3, ~560 nm)
        
        **Rango de valores:** 0 a >2
        
        **Interpretación:**
        - **< 0.5:** Baja turbidez, buena claridad del agua
        - **0.5 a 1.5:** Turbidez moderada, sedimentos en suspensión
        - **> 1.5:** Alta turbidez, alta carga de sedimentos
        
        **Aplicaciones:**
        - Detección de erosión y escorrentía
        - Monitoreo de calidad de agua post-tormentas
        - Identificación de zonas de deposición
        
        **Limitaciones:**
        - No mide turbidez absoluta (en NTU)
        - Valores relativos, no calibrados in-situ
        - Afectado por reflectancia del fondo en aguas someras
        """)
    
    with tabs[2]:
        st.markdown("## 🎯 Metodología")
        
        st.markdown("### Procesamiento de Imágenes")
        st.markdown("""
        #### 1. Adquisición de Datos
        - **Plataforma:** Sentinel-2 A y B
        - **Producto:** Level-2A (corrección atmosférica aplicada)
        - **Frecuencia:** Cada 5 días (con ambos satélites)
        - **Resolución espacial:** 10m (B2, B3, B4, B8), 20m (B5)
        
        #### 2. Pre-procesamiento
        - Filtrado por cobertura de nubes (< 20%)
        - Enmascaramiento de nubes y sombras usando SCL (Scene Classification Layer)
        - Selección de imagen más reciente sin nubes
        
        #### 3. Cálculo de Índices
        - NDCI: `(B5 - B4) / (B5 + B4)`
        - NDWI: `(B3 - B8) / (B3 + B8)`
        - Turbidity: `B4 / B3`
        
        #### 4. Generación del Mapa de Riesgo
        - Cálculo de percentiles (P70, P90) para cada índice
        - Clasificación de riesgo:
          - **Bajo:** Todos los índices bajo P70
          - **Medio:** Al menos un índice entre P70-P90
          - **Alto:** Al menos un índice sobre P90
        
        #### 5. Análisis Estadístico
        - Cálculo de estadísticas descriptivas (media, mediana, desviación estándar)
        - Distribución percentil (P10, P25, P50, P75, P90, P95)
        - Conteo de pixels por categoría de riesgo
        """)
        
        st.markdown("### Validación y Limitaciones")
        st.markdown("""
        **Ventajas:**
        - Cobertura completa del lago cada 5 días
        - Datos gratuitos y de acceso abierto
        - Procesamiento escalable en la nube (GEE)
        - Resolución espacial adecuada (10-20m)
        
        **Limitaciones:**
        - Dependencia de condiciones atmosféricas (nubes)
        - Estimaciones indirectas (no mediciones in-situ)
        - Requiere calibración con muestreos de campo
        - Afectado por reflectancia del fondo en aguas someras (<1m)
        
        **Recomendaciones:**
        - Complementar con muestreos in-situ periódicos
        - Validar umbrales de riesgo con datos históricos
        - Considerar estacionalidad y condiciones climáticas
        - Usar como herramienta de screening, no diagnóstico absoluto
        """)
    
    with tabs[3]:
        st.markdown("## ⚙️ Configuración del Sistema")
        
        st.markdown("### Información Técnica")
        
        col1, col2 = st.columns(2)
        
        with col1:
            render_info_card(f"""
            <strong>Backend:</strong><br>
            Framework: FastAPI<br>
            Python: {SYSTEM_INFO.get('python_version', '3.11+')}<br>
            GEE API: earthengine-api<br>
            Procesamiento: Google Earth Engine
            """)
        
        with col2:
            render_info_card(f"""
            <strong>Frontend:</strong><br>
            Framework: Streamlit<br>
            Mapas: Folium + Leaflet.js<br>
            Charts: Plotly.js<br>
            Estilo: Custom CSS
            """)
        
        st.markdown("### Parámetros del Sistema")
        
        st.markdown(f"""
        **Área de Estudio:**
        - Centro: ({LAKE_INFO['center']['lat']}, {LAKE_INFO['center']['lng']})
        - Límites:
          - Norte: {LAKE_INFO['bounds']['north']}
          - Sur: {LAKE_INFO['bounds']['south']}
          - Este: {LAKE_INFO['bounds']['east']}
          - Oeste: {LAKE_INFO['bounds']['west']}
        
        **Procesamiento:**
        - Máx. cobertura de nubes: 20%
        - Escala de análisis: 30m
        - Máx. días para búsqueda: 30
        - Buffer de ROI: 1000m
        
        **Umbrales de Riesgo:**
        - Bajo riesgo: Todos los índices < P70
        - Riesgo medio: Algún índice entre P70-P90
        - Riesgo alto: Algún índice > P90
        """)
    
    with tabs[4]:
        st.markdown("## ❓ Preguntas Frecuentes")
        
        with st.expander("¿Con qué frecuencia se actualizan los datos?"):
            st.markdown("""
            El sistema procesa automáticamente las imágenes más recientes de Sentinel-2. 
            Con ambos satélites (Sentinel-2A y 2B), la frecuencia de revisita es de aproximadamente 5 días.
            Sin embargo, la disponibilidad de imágenes sin nubes puede variar según la temporada.
            """)
        
        with st.expander("¿Qué significa 'percentil 90' (P90)?"):
            st.markdown("""
            El percentil 90 (P90) indica que el 90% de los valores observados están por debajo de este umbral.
            Es útil para identificar valores atípicamente altos que podrían indicar condiciones problemáticas.
            Por ejemplo, un NDCI en P90 sugiere alta concentración de clorofila en esa área.
            """)
        
        with st.expander("¿Los valores de turbidez son absolutos?"):
            st.markdown("""
            No, el índice de turbidez (Red/Green ratio) proporciona valores relativos, no mediciones absolutas en NTU.
            Para obtener valores calibrados de turbidez, se requeriría calibración con muestreos in-situ.
            Sin embargo, es útil para comparaciones espaciales y temporales relativas.
            """)
        
        with st.expander("¿Por qué hay áreas sin datos en los mapas?"):
            st.markdown("""
            Las áreas sin datos generalmente corresponden a:
            - Nubes o sombras de nubes
            - Áreas terrestres fuera del lago
            - Pixels enmascarados por el procesamiento de calidad
            
            El sistema utiliza el Scene Classification Layer (SCL) de Sentinel-2 L2A para filtrar pixels de baja calidad.
            """)
        
        with st.expander("¿Puedo descargar los datos?"):
            st.markdown("""
            Sí, el sistema permite descargar:
            - Series temporales en formato CSV (Pestaña Análisis Temporal)
            - Estadísticas en formato CSV y JSON (Pestaña Estadísticas)
            
            Para obtener los datos raster completos, puede contactar al administrador del sistema.
            """)
        
        with st.expander("¿Cómo interpreto el mapa de riesgo?"):
            st.markdown("""
            El mapa de riesgo integra los tres índices (NDCI, NDWI, Turbidez) en una clasificación única:
            
            - **Verde (Bajo):** Todos los indicadores están dentro de rangos normales (< P70)
            - **Amarillo (Medio):** Al menos un indicador está elevado (P70-P90)
            - **Rojo (Alto):** Al menos un indicador está en el percentil más alto (> P90)
            
            Esto ayuda a priorizar áreas que requieren investigación adicional.
            """)
        
        st.markdown("---")
        st.markdown("### 📧 Contacto y Soporte")
        render_info_card("""
        Para preguntas técnicas, reportar problemas o solicitar funcionalidades adicionales, 
        contacte al equipo de desarrollo del proyecto Titicaca Sentinel.
        """)
