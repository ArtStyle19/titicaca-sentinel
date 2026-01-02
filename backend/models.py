"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    gee_available: bool


class LatestImageResponse(BaseModel):
    """Latest image data response"""
    date: str
    tile_urls: Dict[str, str]
    statistics: Dict[str, float]


class RiskMapResponse(BaseModel):
    """Risk map response"""
    date: str
    tile_url: str
    risk_zones: Dict[str, int]


class TimeSeriesPoint(BaseModel):
    """Single time series data point"""
    date: str
    ndwi: Optional[float] = None
    ndci: Optional[float] = None
    ci_green: Optional[float] = None
    turbidity: Optional[float] = None
    chla_approx: Optional[float] = None


class TimeSeriesResponse(BaseModel):
    """Time series response"""
    location: Dict[str, float]
    data: List[TimeSeriesPoint]


class StatsResponse(BaseModel):
    """Statistics response"""
    date: str
    statistics: Dict[str, float]
    percentiles: Dict[str, Dict[str, float]]


class ComparisonResponse(BaseModel):
    """Temporal comparison response"""
    period1: Dict[str, Any]  # {date, statistics, tile_urls}
    period2: Dict[str, Any]  # {date, statistics, tile_urls}
    changes: Dict[str, float]  # Absolute changes
    percent_changes: Dict[str, float]  # Percentage changes
    alerts: List[Dict[str, str]]  # Significant changes detected


class PredictionPoint(BaseModel):
    """Single prediction point"""
    date: str
    predicted_value: float
    lower_bound: float
    upper_bound: float
    confidence: float = Field(..., ge=0, le=1, description="Prediction confidence (0-1)")


class PredictionResponse(BaseModel):
    """Time series prediction response"""
    metric: str  # ndci, ndwi, turbidity, chla_approx
    historical_data: List[Dict[str, Any]]  # Historical time series
    predictions: List[Dict[str, Any]]  # Future predictions (changed from List[PredictionPoint])
    forecast_days: int
    model_metrics: Dict[str, float]  # MAE, RMSE, etc
    alerts: List[Dict[str, str]]  # Alerts if predicted values exceed thresholds
    generated_at: str


class ROIFeature(BaseModel):
    """GeoJSON feature for ROI"""
    type: str = "Feature"
    properties: Dict
    geometry: Dict


class ROIResponse(BaseModel):
    """ROI GeoJSON response"""
    type: str = "FeatureCollection"
    features: List[ROIFeature]
