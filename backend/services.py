"""
Service layer for GEE operations
"""
from typing import Dict, Tuple, Optional
import ee
from backend.models import TimeSeriesPoint


class GEEService:
    """Service for Google Earth Engine operations"""
    
    def __init__(self, processor):
        """Initialize with GEE processor instance"""
        self.processor = processor
    
    def get_latest_image_data(
        self, 
        months: Optional[int] = None, 
        cloud_coverage: int = 20, 
        days: Optional[int] = None
    ) -> Tuple:
        """Get latest processed image data
        
        Returns:
            Tuple of (composite, roi, date)
        """
        return self.processor.process_latest(
            months=months or 6,
            cloud_coverage=cloud_coverage,
            days=days
        )
    
    def get_statistics(self, composite, roi) -> Dict[str, float]:
        """Get statistics from composite image"""
        return self.processor.get_statistics(composite, roi)
    
    def generate_tile_urls(self, composite) -> Dict[str, str]:
        """Generate tile URLs for different indices
        
        Returns:
            Dictionary with tile URLs for NDWI, NDCI, and Turbidity
        """
        return {
            'ndwi': self.processor.get_tile_url(composite, {
                'bands': ['NDWI'],
                'min': -1,
                'max': 1,
                'palette': ['red', 'yellow', 'green', 'cyan', 'blue']
            }),
            'ndci': self.processor.get_tile_url(composite, {
                'bands': ['NDCI'],
                'min': -0.5,
                'max': 0.5,
                'palette': ['blue', 'cyan', 'yellow', 'orange', 'red']
            }),
            'turbidity': self.processor.get_tile_url(composite, {
                'bands': ['Turbidity'],
                'min': 0.5,
                'max': 2.0,
                'palette': ['blue', 'cyan', 'yellow', 'orange', 'brown']
            })
        }
    
    def get_risk_map_url(self, composite) -> str:
        """Generate risk map tile URL"""
        return self.processor.get_tile_url(composite, {
            'bands': ['Risk_Level'],
            'min': 1,
            'max': 3,
            'palette': ['green', 'yellow', 'red']
        })
    
    def calculate_risk_zones(self, composite, roi) -> Dict[str, int]:
        """Calculate risk zone statistics
        
        Returns:
            Dictionary with pixel counts for each risk level
        """
        try:
            risk_image = composite.select('Risk_Level')
            risk_stats_raw = risk_image.reduceRegion(
                reducer=ee.Reducer.frequencyHistogram(),
                geometry=roi,
                scale=100,
                maxPixels=1e9,
                bestEffort=True
            ).getInfo()
            
            risk_zones = risk_stats_raw.get('Risk_Level', {})
            return {str(k): int(v) for k, v in risk_zones.items()}
        except Exception as e:
            print(f"Warning: Could not calculate risk zones: {e}")
            return {'1': 0, '2': 0, '3': 0}
    
    def get_time_series_data(
        self, 
        lat: float, 
        lon: float, 
        months: int = 6, 
        cloud_coverage: int = 20
    ) -> Dict:
        """Get time series data for a specific location"""
        return self.processor.get_time_series(
            lat=lat,
            lon=lon,
            months=months,
            cloud_coverage=cloud_coverage
        )
    
    def parse_time_series(self, ts_data: Dict) -> list:
        """Parse time series features into TimeSeriesPoint objects"""
        data_points = []
        for feature in ts_data.get('features', []):
            props = feature.get('properties', {})
            data_points.append(TimeSeriesPoint(
                date=props.get('date', ''),
                ndwi=props.get('NDWI'),
                ndci=props.get('NDCI'),
                ci_green=props.get('CI_green'),
                turbidity=props.get('Turbidity'),
                chla_approx=props.get('Chla_approx')
            ))
        # Sort by date
        data_points.sort(key=lambda x: x.date)
        return data_points
    
    def get_roi_geojson(self) -> Dict:
        """Get Lake Titicaca ROI as GeoJSON"""
        roi = self.processor.get_lake_roi()
        geojson = roi.getInfo()
        area_km2 = roi.area(maxError=10).getInfo() / 1e6
        
        return {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {
                    "name": "Lago Titicaca",
                    "area_km2": area_km2
                },
                "geometry": geojson
            }]
        }
    
    def organize_statistics(self, stats: Dict, date: str) -> Dict:
        """Organize statistics into structured format
        
        Returns:
            Dictionary with means and percentiles organized by band
        """
        means = {k: v for k, v in stats.items() if '_mean' in k}
        
        percentiles = {}
        bands = ['NDWI', 'NDCI', 'CI_green', 'Turbidity', 'TSM', 'Chla_approx']
        
        for band in bands:
            percentiles[band] = {
                'p10': stats.get(f'{band}_p10', 0),
                'p50': stats.get(f'{band}_p50', 0),
                'p90': stats.get(f'{band}_p90', 0)
            }
        
        return {
            'date': date,
            'statistics': means,
            'percentiles': percentiles
        }
