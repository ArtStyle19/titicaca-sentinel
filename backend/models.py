"""
Pydantic models for API requests and responses
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
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


class ROIFeature(BaseModel):
    """GeoJSON feature for ROI"""
    type: str = "Feature"
    properties: Dict
    geometry: Dict


class ROIResponse(BaseModel):
    """ROI GeoJSON response"""
    type: str = "FeatureCollection"
    features: List[ROIFeature]
