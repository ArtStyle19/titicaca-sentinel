#!/usr/bin/env python3
"""
Optimized quick test for Titicaca Sentinel
Tests with faster parameters for quicker response
"""

import requests
import time
import sys

API_URL = "http://localhost:8000"

def test_with_params(months, cloud_coverage):
    """Test API with specific parameters"""
    print(f"\n{'='*60}")
    print(f"Testing with: months={months}, cloud_coverage={cloud_coverage}%")
    print('='*60)
    
    print("\n1️⃣  Testing /health...")
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        data = response.json()
        
        if not data.get('gee_available'):
            print("  ❌ GEE not available. Backend needs to be restarted.")
            return False
        
        print(f"  ✅ Backend healthy, GEE available")
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False
    
    print("\n2️⃣  Testing /risk-map (this may take 1-3 minutes on first run)...")
    start_time = time.time()
    
    try:
        response = requests.get(
            f"{API_URL}/risk-map",
            params={
                'months': months,
                'cloud_coverage': cloud_coverage
            },
            timeout=180
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Success! Processed in {elapsed:.1f} seconds")
            print(f"     Date: {data.get('date')}")
            print(f"     Risk zones: {len(data.get('risk_zones', {}))}")
            return True
        else:
            print(f"  ❌ Error: {response.status_code}")
            print(f"     {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        elapsed = time.time() - start_time
        print(f"  ⏱️  Timeout after {elapsed:.1f} seconds")
        print(f"     Try reducing months or increasing cloud_coverage")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    print("🌊 TITICACA SENTINEL - OPTIMIZED API TEST")
    print("\nThis script tests with optimized parameters for faster response")
    
    # Test with faster parameters first
    test_configs = [
        (3, 40),   # 3 months, 40% clouds - fastest
        (6, 30),   # 6 months, 30% clouds - moderate
        (6, 20),   # 6 months, 20% clouds - full quality
    ]
    
    for months, clouds in test_configs:
        success = test_with_params(months, clouds)
        
        if success:
            print(f"\n{'='*60}")
            print("✅ RECOMMENDATION:")
            print(f"   Use months={months}, cloud_coverage={clouds}% in the dashboard")
            print(f"   for optimal performance")
            print('='*60)
            
            print("\n💡 TIP: Results are cached for 10 minutes.")
            print("   Subsequent requests will be instant!")
            
            print("\n🚀 Ready to use the dashboard:")
            print("   http://localhost:8501")
            
            return 0
        
        print(f"\n⚠️  Configuration {months} months / {clouds}% clouds failed or timed out")
        print("   Trying next configuration...")
        time.sleep(2)
    
    print("\n❌ All configurations failed")
    print("\nTroubleshooting:")
    print("  1. Make sure backend is running: ./start_backend.sh")
    print("  2. Check backend logs for errors")
    print("  3. Try: curl http://localhost:8000/health")
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
