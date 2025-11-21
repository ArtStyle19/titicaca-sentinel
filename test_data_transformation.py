#!/usr/bin/env python3
"""Test data transformation from backend to frontend format"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from frontend.utils.helpers import transform_statistics
import json

# Simulate backend response
backend_stats = {
    "CI_green_mean": -0.2201751061425121,
    "CI_green_p10": -0.4212246171888529,
    "CI_green_p50": -0.170775699353954,
    "CI_green_p90": -0.07929827816398505,
    "CI_green_stdDev": 0.3075619007774737,
    "Chla_approx_mean": 29.352025965929748,
    "Chla_approx_p10": 27.12838594326285,
    "Chla_approx_p50": 29.635081376705912,
    "Chla_approx_p90": 30.105327995557495,
    "Chla_approx_stdDev": 2.93641895921176,
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
    "TSM_mean": 0.962755178260409,
    "TSM_p10": 0.918460340065828,
    "TSM_p50": 0.9708063994476805,
    "TSM_p90": 1.017322111610003,
    "TSM_stdDev": 0.2693052880067356,
    "Turbidity_mean": 0.7947199263795528,
    "Turbidity_p10": 0.6183344150983114,
    "Turbidity_p50": 0.8519589693660584,
    "Turbidity_p90": 0.9291437512058
}

print("=" * 60)
print("BACKEND STATS (original):")
print("=" * 60)
print(json.dumps(backend_stats, indent=2))

print("\n" + "=" * 60)
print("TRANSFORMED STATS (frontend format):")
print("=" * 60)

transformed = transform_statistics(backend_stats)
print(json.dumps(transformed, indent=2))

print("\n" + "=" * 60)
print("VERIFICATION:")
print("=" * 60)
print(f"✓ NDCI mean: {transformed['ndci'].get('mean', 'MISSING')}")
print(f"✓ NDWI mean: {transformed['ndwi'].get('mean', 'MISSING')}")
print(f"✓ Turbidity mean: {transformed['turbidity'].get('mean', 'MISSING')}")
print(f"✓ Chlorophyll mean: {transformed['chlorophyll'].get('mean', 'MISSING')}")
print("=" * 60)
