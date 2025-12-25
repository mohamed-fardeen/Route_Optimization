from math import radians, sin, cos, sqrt, atan2
from typing import List, Tuple
import logging

logger = logging.getLogger(__name__)

class DistanceCalculator:
    """Calculate distances between coordinates"""
    
    EARTH_RADIUS_KM = 6371.0
    COST_PER_KM_INR = 12  # ₹12 per km
    AVG_SPEED_KMH = 30   # km/h average
    
    @staticmethod
    def haversine_distance(
        lat1: float, lon1: float,
        lat2: float, lon2: float
    ) -> float:
        """Calculate great-circle distance using Haversine"""
        try:
            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            
            dlat = lat2 - lat1
            dlon = lon2 - lon1
            
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))
            
            return max(0, DistanceCalculator.EARTH_RADIUS_KM * c)
        except (TypeError, ValueError) as e:
            logger.error(f"Distance calc error: {str(e)}")
            return 0.0
    
    @staticmethod
    def calculate_route_distance(
        coordinates: List[Tuple[float, float]]
    ) -> float:
        """Calculate total distance for a route"""
        if len(coordinates) < 2:
            return 0.0
        
        total = 0.0
        for i in range(len(coordinates) - 1):
            lat1, lon1 = coordinates[i]
            lat2, lon2 = coordinates[i + 1]
            dist = DistanceCalculator.haversine_distance(
                lat1, lon1, lat2, lon2
            )
            total += dist
        
        return round(total, 2)
    
    @staticmethod
    def distance_to_cost(distance_km: float) -> float:
        """Distance to cost in INR"""
        return round(distance_km * DistanceCalculator.COST_PER_KM_INR, 2)
    
    @staticmethod
    def distance_to_time(distance_km: float, speed_kmh: float = None) -> float:
        """Distance to time in minutes"""
        if speed_kmh is None:
            speed_kmh = DistanceCalculator.AVG_SPEED_KMH
        if speed_kmh <= 0:
            return 0.0
        return round((distance_km / speed_kmh) * 60, 1)

distance_calculator = DistanceCalculator()
