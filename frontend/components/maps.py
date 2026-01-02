"""
Map components for Titicaca Sentinel
"""
import folium
import folium.plugins
from frontend.utils.config import MAP_CENTER, MAP_DEFAULT_ZOOM, COLORS


def create_map(center=MAP_CENTER, zoom=MAP_DEFAULT_ZOOM):
    """Create base Folium map with professional styling"""
    m = folium.Map(
        location=center,
        zoom_start=zoom,
        tiles='OpenStreetMap',
        attr='OpenStreetMap',
        prefer_canvas=True,
        control_scale=True
    )

    # Add helpful plugins for a more professional map
    folium.plugins.Fullscreen(
        position='topright',
        title='Pantalla completa',
        title_cancel='Salir de pantalla completa'
    ).add_to(m)
    
    folium.plugins.MeasureControl(
        position='topleft',
        primary_length_unit='meters',
        primary_area_unit='sqmeters',
        secondary_length_unit='kilometers',
        secondary_area_unit='hectares'
    ).add_to(m)

    # Mouse position (lat/lon) for easier inspection
    folium.plugins.MousePosition(
        position='bottomleft',
        separator=' | ',
        prefix='Coordenadas:',
        lat_formatter="function(num) {return L.Util.formatNum(num, 5) + ' °N';}",
        lng_formatter="function(num) {return L.Util.formatNum(num, 5) + ' °E';}"
    ).add_to(m)

    return m


def create_legend_html(layer_type):
    """Create custom legend HTML"""
    legends = {
        "Mapa de Riesgo": {
            "title": "Nivel de Riesgo Ambiental",
            "items": [
                (COLORS['risk_low'], "Condiciones Normales", "Indicadores bajo percentil 70"),
                (COLORS['risk_medium'], "Atención Requerida", "Indicadores entre percentil 70-90"),
                (COLORS['risk_high'], "Zona Crítica", "Indicadores sobre percentil 90"),
            ]
        },
        "NDCI (Clorofila)": {
            "title": "Índice de Clorofila Normalizado",
            "items": [
                ("#3498DB", "Baja Concentración", "NDCI < -0.2 | Aguas oligotróficas"),
                ("#2ECC71", "Concentración Moderada", "-0.2 ≤ NDCI ≤ 0.2 | Aguas mesotróficas"),
                ("#E74C3C", "Alta Concentración", "NDCI > 0.2 | Posible eutrofización"),
            ]
        },
        "NDWI (Agua)": {
            "title": "Índice Normalizado de Agua",
            "items": [
                ("#E74C3C", "Tierra/Vegetación", "NDWI < 0 | Áreas terrestres"),
                ("#F39C12", "Agua Turbia", "0 ≤ NDWI ≤ 0.3 | Sedimentos suspendidos"),
                ("#3498DB", "Agua Clara", "NDWI > 0.3 | Cuerpo de agua definido"),
            ]
        },
        "Turbidez": {
            "title": "Nivel de Turbidez Relativa",
            "items": [
                ("#3498DB", "Baja Turbidez", "Ratio < 0.5 | Buena claridad"),
                ("#F39C12", "Turbidez Moderada", "0.5 ≤ Ratio ≤ 1.5 | Sedimentos moderados"),
                ("#8B4513", "Alta Turbidez", "Ratio > 1.5 | Alta carga de sedimentos"),
            ]
        }
    }
    
    legend = legends.get(layer_type, legends["Mapa de Riesgo"])
    
    html = f"""
    <div class="legend-container">
        <div class="legend-title">{legend['title']}</div>
    """
    
    for color, label, description in legend['items']:
        html += f"""
        <div class="legend-item">
            <div class="legend-color" style="background-color: {color};"></div>
            <div>
                <strong class="legend-label">{label}</strong>
                <div style="font-size: 0.75rem; color: #7f8c8d;">{description}</div>
            </div>
        </div>
        """
    
    html += "</div>"
    return html


def add_tile_overlay(m: folium.Map, tile_url: str, name: str = 'Overlay', opacity: float = 0.8):
    """Add a tile overlay (mapid/tile url) to the map with a default opacity and layer name.

    This helper ensures overlays are added to the LayerControl and can be toggled.
    """
    try:
        folium.raster_layers.TileLayer(
            tiles=tile_url,
            attr=name,
            name=name,
            overlay=True,
            control=True,
            opacity=opacity
        ).add_to(m)
    except Exception as e:
        print(f"Warning: could not add tile overlay {name}: {e}")
