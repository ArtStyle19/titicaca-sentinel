"""
TITICACA SENTINEL - FastAPI Backend (Refactored)
Main application entry point - Scalable and maintainable architecture
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import Optional
import sys
import os

# Add parent directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import configurations and models
from backend.config import settings
from backend.models import (
    HealthResponse, LatestImageResponse, RiskMapResponse,
    TimeSeriesResponse, StatsResponse, ROIResponse, ComparisonResponse,
    PredictionResponse
)

# Import GEE processor
try:
    from gee.gee_processor import TiticacaProcessor
    from backend.services import GEEService
    import ee
except ImportError as e:
    print(f"Warning: Could not import GEE processor: {e}")
    TiticacaProcessor = None
    GEEService = None
    ee = None

# Initialize FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global service instance
gee_service: Optional[GEEService] = None


@app.on_event("startup")
async def startup_event():
    """Initialize GEE service on startup"""
    global gee_service
    try:
        if not TiticacaProcessor:
            print("⚠ GEE Processor not available")
            return
        
        # Initialize processor
        if (settings.EE_SERVICE_ACCOUNT_EMAIL and 
            settings.EE_PRIVATE_KEY_PATH and 
            os.path.exists(settings.EE_PRIVATE_KEY_PATH)):
            # Use service account
            processor = TiticacaProcessor(
                project_id=settings.GOOGLE_CLOUD_PROJECT,
                service_account=settings.EE_SERVICE_ACCOUNT_EMAIL,
                key_file=settings.EE_PRIVATE_KEY_PATH
            )
            print(f"✓ GEE Processor initialized with Service Account")
        else:
            # Use default authentication
            processor = TiticacaProcessor(project_id=settings.GOOGLE_CLOUD_PROJECT)
            print("✓ GEE Processor initialized with default credentials")
        
        # Create service
        gee_service = GEEService(processor)
        print("✓ GEE Service ready")
        
    except Exception as e:
        print(f"Error initializing GEE: {e}")
        import traceback
        traceback.print_exc()


def get_service() -> GEEService:
    """Dependency injection for GEE service"""
    if not gee_service:
        raise HTTPException(
            status_code=503, 
            detail="GEE service not available"
        )
    return gee_service


# ============================================================================
# API Routes
# ============================================================================

@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(),
        gee_available=gee_service is not None
    )


@app.get("/latest", response_model=LatestImageResponse)
async def get_latest_image(
    months: Optional[int] = Query(None, description="Number of months to look back"),
    cloud_coverage: int = Query(
        settings.DEFAULT_CLOUD_COVERAGE, 
        ge=10, 
        le=settings.MAX_CLOUD_COVERAGE,
        description="Maximum cloud coverage percentage"
    ),
    days: Optional[int] = Query(None, description="Number of days to look back (overrides months)"),
    force_refresh: bool = Query(False, description="Force refresh bypassing cache"),
    service: GEEService = Depends(get_service)
):
    """Get the latest processed Sentinel-2 image with water quality indices"""
    try:
        # Resolve period in days (we cache by days)
        if days:
            period_days = days
        else:
            period_days = (months or settings.DEFAULT_MONTHS) * 30

        # Use cached lightweight payload when available (tile urls, stats)
        payload = service.get_cached_for_period(days=period_days, cloud_coverage=cloud_coverage, end_offset=0, force=force_refresh)
        date = payload.get('date')
        tile_urls = payload.get('tile_urls', {})
        stats = payload.get('statistics', {})
        
        return LatestImageResponse(
            date=date,
            tile_urls=tile_urls,
            statistics=stats
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/risk-map", response_model=RiskMapResponse)
async def get_risk_map(
    months: Optional[int] = Query(None, description="Number of months to look back"),
    cloud_coverage: int = Query(
        settings.DEFAULT_CLOUD_COVERAGE,
        ge=10,
        le=settings.MAX_CLOUD_COVERAGE,
        description="Maximum cloud coverage percentage"
    ),
    days: Optional[int] = Query(None, description="Number of days to look back (overrides months)"),
    force_refresh: bool = Query(False, description="Force refresh bypassing cache"),
    service: GEEService = Depends(get_service)
):
    """Get environmental risk classification map"""
    try:
        # Resolve period in days
        if days:
            period_days = days
        else:
            period_days = (months or settings.DEFAULT_MONTHS) * 30

        payload = service.get_cached_for_period(days=period_days, cloud_coverage=cloud_coverage, end_offset=0, force=force_refresh)
        date = payload.get('date')
        risk_url = payload.get('risk_url')
        risk_zones = payload.get('risk_zones', {})
        
        return RiskMapResponse(
            date=date,
            tile_url=risk_url,
            risk_zones=risk_zones
        )
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/time-series", response_model=TimeSeriesResponse)
async def get_time_series(
    lat: float = Query(..., description="Latitude", ge=-17.5, le=-15.0),
    lon: float = Query(..., description="Longitude", ge=-70.5, le=-68.0),
    months: int = Query(settings.DEFAULT_MONTHS, description="Number of months to look back"),
    cloud_coverage: int = Query(
        settings.DEFAULT_CLOUD_COVERAGE,
        ge=10,
        le=settings.MAX_CLOUD_COVERAGE,
        description="Maximum cloud coverage percentage"
    ),
    service: GEEService = Depends(get_service)
):
    """Get time series data for a specific location within Lake Titicaca"""
    try:
        # Get time series data
        ts_data = service.get_time_series_data(
            lat=lat,
            lon=lon,
            months=months,
            cloud_coverage=cloud_coverage
        )
        
        # Parse features
        data_points = service.parse_time_series(ts_data)
        
        return TimeSeriesResponse(
            location={'lat': lat, 'lon': lon},
            data=data_points
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=StatsResponse)
async def get_statistics(
    months: Optional[int] = Query(None, description="Number of months to look back"),
    cloud_coverage: int = Query(
        settings.DEFAULT_CLOUD_COVERAGE,
        ge=10,
        le=settings.MAX_CLOUD_COVERAGE,
        description="Maximum cloud coverage percentage"
    ),
    days: Optional[int] = Query(None, description="Number of days to look back"),
    force_refresh: bool = Query(False, description="Force refresh bypassing cache"),
    service: GEEService = Depends(get_service)
):
    """Get comprehensive lake statistics"""
    try:
        # Resolve period in days and use cache-aware retrieval
        if days:
            period_days = days
        else:
            period_days = (months or settings.DEFAULT_MONTHS) * 30

        payload = service.get_cached_for_period(days=period_days, cloud_coverage=cloud_coverage, end_offset=0, force=force_refresh)
        date = payload.get('date')
        stats = payload.get('statistics', {})

        # Organize statistics
        organized_stats = service.organize_statistics(stats, date)
        
        return StatsResponse(**organized_stats)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/roi", response_model=ROIResponse)
async def get_roi(service: GEEService = Depends(get_service)):
    """Get Lake Titicaca ROI geometry as GeoJSON"""
    try:
        return service.get_roi_geojson()
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/compare")
async def compare_periods(
    period1_days: int = Query(7, description="Days for recent period"),
    period2_days: int = Query(7, description="Days for comparison period"),
    period2_offset: int = Query(30, description="Days to offset period 2 from present"),
    cloud_coverage: int = Query(
        settings.DEFAULT_CLOUD_COVERAGE,
        ge=10,
        le=settings.MAX_CLOUD_COVERAGE,
        description="Maximum cloud coverage percentage"
    ),
    force_refresh: bool = Query(False, description="Force refresh both periods and bypass cache"),
    service: GEEService = Depends(get_service)
):
    """Compare two temporal periods to detect changes
    
    Example: Compare last 7 days vs 7 days from 30 days ago
    """
    try:
        comparison = service.compare_periods(
            period1_days=period1_days,
            period2_days=period2_days,
            period2_offset_days=period2_offset,
            force=force_refresh,
            cloud_coverage=cloud_coverage
        )
        
        return comparison
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/predict", response_model=PredictionResponse, tags=["Prediction"])
async def predict_time_series(
    metric: str = Query("ndci", description="Metric to predict: ndci, ndwi, turbidity, or chla_approx"),
    historical_days: int = Query(90, ge=30, le=180, description="Days of historical data to use"),
    forecast_days: int = Query(7, ge=1, le=14, description="Days to forecast into future"),
    cloud_coverage: int = Query(
        settings.DEFAULT_CLOUD_COVERAGE,
        ge=10,
        le=settings.MAX_CLOUD_COVERAGE,
        description="Maximum cloud coverage percentage"
    ),
    service: GEEService = Depends(get_service)
):
    """Predict future values using Prophet time series forecasting
    
    Uses historical satellite data to predict future values of water quality metrics.
    Includes confidence intervals and automatic alerts for predicted threshold exceedances.
    
    **Supported metrics:**
    - `ndci`: Normalized Difference Chlorophyll Index (algal blooms)
    - `ndwi`: Normalized Difference Water Index (water presence)
    - `turbidity`: Water turbidity (sediment load)
    - `chla_approx`: Approximate Chlorophyll-a concentration (µg/L)
    
    **Example use cases:**
    - Predict algal bloom likelihood 7 days ahead
    - Forecast turbidity trends after rainfall
    - Early warning for water quality degradation
    """
    try:
        # Validate metric
        valid_metrics = ['ndci', 'ndwi', 'turbidity', 'chla_approx']
        if metric not in valid_metrics:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid metric '{metric}'. Must be one of: {', '.join(valid_metrics)}"
            )
        
        print(f"[PREDICT] Starting prediction for {metric}, {historical_days} days, forecast {forecast_days}")
        
        prediction = service.predict_time_series(
            metric=metric,
            historical_days=historical_days,
            forecast_days=forecast_days,
            cloud_coverage=cloud_coverage
        )
        
        print(f"[PREDICT] Prediction completed successfully")
        
        return prediction
    
    except ValueError as e:
        print(f"[PREDICT ERROR] ValueError: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except ImportError as e:
        print(f"[PREDICT ERROR] ImportError: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Prophet library not installed. Run: pip install prophet"
        )
    except Exception as e:
        print(f"[PREDICT ERROR] Exception: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Application Entry Point
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.API_RELOAD,
        timeout_keep_alive=300  # 5 minutos para procesamiento largo de GEE
    )
