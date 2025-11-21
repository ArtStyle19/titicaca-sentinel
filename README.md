# 🌊 Titicaca Sentinel

**Plataforma de Monitoreo de Calidad del Agua del Lago Titicaca**

Sistema completo de análisis ambiental usando Sentinel-2 y Google Earth Engine para detectar contaminación, niveles de clorofila, turbidez y clasificación de riesgo ambiental.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Arquitectura](#-arquitectura)
- [Requisitos](#-requisitos)
- [Instalación](#-instalación)
- [Configuración](#-configuración)
- [Uso](#-uso)
- [API Endpoints](#-api-endpoints)
- [Índices Calculados](#-índices-calculados)
- [Estructura del Proyecto](#-estructura-del-proyecto)

---

## 🎯 Características

- ✅ **Procesamiento automático** de imágenes Sentinel-2
- ✅ **Cálculo de índices** de calidad del agua (NDWI, NDCI, CI-green, Turbidez)
- ✅ **Clasificación de riesgo** ambiental (Bajo, Medio, Alto)
- ✅ **Dashboard interactivo** con Streamlit + Leaflet
- ✅ **API REST** con FastAPI
- ✅ **Series temporales** para análisis de tendencias
- ✅ **Exportación de datos** en GeoJSON y JSON
- ✅ **Visualización de mapas** con Google Earth Engine tiles
- ✅ **Estadísticas del lago** con percentiles y promedios
- ✅ **Detección de zonas críticas** automática

---

## 🏗️ Arquitectura

```
┌─────────────────┐
│  Google Earth   │
│    Engine API   │ ← Sentinel-2 SR Harmonized
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Backend API    │
│    (FastAPI)    │ ← Procesamiento de datos
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Frontend       │
│  (Streamlit)    │ ← Dashboard interactivo
└─────────────────┘
```

### Componentes:

1. **Google Earth Engine (GEE)**

   - Procesamiento de imágenes Sentinel-2
   - Cálculo de índices espectrales
   - Generación de tiles para mapas

2. **Backend (FastAPI)**

   - Endpoints REST API
   - Integración con GEE
   - Caché de datos
   - Generación de estadísticas

3. **Frontend (Streamlit)**
   - Dashboard interactivo
   - Mapas con Folium
   - Gráficas con Plotly
   - Interfaz de usuario

---

## 📦 Requisitos

### Software:

- Python 3.8+
- Cuenta de Google Earth Engine
- Google Cloud Project (configurado en GEE)

### Dependencias principales:

- `earthengine-api` - Google Earth Engine
- `fastapi` - Backend API
- `streamlit` - Dashboard
- `folium` - Mapas interactivos
- `plotly` - Visualizaciones

Ver `requirements.txt` para la lista completa.

---

## 🚀 Instalación

### 1. Clonar/Descargar el proyecto

```bash
cd titicaca-sentinel
```

### 2. Ejecutar script de instalación

```bash
chmod +x setup.sh
./setup.sh
```

El script:

- Crea un entorno virtual Python
- Instala todas las dependencias
- Muestra los siguientes pasos

### 3. Autenticar Google Earth Engine

```bash
source venv/bin/activate
earthengine authenticate
```

Sigue las instrucciones en el navegador para autenticar tu cuenta.

---

## ⚙️ Configuración

### 1. Crear archivo de configuración

```bash
cp .env.example .env
nano .env  # o usa tu editor favorito
```

### 2. Configurar variables de entorno

```bash
# Google Earth Engine Configuration
GOOGLE_CLOUD_PROJECT=tu-proyecto-gcp
EE_SERVICE_ACCOUNT_EMAIL=tu-email@tu-proyecto.iam.gserviceaccount.com
EE_PRIVATE_KEY_PATH=./config/gee-service-account-key.json

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=True

# Streamlit Configuration
STREAMLIT_PORT=8501

# Analysis parameters
CLOUD_COVERAGE_MAX=20
ANALYSIS_MONTHS=6
UPDATE_FREQUENCY_DAYS=7
```

**Nota:** Para uso local con autenticación personal, solo necesitas configurar `GOOGLE_CLOUD_PROJECT`.

### 3. (Opcional) Exportar ROI del lago

```bash
source venv/bin/activate
python gee/gee_processor.py
```

Esto generará `config/titicaca_roi.geojson` con la geometría exacta del lago.

---

## 🎮 Uso

### Opción 1: Iniciar ambos servicios

Terminal 1 - Backend:

```bash
chmod +x start_backend.sh
./start_backend.sh
```

Terminal 2 - Frontend:

```bash
chmod +x start_frontend.sh
./start_frontend.sh
```

### Opción 2: Manual

**Backend:**

```bash
source venv/bin/activate
cd backend
python main.py
```

**Frontend:**

```bash
source venv/bin/activate
cd frontend
streamlit run app.py
```

### Acceder a la aplicación

- **Dashboard**: http://localhost:8501
- **API Docs**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc

---

## 🔌 API Endpoints

### `GET /health`

Estado de salud del servicio

**Response:**

```json
{
  "status": "healthy",
  "timestamp": "2024-11-21T10:00:00",
  "gee_available": true
}
```

### `GET /latest`

Obtener la imagen más reciente procesada

**Parameters:**

- `months` (int): Meses retrospectivos (default: 6)
- `cloud_coverage` (int): Cobertura de nubes máxima % (default: 20)

**Response:**

```json
{
  "date": "2024-11-15",
  "tile_urls": {
    "ndwi": "https://earthengine.googleapis.com/...",
    "ndci": "https://earthengine.googleapis.com/...",
    "turbidity": "https://earthengine.googleapis.com/..."
  },
  "statistics": {
    "NDWI_mean": 0.5234,
    "NDCI_mean": 0.1456,
    ...
  }
}
```

### `GET /risk-map`

Obtener mapa de clasificación de riesgo

**Parameters:**

- `months` (int): Meses retrospectivos
- `cloud_coverage` (int): Cobertura de nubes máxima %

**Response:**

```json
{
  "date": "2024-11-15",
  "tile_url": "https://earthengine.googleapis.com/...",
  "risk_zones": {
    "1": 12500, // bajo
    "2": 8300, // medio
    "3": 3200 // alto
  }
}
```

### `GET /time-series`

Obtener serie temporal para un punto

**Parameters:**

- `lat` (float): Latitud
- `lon` (float): Longitud
- `months` (int): Meses retrospectivos
- `cloud_coverage` (int): Cobertura de nubes máxima %

**Response:**

```json
{
  "location": {"lat": -16.0, "lon": -69.0},
  "data": [
    {
      "date": "2024-06-01",
      "ndwi": 0.52,
      "ndci": 0.14,
      "turbidity": 1.2,
      "chla_approx": 25.3
    },
    ...
  ]
}
```

### `GET /stats`

Obtener estadísticas generales del lago

**Response:**

```json
{
  "date": "2024-11-15",
  "statistics": {
    "NDWI_mean": 0.5234,
    "NDCI_mean": 0.1456,
    ...
  },
  "percentiles": {
    "NDCI": {
      "p10": 0.05,
      "p50": 0.14,
      "p90": 0.28
    },
    ...
  }
}
```

### `GET /roi`

Obtener geometría del ROI del lago

**Response:**

```json
{
  "type": "FeatureCollection",
  "features": [{
    "type": "Feature",
    "properties": {
      "name": "Lago Titicaca",
      "area_km2": 8372.5
    },
    "geometry": {...}
  }]
}
```

---

## 📊 Índices Calculados

### NDWI - Normalized Difference Water Index

**Fórmula:** `(NIR - Green) / (NIR + Green)`

Detecta cuerpos de agua y humedad. Valores altos indican presencia de agua.

### NDCI - Normalized Difference Chlorophyll Index

**Fórmula:** `(Red Edge - Red) / (Red Edge + Red)`

Estima concentración de clorofila. Correlacionado con floración de algas.

### CI-green - Chlorophyll Index Green

**Fórmula:** `(NIR / Green) - 1`

Índice complementario para detección de clorofila.

### Turbidez

**Fórmula:** `Red / Green`

Aproximación de turbidez basada en ratio de bandas visibles.

### TSM - Total Suspended Matter

**Fórmula:** `NIR / Red`

Estimación de materia suspendida total.

### Clorofila-a (aproximada)

**Fórmula:** `NDCI * 50 + 30` (μg/L)

Conversión empírica de NDCI a concentración de clorofila.

---

## 🎨 Clasificación de Riesgo

El sistema clasifica zonas en tres niveles:

| Nivel     | Criterio | Color       | Descripción              |
| --------- | -------- | ----------- | ------------------------ |
| **Bajo**  | < P70    | 🟢 Verde    | Condiciones normales     |
| **Medio** | P70-P90  | 🟡 Amarillo | Atención requerida       |
| **Alto**  | > P90    | 🔴 Rojo     | Riesgo ambiental crítico |

**P70** = Percentil 70
**P90** = Percentil 90

Los umbrales son **relativos** al estado actual del lago, calculados dinámicamente.

---

## 📁 Estructura del Proyecto

```
titicaca-sentinel/
│
├── backend/                    # Backend FastAPI
│   └── main.py                # App principal y endpoints
│
├── frontend/                   # Frontend Streamlit
│   └── app.py                 # Dashboard interactivo
│
├── gee/                        # Google Earth Engine scripts
│   ├── 01_extract_roi.js      # Extracción de ROI (JavaScript)
│   ├── 02_process_sentinel2.js # Procesamiento S2 (JavaScript)
│   └── gee_processor.py       # Procesador Python GEE
│
├── notebooks/                  # Jupyter notebooks (futuro ML)
│
├── data/                       # Datos exportados
│   └── exports/               # Estadísticas y GeoTIFFs
│
├── config/                     # Configuración
│   └── titicaca_roi.geojson   # Geometría del lago
│
├── requirements.txt            # Dependencias Python
├── .env.example               # Plantilla de configuración
├── .gitignore                 # Git ignore
├── setup.sh                   # Script de instalación
├── start_backend.sh           # Iniciar backend
├── start_frontend.sh          # Iniciar frontend
└── README.md                  # Esta documentación
```

---

## 🧪 Testing

### Probar el backend manualmente:

```bash
# Health check
curl http://localhost:8000/health

# Obtener última imagen
curl "http://localhost:8000/latest?months=6&cloud_coverage=20"

# Obtener mapa de riesgo
curl "http://localhost:8000/risk-map?months=6"

# Serie temporal
curl "http://localhost:8000/time-series?lat=-16.0&lon=-69.0&months=3"
```

### Probar con navegador:

Visita http://localhost:8000/docs para la interfaz Swagger interactiva.

---

## 🔧 Troubleshooting

### Error: "Earth Engine not initialized"

**Solución:**

```bash
earthengine authenticate
```

### Error: "GEE processor not available"

**Solución:**

1. Verifica que `earthengine-api` esté instalado
2. Configura `GOOGLE_CLOUD_PROJECT` en `.env`
3. Reinicia el backend

### Error: "No images found"

**Solución:**

- Aumenta el rango de meses (`months=12`)
- Aumenta la cobertura de nubes permitida (`cloud_coverage=30`)
- Verifica las fechas en Google Earth Engine Code Editor

### Error: "Connection refused" en frontend

**Solución:**

- Asegúrate de que el backend esté corriendo en `http://localhost:8000`
- Verifica que `API_BASE_URL` en `frontend/app.py` sea correcto

---

## 🚧 Futuras Mejoras

- [ ] Modelo baseline Random Forest para clasificación
- [ ] Detección de cambios temporales automática
- [ ] Alertas por email cuando se detecte riesgo alto
- [ ] Exportación de reportes PDF
- [ ] Comparación entre fechas
- [ ] Integración con datos in-situ
- [ ] API de predicción a futuro
- [ ] Análisis de tendencias históricas
- [ ] Dashboard móvil

---

## 📄 Licencia

Este proyecto es un prototipo para hackathons y proyectos educativos.

---

## 👥 Contribuciones

Desarrollado como prototipo funcional para monitoreo ambiental del Lago Titicaca.

---

## 📞 Contacto

Para preguntas o sugerencias sobre el proyecto.

---

## 🙏 Agradecimientos

- **ESA Copernicus** - Por las imágenes Sentinel-2
- **Google Earth Engine** - Por la plataforma de procesamiento
- **JRC Global Surface Water** - Por los datos de cuerpos de agua

---

**¡Protejamos el Lago Titicaca! 🌊🌍**
