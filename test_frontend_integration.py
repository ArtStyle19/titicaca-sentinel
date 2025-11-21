#!/usr/bin/env python3
"""Test frontend data integration"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from frontend.utils.helpers import transform_statistics

# Simulate backend response
backend_stats = {
    "NDCI_mean": -0.012992958877151515,
    "NDCI_p10": -0.0584247854255414,
    "NDCI_p50": -0.0037990020254281536,
    "NDCI_p90": 0.002823967703015508,
    "NDCI_stdDev": 0.05894268650612631,
    "NDWI_mean": -0.15193325109631015,
    "NDWI_p10": -0.29293518576439465,
    "NDWI_p50": -0.09751186856153517,
    "NDWI_p90": -0.04303618346564629,
    "NDWI_stdDev": 0.18214386184410905,
    "Turbidity_mean": 0.7947199263795528,
    "Turbidity_p10": 0.6183344150983114,
    "Turbidity_p50": 0.8519589693660584,
    "Turbidity_p90": 0.9291437512058
}

print("=" * 70)
print("TESTING STATISTICS TRANSFORMATION")
print("=" * 70)

transformed = transform_statistics(backend_stats)

print("\n✅ Transformed keys:", list(transformed.keys()))

for index_name in ['ndci', 'ndwi', 'turbidity']:
    if index_name in transformed:
        stats = transformed[index_name]
        print(f"\n{index_name.upper()}:")
        print(f"  - mean: {stats.get('mean', 'MISSING')}")
        print(f"  - median: {stats.get('median', 'MISSING')}")
        print(f"  - min: {stats.get('min', 'MISSING')}")
        print(f"  - max: {stats.get('max', 'MISSING')}")
        print(f"  - std: {stats.get('std', 'MISSING')}")

# Simulate time series data
print("\n" + "=" * 70)
print("TESTING TIME SERIES DATA STRUCTURE")
print("=" * 70)

time_series_sample = [
    {
        "date": "2025-06-11",
        "ndwi": -0.24242423743552324,
        "ndci": 0.012195109389722347,
        "ci_green": -0.3902438959753537,
        "turbidity": 0.6585366241478777,
        "chla_approx": 30.609755469486117
    }
]

print("\n✅ Time series keys:", list(time_series_sample[0].keys()))
print("   Expected by frontend: 'date', 'ndwi', 'ndci', 'turbidity'")

# Check for case sensitivity
required_keys = ['date', 'ndwi', 'ndci', 'turbidity']
available_keys = list(time_series_sample[0].keys())

print("\n" + "=" * 70)
print("KEY VALIDATION")
print("=" * 70)

for key in required_keys:
    if key in available_keys:
        print(f"✅ '{key}' - FOUND")
    else:
        print(f"❌ '{key}' - MISSING")

print("\n" + "=" * 70)
print("ALL TESTS COMPLETE")
print("=" * 70)
