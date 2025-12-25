import pytest
from app.models.address import AddressInput, AddressWithCoordinates
from app.models.route import Route, RouteStop, OptimizationMetrics
from app.models.optimization_result import OptimizationRequest, OptimizationResponse
from datetime import datetime

class TestAddressInput:
    """Test AddressInput validation"""
    
    def test_valid_address(self):
        addr = AddressInput(
            id=1,
            name="Office",
            street="123 Main Street",
            city="Delhi",
            postal_code="110001"
        )
        assert addr.id == 1
        assert addr.name == "Office"
    
    def test_coordinate_validation(self):
        """Coordinates must be in valid ranges"""
        with pytest.raises(ValueError):
            AddressInput(
                id=1, name="T", street="S", city="C",
                latitude=95  # Invalid
            )
        
        with pytest.raises(ValueError):
            AddressInput(
                id=1, name="T", street="S", city="C",
                longitude=190  # Invalid
            )
    
    def test_empty_street_rejected(self):
        """Empty/whitespace streets rejected"""
        with pytest.raises(ValueError):
            AddressInput(
                id=1, name="T", street="   ", city="Delhi"
            )
    
    def test_min_length_enforced(self):
        """Min length for name enforced"""
        with pytest.raises(ValueError):
            AddressInput(
                id=1, name="", street="S", city="C"
            )

class TestAddressWithCoordinates:
    """Test AddressWithCoordinates"""
    
    def test_coords_required(self):
        """Latitude and longitude required"""
        with pytest.raises(ValueError):
            AddressWithCoordinates(
                id=1, name="T", street="S", city="C"
            )
    
    def test_valid_coords(self):
        addr = AddressWithCoordinates(
            id=1, name="Test", street="Main", city="Delhi",
            latitude=28.6139, longitude=77.2090
        )
        assert addr.latitude == 28.6139
        assert addr.longitude == 77.2090

class TestOptimizationRequest:
    """Test OptimizationRequest"""
    
    def test_min_addresses(self):
        """At least 2 addresses required"""
        with pytest.raises(ValueError):
            OptimizationRequest(
                addresses=[
                    AddressInput(id=1, name="A", street="S", city="C")
                ]
            )
    
    def test_max_addresses(self):
        """Max 1000 addresses"""
        with pytest.raises(ValueError):
            OptimizationRequest(
                addresses=[
                    AddressInput(id=i, name=f"A{i}", street="S", city="C")
                    for i in range(1001)
                ]
            )
    
    def test_valid_request(self):
        req = OptimizationRequest(
            addresses=[
                AddressInput(id=1, name="A1", street="S1", city="C"),
                AddressInput(id=2, name="A2", street="S2", city="C")
            ]
        )
        assert len(req.addresses) == 2
        assert req.depot_name == "Office"
        assert req.optimize_for == "distance"

class TestRoute:
    """Test Route model"""
    
    def test_route_creation(self):
        stops = [
            RouteStop(
                sequence=1, address_id=1, address_name="A1",
                street="S1", city="C", latitude=28.6, longitude=77.2,
                distance_from_previous_km=0, time_from_previous_min=0,
                cumulative_distance_km=0, cumulative_time_min=0
            ),
            RouteStop(
                sequence=2, address_id=2, address_name="A2",
                street="S2", city="C", latitude=28.7, longitude=77.3,
                distance_from_previous_km=5, time_from_previous_min=10,
                cumulative_distance_km=5, cumulative_time_min=10
            )
        ]
        
        route = Route(
            route_id="R1",
            stops=stops,
            total_distance_km=5,
            total_time_min=10,
            total_cost_inr=100,
            computation_time_ms=50
        )
        
        assert route.route_id == "R1"
        assert len(route.stops) == 2
        assert route.total_distance_km == 5

class TestOptimizationMetrics:
    """Test OptimizationMetrics"""
    
    def test_valid_metrics(self):
        metrics = OptimizationMetrics(
            distance_saved_km=10,
            distance_saved_percent=15,
            cost_saved_inr=500,
            cost_saved_percent=20,
            time_saved_min=30
        )
        assert metrics.distance_saved_percent <= 100
        assert metrics.cost_saved_percent <= 100

class TestOptimizationResponse:
    """Test OptimizationResponse"""
    
    def test_response_with_route(self):
        stops = [
            RouteStop(
                sequence=1, address_id=1, address_name="A1",
                street="S1", city="C", latitude=28.6, longitude=77.2,
                distance_from_previous_km=0, time_from_previous_min=0,
                cumulative_distance_km=0, cumulative_time_min=0
            ),
            RouteStop(
                sequence=2, address_id=2, address_name="A2",
                street="S2", city="C", latitude=28.7, longitude=77.3,
                distance_from_previous_km=5, time_from_previous_min=10,
                cumulative_distance_km=5, cumulative_time_min=10
            )
        ]
        
        route = Route(
            route_id="R1",
            stops=stops,
            total_distance_km=5,
            total_time_min=10,
            total_cost_inr=100,
            computation_time_ms=50
        )
        
        response = OptimizationResponse(
            request_id="REQ1",
            status="success",
            route=route,
            computation_time_ms=50
        )
        
        assert response.status == "success"
        assert response.route is not None
        assert response.error_message is None

    def test_response_with_error(self):
        response = OptimizationResponse(
            request_id="REQ1",
            status="error",
            error_message="Invalid input",
            computation_time_ms=10
        )
        
        assert response.status == "error"
        assert response.route is None
        assert response.error_message == "Invalid input"
