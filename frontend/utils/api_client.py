"""
API client for backend communication
Centralized API calls with error handling
"""
import requests
import streamlit as st
from typing import Dict, Optional, Any
from frontend.utils.config import API_BASE_URL, API_TIMEOUT


class APIClient:
    """Client for Titicaca Sentinel API"""
    
    def __init__(self, base_url: str = API_BASE_URL):
        self.base_url = base_url
        self.timeout = API_TIMEOUT
    
    def _make_request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make HTTP GET request with error handling"""
        # Build deterministic cache key from endpoint and params
        cache_key = (endpoint, tuple(sorted(params.items())) if params else None)

        # Ensure session cache exists
        try:
            cache = st.session_state.setdefault("_api_cache", {})
        except Exception:
            # If Streamlit session_state isn't available for some reason,
            # fall back to a simple in-memory attribute on the client
            if not hasattr(self, "_local_cache"):
                self._local_cache = {}
            cache = self._local_cache

        # Return cached response if available
        if cache_key in cache:
            print(f"[DEBUG] API cache hit for {cache_key}")
            return cache[cache_key]

        # Not cached: perform request
        try:
            url = f"{self.base_url}{endpoint}"
            print(f"[DEBUG] Making request to: {url} with params: {params}")  # DEBUG

            response = requests.get(
                url,
                params=params,
                timeout=self.timeout
            )

            print(f"[DEBUG] Response status: {response.status_code}")  # DEBUG
            print(f"[DEBUG] Response headers: {dict(response.headers)}")  # DEBUG

            response.raise_for_status()

            data = response.json()
            print(f"[DEBUG] Response data keys: {list(data.keys()) if isinstance(data, dict) else 'None'}")  # DEBUG

            # Store in cache for this Streamlit session
            try:
                st.session_state.setdefault("_api_cache", {})[cache_key] = data
            except Exception:
                # fallback to local cache
                self._local_cache[cache_key] = data

            return data

        except requests.exceptions.Timeout as e:
            # Don't show error here - let caller handle it
            raise Exception(f"TIMEOUT: El procesamiento excedió el tiempo límite de {self.timeout}s")
        except requests.exceptions.HTTPError as e:
            # Don't show error here - let caller handle it
            raise Exception(f"HTTP Error: {e}")
        except Exception as e:
            # Don't show error here - let caller handle it
            raise Exception(f"Request Error: {str(e)}")
    
    # TEMPORARILY DISABLED CACHE FOR DEBUGGING
    # @st.cache_data(ttl=600, show_spinner=False)
    def get_latest_data(_self, cloud_coverage: int = 20, days: int = None, months: int = None) -> Optional[Dict]:
        """Fetch latest image data from API"""
        params = {'cloud_coverage': cloud_coverage}
        if days is not None:
            params['days'] = days
        elif months is not None:
            params['months'] = months
        
        return _self._make_request("/latest", params)
    
    # TEMPORARILY DISABLED CACHE FOR DEBUGGING
    # @st.cache_data(ttl=600, show_spinner=False)
    def get_risk_map(_self, cloud_coverage: int = 20, days: int = None, months: int = None) -> Optional[Dict]:
        """Fetch risk map data from API"""
        params = {'cloud_coverage': cloud_coverage}
        if days is not None:
            params['days'] = days
        elif months is not None:
            params['months'] = months
        
        return _self._make_request("/risk-map", params)
    
    # TEMPORARILY DISABLED CACHE FOR DEBUGGING
    # @st.cache_data(ttl=600, show_spinner=False)
    def get_time_series(
        _self, 
        start_date: str,
        end_date: str,
        lat: float, 
        lon: float, 
        cloud_coverage: int = 20
    ) -> Optional[Dict]:
        """Fetch time series data from API"""
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'lat': lat,
            'lon': lon,
            'cloud_coverage': cloud_coverage
        }
        
        return _self._make_request("/time-series", params)
    
    # TEMPORARILY DISABLED CACHE FOR DEBUGGING
    # @st.cache_data(ttl=600, show_spinner=False)
    def get_roi(_self) -> Optional[Dict]:
        """Fetch ROI geometry from API"""
        return _self._make_request("/roi")
    
    def get_comparison(
        _self,
        period1_days: int = 7,
        period2_days: int = 7,
        period2_offset: int = 30,
        cloud_coverage: int = 20
    ) -> Optional[Dict]:
        """Fetch temporal comparison data from API"""
        params = {
            'period1_days': period1_days,
            'period2_days': period2_days,
            'period2_offset': period2_offset,
            'cloud_coverage': cloud_coverage
        }
        
        return _self._make_request("/compare", params)
    
    def get_prediction(_self, metric: str = "ndci", historical_days: int = 90, forecast_days: int = 7, cloud_coverage: int = 20) -> Optional[Dict]:
        """Fetch time series predictions from API
        
        Args:
            metric: Metric to predict (ndci, ndwi, turbidity, chla_approx)
            historical_days: Days of historical data to use (30-180)
            forecast_days: Days to forecast (1-14)
            cloud_coverage: Max cloud coverage percentage
        """
        params = {
            'metric': metric,
            'historical_days': historical_days,
            'forecast_days': forecast_days,
            'cloud_coverage': cloud_coverage
        }
        
        return _self._make_request("/predict", params)
    
    def health_check(_self) -> Optional[Dict]:
        """Check API health status"""
        return _self._make_request("/health")

    def clear_cache(_self) -> None:
        """Clear the session/local API cache used to avoid repeated requests.

        This clears the Streamlit session cache (`_api_cache`) if available,
        otherwise clears the client's local fallback cache.
        """
        try:
            if "_api_cache" in st.session_state:
                st.session_state.pop("_api_cache")
                print("[DEBUG] Cleared Streamlit session API cache")
        except Exception:
            if hasattr(_self, "_local_cache"):
                _self._local_cache.clear()
                print("[DEBUG] Cleared local API cache")


# Global API client instance
api_client = APIClient()
