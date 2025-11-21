"""
TITICACA SENTINEL - Google Earth Engine Python API
Process Sentinel-2 data and export results
"""

import ee
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import time

class TiticacaProcessor:
    """Process Sentinel-2 data for Lake Titicaca water quality analysis"""
    
    def __init__(self, project_id=None, service_account=None, key_file=None):
        """Initialize Google Earth Engine"""
        try:
            if service_account and key_file:
                # Use service account authentication
                credentials = ee.ServiceAccountCredentials(service_account, key_file)
                ee.Initialize(credentials, project=project_id)
                print("✓ Earth Engine initialized with Service Account")
            elif project_id:
                # Use default authentication
                ee.Initialize(project=project_id)
                print("✓ Earth Engine initialized with default credentials")
            else:
                ee.Initialize()
                print("✓ Earth Engine initialized")
        except Exception as e:
            print(f"Error initializing Earth Engine: {e}")
            print("Run: earthengine authenticate")
            raise
    
    def get_lake_roi(self):
        """Extract Lake Titicaca ROI using JRC Global Surface Water"""
        bbox = ee.Geometry.Rectangle([-70.3, -17.3, -68.4, -15.4])
        
        # Load JRC Global Surface Water
        gsw = ee.Image("JRC/GSW1_4/GlobalSurfaceWater")
        occurrence = gsw.select("occurrence")
        
        # Water mask (permanent water > 50%)
        water_mask = occurrence.gt(50).selfMask()
        
        # Convert to vectors
        vectors = water_mask.reduceToVectors(
            geometry=bbox,
            scale=30,
            geometryType="polygon",
            maxPixels=1e13
        )
        
        # Add area and select largest polygon
        def add_area(feature):
            area = feature.geometry().area(maxError=10)
            return feature.set("area", area)
        
        vectors_with_area = vectors.map(add_area)
        lake = vectors_with_area.sort("area", False).first()
        roi = lake.geometry()
        
        print(f"✓ ROI extracted - Area: {roi.area(maxError=10).getInfo() / 1e6:.2f} km²")
        return roi
    
    def mask_s2_clouds(self, image):
        """Mask clouds in Sentinel-2 image"""
        qa = image.select('QA60')
        cloud_bit_mask = 1 << 10
        cirrus_bit_mask = 1 << 11
        
        mask = (qa.bitwiseAnd(cloud_bit_mask).eq(0)
                .And(qa.bitwiseAnd(cirrus_bit_mask).eq(0)))
        
        return (image.updateMask(mask)
                .divide(10000)
                .copyProperties(image, ['system:time_start']))
    
    def calculate_indices(self, image):
        """Calculate water quality indices"""
        green = image.select('B3')
        red = image.select('B4')
        red_edge1 = image.select('B5')
        nir = image.select('B8')
        
        # NDWI - Normalized Difference Water Index
        ndwi = nir.subtract(green).divide(nir.add(green)).rename('NDWI')
        
        # NDCI - Normalized Difference Chlorophyll Index
        ndci = red_edge1.subtract(red).divide(red_edge1.add(red)).rename('NDCI')
        
        # CI-green - Chlorophyll Index Green
        ci_green = nir.divide(green).subtract(1).rename('CI_green')
        
        # Turbidity approximation
        turbidity = red.divide(green).rename('Turbidity')
        
        # TSM approximation
        tsm = nir.divide(red).rename('TSM')
        
        # Chlorophyll-a approximation
        chla = ndci.multiply(50).add(30).clamp(0, 150).rename('Chla_approx')
        
        return image.addBands([ndwi, ndci, ci_green, turbidity, tsm, chla])
    
    def classify_risk(self, image, roi):
        """Classify environmental risk levels"""
        print("  Calculating risk thresholds...")
        ndci = image.select('NDCI')
        turbidity = image.select('Turbidity')
        
        # Calculate percentiles with larger scale for speed
        ndci_stats = ndci.reduceRegion(
            reducer=ee.Reducer.percentile([70, 90]),
            geometry=roi,
            scale=100,  # Increased from 30 for faster processing
            maxPixels=1e9,
            bestEffort=True
        )
        
        turb_stats = turbidity.reduceRegion(
            reducer=ee.Reducer.percentile([70, 90]),
            geometry=roi,
            scale=100,
            maxPixels=1e9,
            bestEffort=True
        )
        
        ndci_p70 = ee.Number(ndci_stats.get('NDCI_p70'))
        ndci_p90 = ee.Number(ndci_stats.get('NDCI_p90'))
        turb_p70 = ee.Number(turb_stats.get('Turbidity_p70'))
        turb_p90 = ee.Number(turb_stats.get('Turbidity_p90'))
        
        print(f"  NDCI thresholds: P70={ndci_p70.getInfo():.4f}, P90={ndci_p90.getInfo():.4f}")
        print(f"  Turbidity thresholds: P70={turb_p70.getInfo():.4f}, P90={turb_p90.getInfo():.4f}")
        
        # Risk classification
        high_risk = ndci.gt(ndci_p90).Or(turbidity.gt(turb_p90))
        medium_risk = (ndci.gt(ndci_p70).Or(turbidity.gt(turb_p70))
                      .And(high_risk.Not()))
        low_risk = high_risk.Not().And(medium_risk.Not())
        
        risk_map = (low_risk.multiply(1)
                   .add(medium_risk.multiply(2))
                   .add(high_risk.multiply(3))
                   .rename('Risk_Level'))
        
        return image.addBands(risk_map)
    
    def process_latest(self, months=6, cloud_coverage=20, days=None):
        """Process latest available Sentinel-2 data
        
        Args:
            months: Number of months to look back (default: 6)
            cloud_coverage: Maximum cloud coverage percentage (default: 20)
            days: Number of days to look back (overrides months if specified)
        """
        if days:
            period_days = days
            print(f"Processing latest Sentinel-2 data (last {days} days)...")
        else:
            period_days = months * 30
            print(f"Processing latest Sentinel-2 data (last {months} months)...")
            
        end_date = datetime.now()
        start_date = end_date - timedelta(days=period_days)
        
        print("  Step 1/5: Extracting lake ROI...")
        roi = self.get_lake_roi()
        
        # Load Sentinel-2 data
        print("  Step 2/5: Loading Sentinel-2 images...")
        s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
              .filterBounds(roi)
              .filterDate(start_date.strftime('%Y-%m-%d'), 
                         end_date.strftime('%Y-%m-%d'))
              .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_coverage)))
        
        count = s2.size().getInfo()
        print(f"  ✓ Found {count} Sentinel-2 images")
        
        if count == 0:
            raise ValueError(f"No images found for the specified period. Try increasing cloud_coverage or time period.")
        
        # Process collection
        print("  Step 3/5: Applying cloud mask and calculating indices...")
        s2_processed = s2.map(self.mask_s2_clouds).map(self.calculate_indices)
        
        # Get latest image
        latest = s2_processed.sort('system:time_start', False).first()
        latest_date = ee.Date(latest.get('system:time_start')).format('YYYY-MM-dd').getInfo()
        
        # Create composite
        print("  Step 4/5: Creating median composite...")
        composite = s2_processed.median().clip(roi)
        
        print("  Step 5/5: Classifying risk levels...")
        composite_with_risk = self.classify_risk(composite, roi)
        
        print(f"✓ Processing complete! Latest image: {latest_date}")
        
        return composite_with_risk, roi, latest_date
    
    def get_statistics(self, image, roi):
        """Calculate lake statistics"""
        bands = ['NDWI', 'NDCI', 'CI_green', 'Turbidity', 'TSM', 'Chla_approx']
        
        stats = image.select(bands).reduceRegion(
            reducer=ee.Reducer.mean().combine(
                reducer2=ee.Reducer.stdDev(),
                sharedInputs=True
            ).combine(
                reducer2=ee.Reducer.percentile([10, 50, 90]),
                sharedInputs=True
            ),
            geometry=roi,
            scale=100,
            maxPixels=1e9
        )
        
        return stats.getInfo()
    
    def get_time_series(self, lat, lon, months=6, cloud_coverage=20):
        """Get time series data for a specific point"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=months * 30)
        
        point = ee.Geometry.Point([lon, lat])
        
        s2 = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
              .filterBounds(point)
              .filterDate(start_date.strftime('%Y-%m-%d'), 
                         end_date.strftime('%Y-%m-%d'))
              .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', cloud_coverage)))
        
        s2_processed = s2.map(self.mask_s2_clouds).map(self.calculate_indices)
        
        def extract_values(image):
            date = ee.Date(image.get('system:time_start')).format('YYYY-MM-dd')
            values = image.select(['NDWI', 'NDCI', 'CI_green', 'Turbidity', 
                                  'TSM', 'Chla_approx']).reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=point,
                scale=30
            )
            return ee.Feature(None, values.set('date', date))
        
        time_series = s2_processed.map(extract_values)
        
        return time_series.getInfo()
    
    def get_tile_url(self, image, vis_params):
        """Get tile URL for web visualization"""
        return image.getMapId(vis_params)['tile_fetcher'].url_format
    
    def export_geojson_roi(self, output_path='./config/titicaca_roi.geojson'):
        """Export ROI as GeoJSON"""
        roi = self.get_lake_roi()
        geojson = roi.getInfo()
        
        # Create proper GeoJSON structure
        feature_collection = {
            "type": "FeatureCollection",
            "features": [{
                "type": "Feature",
                "properties": {
                    "name": "Lago Titicaca",
                    "source": "JRC Global Surface Water"
                },
                "geometry": geojson
            }]
        }
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(feature_collection, f, indent=2)
        
        print(f"✓ ROI exported to {output_path}")


if __name__ == "__main__":
    # Example usage
    print("=== Titicaca Sentinel - GEE Processor ===\n")
    
    # Initialize (replace with your project ID)
    processor = TiticacaProcessor(project_id='your-gcp-project-id')
    
    # Export ROI
    processor.export_geojson_roi()
    
    # Process latest data
    composite, roi, date = processor.process_latest(months=6, cloud_coverage=20)
    
    # Get statistics
    stats = processor.get_statistics(composite, roi)
    print(f"\n✓ Lake Statistics for {date}:")
    for key, value in stats.items():
        if isinstance(value, (int, float)):
            print(f"  {key}: {value:.4f}")
    
    # Save statistics
    output_dir = Path('./data/exports')
    output_dir.mkdir(parents=True, exist_ok=True)
    
    stats_file = output_dir / f'stats_{date}.json'
    with open(stats_file, 'w') as f:
        json.dump({
            'date': date,
            'statistics': stats
        }, f, indent=2)
    
    print(f"\n✓ Statistics saved to {stats_file}")
    
    # Get tile URLs for visualization
    print("\n✓ Generating tile URLs for web visualization...")
    
    ndci_vis = {
        'bands': ['NDCI'],
        'min': -0.5,
        'max': 0.5,
        'palette': ['blue', 'cyan', 'yellow', 'orange', 'red']
    }
    
    risk_vis = {
        'bands': ['Risk_Level'],
        'min': 1,
        'max': 3,
        'palette': ['green', 'yellow', 'red']
    }
    
    ndci_url = processor.get_tile_url(composite, ndci_vis)
    risk_url = processor.get_tile_url(composite, risk_vis)
    
    print(f"  NDCI URL: {ndci_url[:80]}...")
    print(f"  Risk URL: {risk_url[:80]}...")
    
    print("\n✓ Processing complete!")
