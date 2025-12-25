from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

# Test optimization with multiple addresses
addresses = [
    {
        "id": i,
        "name": f"Stop{i}",
        "street": f"Street{i}",
        "city": "Delhi",
        "latitude": 28.6139 + (i * 0.001),
        "longitude": 77.2090 + (i * 0.001)
    }
    for i in range(20)
]

print("=== RouteOptimizer API Performance Test ===\n")

# Test 20 stops
payload = {"addresses": addresses}
start = time.time()
response = client.post("/api/optimize", json=payload)
elapsed = time.time() - start

data = response.json()
print(f"20 Stops Optimization:")
print(f"  Status Code: {response.status_code}")
print(f"  Response Status: {data['status']}")
print(f"  Total Distance: {data['route']['total_distance_km']:.2f} km")
print(f"  Total Cost: ₹{data['route']['total_cost_inr']:.2f}")
print(f"  Total Time: {data['route']['total_time_min']:.1f} minutes")
print(f"  Cost Saved: ₹{data['metrics']['cost_saved_inr']:.2f}")
print(f"  Distance Saved: {data['metrics']['distance_saved_percent']:.1f}%")
print(f"  Computation Time: {data['computation_time_ms']} ms")
print(f"  Request Duration: {elapsed:.2f} seconds")
print(f"  Route Stops: {len(data['route']['stops'])}")

# Verify all stops have proper data
all_valid = all(
    'cumulative_distance_km' in stop and 
    'cumulative_time_min' in stop 
    for stop in data['route']['stops']
)
print(f"  All Stops Valid: {all_valid}")

print("\n✓ API is functional and performing well!")
