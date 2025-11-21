#!/usr/bin/env python3
"""
Quick test script to verify the API is working
"""

import requests
import json
import sys

API_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("Testing /health endpoint...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        data = response.json()
        
        print(f"  Status: {data['status']}")
        print(f"  GEE Available: {data['gee_available']}")
        
        if data['gee_available']:
            print("  ✅ GEE is working!")
            return True
        else:
            print("  ❌ GEE is NOT available")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_roi():
    """Test ROI endpoint"""
    print("\nTesting /roi endpoint...")
    try:
        response = requests.get(f"{API_URL}/roi", timeout=30)
        data = response.json()
        
        if 'features' in data and len(data['features']) > 0:
            area = data['features'][0]['properties'].get('area_km2', 0)
            print(f"  ✅ ROI loaded: {area:.2f} km²")
            return True
        else:
            print("  ❌ No ROI data")
            return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_latest():
    """Test latest endpoint"""
    print("\nTesting /latest endpoint (this may take 30-60 seconds)...")
    try:
        response = requests.get(
            f"{API_URL}/latest",
            params={'months': 6, 'cloud_coverage': 30},
            timeout=120
        )
        data = response.json()
        
        print(f"  ✅ Latest image date: {data['date']}")
        print(f"  ✅ Tile URLs generated: {len(data['tile_urls'])}")
        print(f"  ✅ Statistics available: {len(data['statistics'])}")
        return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("=" * 60)
    print("TITICACA SENTINEL - API TEST")
    print("=" * 60)
    print()
    
    results = []
    
    # Test health
    results.append(("Health Check", test_health()))
    
    if not results[0][1]:
        print("\n❌ Backend is not running or GEE is not available")
        print("\nMake sure the backend is running:")
        print("  ./start_backend.sh")
        return 1
    
    # Test ROI
    results.append(("ROI Extraction", test_roi()))
    
    # Test latest
    results.append(("Latest Image", test_latest()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} {test_name}")
        if not passed:
            all_passed = False
    
    print()
    
    if all_passed:
        print("🎉 All API tests passed!")
        print("\nYou can now:")
        print("  1. Open dashboard: http://localhost:8501")
        print("  2. View API docs: http://localhost:8000/docs")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
