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
    TimeSeriesResponse, StatsResponse, ROIResponse
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
    service: GEEService = Depends(get_service)
):
    """Get the latest processed Sentinel-2 image with water quality indices"""
    try:
        # Use days if provided, otherwise use months or default
        period_months = None if days else (months or settings.DEFAULT_MONTHS)
        
        # Get latest image data
        composite, roi, date = service.get_latest_image_data(
            months=period_months,
            cloud_coverage=cloud_coverage,
            days=days
        )
        
        # Get statistics
        stats = service.get_statistics(composite, roi)
        
        # Generate tile URLs
        tile_urls = service.generate_tile_urls(composite)
        
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
    service: GEEService = Depends(get_service)
):
    """Get environmental risk classification map"""
    try:
        # Use days if provided, otherwise use months or default
        period_months = None if days else (months or settings.DEFAULT_MONTHS)
        
        # Process latest data
        composite, roi, date = service.get_latest_image_data(
            months=period_months,
            cloud_coverage=cloud_coverage,
            days=days
        )
        
        # Generate risk map tile URL
        risk_url = service.get_risk_map_url(composite)
        
        # Calculate risk zones statistics
        risk_zones = service.calculate_risk_zones(composite, roi)
        
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
    service: GEEService = Depends(get_service)
):
    """Get comprehensive lake statistics"""
    try:
        # Use days if provided, otherwise use months or default
        period_months = None if days else (months or settings.DEFAULT_MONTHS)
        
        # Process latest data
        composite, roi, date = service.get_latest_image_data(
            months=period_months,
            cloud_coverage=cloud_coverage,
            days=days
        )
        
        # Get statistics
        stats = service.get_statistics(composite, roi)
        
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
