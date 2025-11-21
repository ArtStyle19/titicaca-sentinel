#!/usr/bin/env python3
"""
Quick API test using days instead of months for faster iteration
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🏥 Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ GEE Available: {data['gee_available']}")
        return data['gee_available']
    return False

def test_with_days(days, cloud_coverage):
    """Test API with specific days and cloud coverage"""
    print(f"\n{'='*60}")
    print(f"Testing with {days} days, {cloud_coverage}% cloud coverage")
    print(f"{'='*60}")
    
    start_time = datetime.now()
    
    # Test /latest endpoint
    print(f"\n📊 Testing /latest endpoint...")
    try:
        response = requests.get(
            f"{BASE_URL}/latest",
            params={"days": days, "cloud_coverage": cloud_coverage},
            timeout=180
        )
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"Status: {response.status_code} (took {elapsed:.1f}s)")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Date: {data['date']}")
            print(f"✅ Statistics: {', '.join(data['statistics'].keys())}")
            
            # Show some statistical values
            for stat_name, stat_value in list(data['statistics'].items())[:3]:
                print(f"   - {stat_name}: {stat_value:.4f}")
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except requests.Timeout:
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"⏱️  Request timed out after {elapsed:.1f}s")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    # Test /risk-map endpoint
    print(f"\n🗺️  Testing /risk-map endpoint...")
    start_time = datetime.now()
    try:
        response = requests.get(
            f"{BASE_URL}/risk-map",
            params={"days": days, "cloud_coverage": cloud_coverage},
            timeout=180
        )
        
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"Status: {response.status_code} (took {elapsed:.1f}s)")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Date: {data['date']}")
            print(f"✅ Risk zones: {data.get('risk_zones', {})}")
            print(f"✅ Tile URL: {data['tile_url'][:80]}...")
            return True
        else:
            print(f"❌ Error: {response.text}")
            return False
            
    except requests.Timeout:
        elapsed = (datetime.now() - start_time).total_seconds()
        print(f"⏱️  Request timed out after {elapsed:.1f}s")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("🚀 Titicaca Sentinel API - Quick Test with Days")
    print("="*60)
    
    # Check health first
    if not test_health():
        print("\n❌ Backend not ready. Make sure it's running with ./start_backend.sh")
        return
    
    # Test configurations (days, cloud_coverage)
    configs = [
        (1, 50),   # 1 day, 50% clouds - ultra fast
        (3, 40),   # 3 days, 40% clouds - fast
        (7, 30),   # 7 days, 30% clouds - more data
    ]
    
    results = []
    for days, cloud_coverage in configs:
        success = test_with_days(days, cloud_coverage)
        results.append((days, cloud_coverage, success))
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    for days, cloud_coverage, success in results:
        status = "✅" if success else "❌"
        print(f"{status} {days} days, {cloud_coverage}% clouds")
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    successful = [r for r in results if r[2]]
    if successful:
        best = successful[0]
        print(f"✅ Use days={best[0]}, cloud_coverage={best[1]} for fastest results")
        print(f"   Run: curl 'http://localhost:8000/risk-map?days={best[0]}&cloud_coverage={best[1]}'")
    else:
        print("❌ All configurations failed. Check backend logs for errors.")
        print("   Try: tail -f backend.log")

if __name__ == "__main__":
    main()
