import pytest
from math import isclose
from app.services.distance_calculator import DistanceCalculator

class TestHaversine:
    def test_same_point(self):
        dist = DistanceCalculator.haversine_distance(28.6, 77.2, 28.6, 77.2)
        assert isclose(dist, 0, abs_tol=0.01)
    
    def test_delhi_mumbai(self):
        # ~1148 km
        dist = DistanceCalculator.haversine_distance(
            28.6139, 77.2090,
            19.0760, 72.8777
        )
        assert 1100 < dist < 1200

class TestRoute:
    def test_empty_route(self):
        dist = DistanceCalculator.calculate_route_distance([])
        assert dist == 0.0
    
    def test_single_point(self):
        coords = [(28.6139, 77.2090)]
        dist = DistanceCalculator.calculate_route_distance(coords)
        assert dist == 0.0
    
    def test_multi_point(self):
        coords = [
            (28.6139, 77.2090),
            (28.6145, 77.2100),
            (28.6150, 77.2110),
        ]
        dist = DistanceCalculator.calculate_route_distance(coords)
        assert dist > 0

class TestCost:
    def test_cost_conversion(self):
        cost = DistanceCalculator.distance_to_cost(100)
        assert cost == 1200  # 100 * 12
    
    def test_zero_distance(self):
        cost = DistanceCalculator.distance_to_cost(0)
        assert cost == 0

class TestTime:
    def test_time_conversion(self):
        # 30 km at 30 km/h = 60 minutes
        time = DistanceCalculator.distance_to_time(30, speed_kmh=30)
        assert time == 60.0
    
    def test_time_default_speed(self):
        # Using default 30 km/h
        time = DistanceCalculator.distance_to_time(30)
        assert time == 60.0
    
    def test_invalid_speed(self):
        time = DistanceCalculator.distance_to_time(100, speed_kmh=0)
        assert time == 0.0
