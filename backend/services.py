"""
Service layer for GEE operations
"""
from typing import Dict, Tuple, Optional, List
import ee
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from backend.models import TimeSeriesPoint
import pandas as pd
import numpy as np


class GEEService:
    """Service for Google Earth Engine operations"""
    
    def __init__(self, processor):
        """Initialize with GEE processor instance"""
        self.processor = processor
        # Cache directory for storing lightweight results (tile URLs, stats)
        self.cache_dir = Path('./data/cache')
        self.cache_dir.mkdir(parents=True, exist_ok=True)
    
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

    # --------------------- CACHING HELPERS ---------------------
    def _cache_filename(self, days: int, cloud_coverage: int, end_offset: int) -> str:
        return f"latest_{days}d_cloud{cloud_coverage}_offset{end_offset}.json"

    def _cache_path(self, days: int, cloud_coverage: int, end_offset: int) -> Path:
        return self.cache_dir / self._cache_filename(days, cloud_coverage, end_offset)

    def _is_cache_valid(self, path: Path, ttl_days: int = 5) -> bool:
        if not path.exists():
            return False
        try:
            with open(path, 'r') as f:
                payload = json.load(f)
            cached_at = payload.get('cached_at')
            if not cached_at:
                return False
            cached_time = datetime.fromisoformat(cached_at)
            return (datetime.utcnow() - cached_time) <= timedelta(days=ttl_days)
        except Exception:
            return False

    def get_cached_for_period(self, days: int, cloud_coverage: int = 20, end_offset: int = 0, force: bool = False) -> Dict:
        """Return cached statistics and tile URLs for the specified period.

        If cache is invalid or `force` is True, runs GEE processing once and caches
        lightweight artifacts (statistics, tile urls, risk url, risk_zones).
        """
        cache_path = self._cache_path(days, cloud_coverage, end_offset)

        if not force and self._is_cache_valid(cache_path):
            try:
                with open(cache_path, 'r') as f:
                    data = json.load(f)
                return data
            except Exception as e:
                print(f"Warning: Failed to load cache {cache_path}: {e}")

        # Cache miss or forced refresh -> run heavy processing once
        print(f"Cache miss or refresh requested for period={days}d offset={end_offset} - running GEE processing...")
        composite, roi, date = self.processor.process_latest(days=days, cloud_coverage=cloud_coverage, end_date_offset=end_offset)

        # Compute lightweight results
        stats = self.get_statistics(composite, roi)
        tiles = self.generate_tile_urls(composite)
        risk_url = self.get_risk_map_url(composite)
        risk_zones = self.calculate_risk_zones(composite, roi)

        payload = {
            'date': date,
            'statistics': stats,
            'tile_urls': tiles,
            'risk_url': risk_url,
            'risk_zones': risk_zones,
            'params': {
                'days': days,
                'cloud_coverage': cloud_coverage,
                'end_offset': end_offset
            },
            'cached_at': datetime.utcnow().isoformat()
        }

        try:
            with open(cache_path, 'w') as f:
                json.dump(payload, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not write cache to {cache_path}: {e}")

        return payload
    
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
    
    def compare_periods(
        self,
        period1_days: int,
        period2_days: int,
        period2_offset_days: int,
        force: bool = False,
        cloud_coverage: int = 20
    ) -> Dict:
        """Compare two temporal periods
        
        Args:
            period1_days: Days for recent period
            period2_days: Days for comparison period
            period2_offset_days: Days to offset period2 from present
            cloud_coverage: Max cloud coverage
            
        Returns:
            Dictionary with comparison data
        """
        # Get data for both periods (use cache to avoid repeated heavy GEE calls)
        p1 = self.get_cached_for_period(days=period1_days, cloud_coverage=cloud_coverage, end_offset=0, force=force)
        p2 = self.get_cached_for_period(days=period2_days, cloud_coverage=cloud_coverage, end_offset=period2_offset_days, force=force)

        date1 = p1.get('date')
        stats1 = p1.get('statistics', {})
        tiles1 = p1.get('tile_urls', {})

        date2 = p2.get('date')
        stats2 = p2.get('statistics', {})
        tiles2 = p2.get('tile_urls', {})
        
        # Calculate changes and detect anomalies
        changes = {}
        percent_changes = {}
        alerts = []
        
        # Key indices to monitor
        key_indices = ['NDCI_mean', 'NDWI_mean', 'Turbidity_mean', 'Chla_approx_mean']
        
        for key in key_indices:
            if key in stats1 and key in stats2:
                val1 = stats1[key]
                val2 = stats2[key]
                change = val1 - val2
                changes[key] = change
                
                # Calculate percent change (avoid division by zero)
                if abs(val2) > 0.001:
                    pct_change = (change / val2) * 100
                    percent_changes[key] = pct_change
                    
                    # Alert if change > 20%
                    if abs(pct_change) > 20:
                        index_name = key.replace('_mean', '').replace('_', ' ').title()
                        direction = "aumento" if pct_change > 0 else "disminución"
                        alerts.append({
                            'index': index_name,
                            'change': f"{pct_change:+.1f}%",
                            'message': f"{index_name}: {direction} significativo de {abs(pct_change):.1f}%",
                            'severity': 'high' if abs(pct_change) > 50 else 'medium'
                        })
        
        return {
            'period1': {
                'date': date1,
                'statistics': stats1,
                'tile_urls': tiles1
            },
            'period2': {
                'date': date2,
                'statistics': stats2,
                'tile_urls': tiles2
            },
            'changes': changes,
            'percent_changes': percent_changes,
            'alerts': alerts
        }
    
    def predict_time_series(
        self,
        metric: str = 'ndci',
        historical_days: int = 90,
        forecast_days: int = 7,
        cloud_coverage: int = 20
    ) -> Dict:
        """Predict future values using Prophet time series forecasting
        
        Args:
            metric: Metric to predict (ndci, ndwi, turbidity, chla_approx)
            historical_days: Days of historical data to use
            forecast_days: Days to forecast into future
            cloud_coverage: Max cloud coverage
            
        Returns:
            Dictionary with predictions and model metrics
        """
        try:
            from prophet import Prophet
        except ImportError:
            raise ImportError("Prophet not installed. Run: pip install prophet")
        
        # Get historical data
        historical_data = []
        errors = []
        
        # Collect data points from past historical_days
        # Sample every 14 days to reduce GEE calls while maintaining trend
        sample_interval = 14 if historical_days >= 60 else 7
        
        print(f"[PREDICT] Collecting historical data with interval {sample_interval} days")
        
        for offset in range(0, historical_days, sample_interval):
            try:
                print(f"[PREDICT] Fetching data for offset {offset} days...")
                data = self.get_cached_for_period(
                    days=7,
                    cloud_coverage=cloud_coverage,
                    end_offset=offset,
                    force=False
                )
                
                stats = data.get('statistics', {})
                date_str = data.get('date', '')
                
                print(f"[PREDICT] Got data for date {date_str}, stats keys: {list(stats.keys())}")
                
                # Extract mean value for the metric
                # Stats keys are in UPPERCASE, but metric param is lowercase
                # Map lowercase metric to uppercase stat key
                metric_mapping = {
                    'ndci': 'NDCI_mean',
                    'ndwi': 'NDWI_mean',
                    'turbidity': 'Turbidity_mean',
                    'chla_approx': 'Chla_approx_mean'
                }
                
                metric_key = metric_mapping.get(metric.lower())
                
                if not metric_key:
                    print(f"[PREDICT] Unknown metric: {metric}")
                    continue
                
                print(f"[PREDICT] Looking for metric key: {metric_key}")
                
                if metric_key in stats:
                    value = stats[metric_key]
                    print(f"[PREDICT] Found value {value} for {metric_key} at {date_str}")
                    historical_data.append({
                        'ds': date_str,  # Prophet expects 'ds' column
                        'y': value  # Prophet expects 'y' column
                    })
                else:
                    print(f"[PREDICT] Metric key {metric_key} not found in stats")
            except Exception as e:
                print(f"[PREDICT] Error at offset {offset}: {str(e)}")
                errors.append(f"Error at offset {offset}: {str(e)}")
                continue
        
        print(f"[PREDICT] Collected {len(historical_data)} historical data points")
        if errors:
            print(f"[PREDICT] Errors encountered: {errors}")
        if len(historical_data) < 3:
            raise ValueError(f"Insufficient historical data: {len(historical_data)} points. Need at least 3.")
        
        # Prepare DataFrame for Prophet
        df = pd.DataFrame(historical_data)
        df['ds'] = pd.to_datetime(df['ds'])
        df = df.sort_values('ds')
        
        # Train Prophet model
        model = Prophet(
            daily_seasonality=False,
            weekly_seasonality=True,
            yearly_seasonality=False,
            interval_width=0.95,  # 95% confidence interval
            changepoint_prior_scale=0.05  # Less flexible to avoid overfitting
        )
        
        model.fit(df)
        
        # Create future dataframe
        future = model.make_future_dataframe(periods=forecast_days, freq='D')
        
        # Make predictions
        forecast = model.predict(future)
        
        # Extract only future predictions
        predictions_df = forecast[forecast['ds'] > df['ds'].max()]
        
        # Format predictions
        predictions = []
        alerts = []
        
        # Define thresholds for alerts
        thresholds = {
            'ndci': {'high': 0.2, 'critical': 0.3},
            'ndwi': {'low': 0, 'critical_low': -0.2},
            'turbidity': {'high': 1.5, 'critical': 2.0},
            'chla_approx': {'high': 30, 'critical': 50}
        }
        
        for _, row in predictions_df.iterrows():
            pred_point = {
                'date': row['ds'].strftime('%Y-%m-%d'),
                'predicted_value': float(row['yhat']),
                'lower_bound': float(row['yhat_lower']),
                'upper_bound': float(row['yhat_upper']),
                'confidence': 0.95  # Based on interval_width
            }
            predictions.append(pred_point)
            
            # Check for alerts
            if metric in thresholds:
                value = row['yhat']
                threshold = thresholds[metric]
                
                if metric == 'ndci':
                    if value > threshold['critical']:
                        alerts.append({
                            'date': row['ds'].strftime('%Y-%m-%d'),
                            'severity': 'critical',
                            'message': f'ALERTA CRÍTICA: NDCI predicho {value:.3f} indica florecimiento algal severo',
                            'recommendation': 'Activar protocolo de emergencia. Muestreo in-situ inmediato.'
                        })
                    elif value > threshold['high']:
                        alerts.append({
                            'date': row['ds'].strftime('%Y-%m-%d'),
                            'severity': 'high',
                            'message': f'ALERTA: NDCI predicho {value:.3f} indica alto riesgo de eutrofización',
                            'recommendation': 'Incrementar monitoreo. Preparar equipos de muestreo.'
                        })
                
                elif metric == 'turbidity':
                    if value > threshold['critical']:
                        alerts.append({
                            'date': row['ds'].strftime('%Y-%m-%d'),
                            'severity': 'critical',
                            'message': f'ALERTA CRÍTICA: Turbidez predicha {value:.3f} extremadamente alta',
                            'recommendation': 'Investigar fuentes de sedimentación. Revisar erosión.'
                        })
                    elif value > threshold['high']:
                        alerts.append({
                            'date': row['ds'].strftime('%Y-%m-%d'),
                            'severity': 'high',
                            'message': f'ALERTA: Turbidez predicha {value:.3f} elevada',
                            'recommendation': 'Monitorear fuentes de sedimentos.'
                        })
                
                elif metric == 'ndwi':
                    if value < threshold['critical_low']:
                        alerts.append({
                            'date': row['ds'].strftime('%Y-%m-%d'),
                            'severity': 'high',
                            'message': f'ALERTA: NDWI predicho {value:.3f} muy bajo',
                            'recommendation': 'Verificar niveles de agua. Posible sequía.'
                        })
                
                elif metric == 'chla_approx':
                    if value > threshold['critical']:
                        alerts.append({
                            'date': row['ds'].strftime('%Y-%m-%d'),
                            'severity': 'critical',
                            'message': f'ALERTA CRÍTICA: Clorofila-a predicha {value:.1f} µg/L crítica',
                            'recommendation': 'Florecimiento algal severo esperado. Alertar autoridades.'
                        })
                    elif value > threshold['high']:
                        alerts.append({
                            'date': row['ds'].strftime('%Y-%m-%d'),
                            'severity': 'high',
                            'message': f'ALERTA: Clorofila-a predicha {value:.1f} µg/L elevada',
                            'recommendation': 'Riesgo moderado de bloom algal.'
                        })
        
        # Calculate model metrics (on historical data)
        # Split data for validation
        train_size = int(len(df) * 0.8)
        train_df = df[:train_size]
        test_df = df[train_size:]
        
        if len(test_df) > 0:
            # Retrain on training set
            val_model = Prophet(
                daily_seasonality=False,
                weekly_seasonality=True,
                yearly_seasonality=False,
                interval_width=0.95
            )
            val_model.fit(train_df)
            
            # Predict on test set
            test_forecast = val_model.predict(test_df[['ds']])
            
            # Calculate metrics
            mae = np.mean(np.abs(test_df['y'].values - test_forecast['yhat'].values))
            rmse = np.sqrt(np.mean((test_df['y'].values - test_forecast['yhat'].values) ** 2))
            
            # Calculate MAPE with protection against division by zero
            # Use a more robust approach: only calculate for non-zero values
            y_values = test_df['y'].values
            y_pred = test_forecast['yhat'].values
            
            # Filter out values too close to zero (< 1% of range)
            y_range = np.max(np.abs(y_values)) - np.min(np.abs(y_values))
            threshold = max(0.001, y_range * 0.01)
            
            mask = np.abs(y_values) > threshold
            if np.sum(mask) > 0:
                mape = np.mean(np.abs((y_values[mask] - y_pred[mask]) / y_values[mask])) * 100
                # Cap MAPE at 100% for display purposes
                mape = min(mape, 100.0)
            else:
                # If all values are too small, use normalized MAE instead
                # This gives a percentage-like metric
                if np.max(np.abs(y_values)) > 0:
                    mape = (mae / np.max(np.abs(y_values))) * 100
                    mape = min(mape, 100.0)
                else:
                    mape = 0.0
        else:
            # Not enough data for validation
            mae = 0.0
            rmse = 0.0
            mape = 0.0
        
        # Format historical data for response
        historical_formatted = [
            {
                'date': row['ds'].strftime('%Y-%m-%d'),
                'value': float(row['y'])
            }
            for _, row in df.iterrows()
        ]
        
        return {
            'metric': metric,
            'historical_data': historical_formatted,
            'predictions': predictions,
            'forecast_days': forecast_days,
            'model_metrics': {
                'mae': float(mae),
                'rmse': float(rmse),
                'mape': float(mape),
                'data_points': len(df)
            },
            'alerts': alerts,
            'generated_at': datetime.now().isoformat()
        }
