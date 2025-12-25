#!/usr/bin/env python3
"""
Quick test script to verify the API is working
Run this after starting the server
"""

import requests
import json
from time import sleep

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoints"""
    print("\n✓ Testing Health Endpoints...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/health/live", timeout=5)
        assert response.status_code == 200
        print("  ✓ /api/health/live - OK")
        
        response = requests.get(f"{BASE_URL}/api/health/ready", timeout=5)
        assert response.status_code == 200
        print("  ✓ /api/health/ready - OK")
        
        return True
    except Exception as e:
        print(f"  ✗ Health check failed: {e}")
        return False

def test_optimize():
    """Test route optimization"""
    print("\n✓ Testing Route Optimization...")
    
    try:
        addresses = [
            {"street": "123 Main St", "city": "Delhi", "postal_code": "110001"},
            {"street": "456 Park Ave", "city": "Delhi", "postal_code": "110002"},
            {"street": "789 Market St", "city": "Delhi", "postal_code": "110003"},
            {"street": "321 Beach Rd", "city": "Delhi", "postal_code": "110004"},
        ]
        
        response = requests.post(
            f"{BASE_URL}/api/optimize",
            json={"addresses": addresses},
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["status"] == "success", "Optimization failed"
        assert "route" in data, "No route in response"
        assert "metrics" in data, "No metrics in response"
        assert "computation_time_ms" in data, "No timing info"
        
        stops = data["route"]["stops"]
        print(f"  ✓ Optimized {len(stops)} stops")
        print(f"  ✓ Total distance: {data['metrics']['total_distance_km']} km")
        print(f"  ✓ Cost saved: ₹{data['metrics']['cost_saved_inr']}")
        print(f"  ✓ Time saved: {data['metrics']['time_saved_minutes']} minutes")
        print(f"  ✓ Computation time: {data['computation_time_ms']} ms")
        
        return True
    except Exception as e:
        print(f"  ✗ Optimization failed: {e}")
        return False

def test_csv_upload():
    """Test CSV upload"""
    print("\n✓ Testing CSV Upload...")
    
    try:
        # Create test CSV
        csv_content = """id,name,street,city,postal_code
1,Store A,123 Main St,Delhi,110001
2,Store B,456 Park Ave,Delhi,110002
3,Store C,789 Market St,Delhi,110003"""
        
        files = {"file": ("test.csv", csv_content)}
        response = requests.post(
            f"{BASE_URL}/api/upload/csv",
            files=files,
            timeout=30
        )
        
        assert response.status_code == 200, f"Expected 200, got {response.status_code}"
        data = response.json()
        
        assert data["status"] == "success", "Upload failed"
        assert data["parsed_successfully"] == 3, "Not all rows parsed"
        
        print(f"  ✓ Uploaded CSV with {data['total_rows']} rows")
        print(f"  ✓ Successfully parsed: {data['parsed_successfully']}")
        print(f"  ✓ Addresses returned: {len(data['addresses'])}")
        
        return True
    except Exception as e:
        print(f"  ✗ CSV upload failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("RouteOptimizer API - Quick Test")
    print("=" * 60)
    
    # Check if server is running
    print("\nChecking if server is running...")
    for attempt in range(10):
        try:
            requests.get(f"{BASE_URL}/api/health/live", timeout=2)
            print(f"✓ Server is running at {BASE_URL}")
            break
        except:
            if attempt == 9:
                print("✗ Server not responding. Run: docker-compose up")
                return
            sleep(1)
    
    # Run tests
    results = []
    results.append(("Health Checks", test_health()))
    results.append(("Route Optimization", test_optimize()))
    results.append(("CSV Upload", test_csv_upload()))
    
    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    print(f"\n{passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 Everything is working! 🎉")
        print(f"\nAccess the API at: {BASE_URL}/api/docs")
    else:
        print("\n⚠️ Some tests failed. Check server logs.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
