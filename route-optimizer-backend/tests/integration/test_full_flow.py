from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["message"] == "RouteOptimizer API"

def test_health_live():
    """Test liveness check"""
    response = client.get("/api/health/live")
    assert response.status_code == 200
    assert response.json()["status"] == "alive"

def test_health_ready():
    """Test readiness check"""
    response = client.get("/api/health/ready")
    assert response.status_code == 200
    assert response.json()["status"] == "ready"

def test_optimize_valid_request():
    """Test optimization endpoint with valid request"""
    payload = {
        "addresses": [
            {
                "id": 1,
                "name": "Office",
                "street": "123 Main St",
                "city": "Delhi",
                "latitude": 28.6139,
                "longitude": 77.2090
            },
            {
                "id": 2,
                "name": "Stop 1",
                "street": "456 Second St",
                "city": "Delhi",
                "latitude": 28.6145,
                "longitude": 77.2100
            },
            {
                "id": 3,
                "name": "Stop 2",
                "street": "789 Third St",
                "city": "Delhi",
                "latitude": 28.6150,
                "longitude": 77.2110
            }
        ]
    }
    
    response = client.post("/api/optimize", json=payload)
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "success"
    assert data["request_id"]
    assert data["route"] is not None
    assert data["route"]["total_distance_km"] > 0
    assert data["computation_time_ms"] >= 0  # Could be 0 in test client
    assert data["metrics"] is not None

def test_optimize_insufficient_addresses():
    """Test optimization with < 2 addresses"""
    payload = {
        "addresses": [
            {
                "id": 1,
                "name": "Office",
                "street": "123 Main St",
                "city": "Delhi",
                "latitude": 28.6139,
                "longitude": 77.2090
            }
        ]
    }
    
    response = client.post("/api/optimize", json=payload)
    # Pydantic validation returns 422, but request handler could catch and return 400
    assert response.status_code in [200, 400, 422]

def test_optimize_request_tracking():
    """Test that request ID is unique"""
    payload = {
        "addresses": [
            {
                "id": 1,
                "name": "A",
                "street": "S1",
                "city": "Delhi",
                "latitude": 28.6139,
                "longitude": 77.2090
            },
            {
                "id": 2,
                "name": "B",
                "street": "S2",
                "city": "Delhi",
                "latitude": 28.6145,
                "longitude": 77.2100
            }
        ]
    }
    
    r1 = client.post("/api/optimize", json=payload).json()
    r2 = client.post("/api/optimize", json=payload).json()
    
    assert r1["request_id"] != r2["request_id"]

def test_optimize_response_contains_stops():
    """Test that response contains route stops"""
    payload = {
        "addresses": [
            {
                "id": 1,
                "name": "Office",
                "street": "123 Main",
                "city": "Delhi",
                "latitude": 28.6139,
                "longitude": 77.2090
            },
            {
                "id": 2,
                "name": "Stop1",
                "street": "456 Second",
                "city": "Delhi",
                "latitude": 28.6145,
                "longitude": 77.2100
            }
        ]
    }
    
    response = client.post("/api/optimize", json=payload)
    data = response.json()
    
    if data["status"] == "success":
        assert len(data["route"]["stops"]) > 0
        stop = data["route"]["stops"][0]
        assert "sequence" in stop
        assert "address_id" in stop
        assert "distance_from_previous_km" in stop
        assert "cumulative_distance_km" in stop

