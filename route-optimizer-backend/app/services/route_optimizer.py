from app.models.address import AddressWithCoordinates
from app.services.distance_calculator import DistanceCalculator
from typing import List, Tuple
import logging
import time
from itertools import permutations

logger = logging.getLogger(__name__)

class RouteOptimizer:
    """Optimize routes using nearest neighbor algorithm with OR-Tools fallback"""
    
    def __init__(self, timeout_seconds: int = 30):
        self.timeout_seconds = timeout_seconds
        self.distance_calc = DistanceCalculator()
        self._ortools_available = self._check_ortools()
    
    def _check_ortools(self) -> bool:
        """Check if OR-Tools routing is available"""
        try:
            from ortools.routing import routing_enums_pb2, routing_index_manager, routing_model
            return True
        except ImportError:
            logger.warning("OR-Tools routing not available, using nearest neighbor algorithm")
            return False
    
    def _nearest_neighbor_route(
        self, addresses: List[AddressWithCoordinates], depot_index: int = 0
    ) -> List[int]:
        """Simple nearest neighbor algorithm for route optimization"""
        n = len(addresses)
        unvisited = set(range(n))
        route = [depot_index]
        current = depot_index
        unvisited.remove(depot_index)
        
        coords = [(a.latitude, a.longitude) for a in addresses]
        
        while unvisited:
            # Find nearest unvisited
            nearest = min(
                unvisited,
                key=lambda x: self.distance_calc.haversine_distance(
                    coords[current][0], coords[current][1],
                    coords[x][0], coords[x][1]
                )
            )
            route.append(nearest)
            current = nearest
            unvisited.remove(nearest)
        
        # Return to depot
        route.append(depot_index)
        return route
    
    def _ortools_route(
        self,
        addresses: List[AddressWithCoordinates],
        depot_index: int = 0
    ) -> List[int]:
        """Optimize using Google OR-Tools"""
        try:
            from ortools.routing import routing_enums_pb2, routing_index_manager, routing_model
        except ImportError:
            raise ImportError("OR-Tools routing not available")
        
        coords = [(a.latitude, a.longitude) for a in addresses]
        
        # Create manager
        manager = routing_index_manager.RoutingIndexManager(
            len(coords), 1, depot_index
        )
        
        # Create model
        routing = routing_model.RoutingModel(manager)
        
        # Distance callback
        def distance_callback(from_idx, to_idx):
            from_node = manager.IndexToNode(from_idx)
            to_node = manager.IndexToNode(to_idx)
            dist_km = self.distance_calc.haversine_distance(
                coords[from_node][0], coords[from_node][1],
                coords[to_node][0], coords[to_node][1]
            )
            return int(dist_km * 1000)  # meters
        
        callback_idx = routing.RegisterTransitCallback(distance_callback)
        routing.SetArcCostEvaluatorOfAllVehicles(callback_idx)
        
        # Search parameters
        params = routing.DefaultRoutingSearchParameters()
        params.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        params.time_limit.seconds = self.timeout_seconds
        
        # Solve
        assignment = routing.SolveFromAssignmentWithParameters(
            initial_routes=None, parameters=params
        )
        
        if not assignment:
            raise Exception("Optimization failed")
        
        # Extract route
        route = []
        idx = routing.Start(0)
        while not routing.IsEnd(idx):
            route.append(manager.IndexToNode(idx))
            idx = assignment.Value(routing.NextVar(idx))
        route.append(manager.IndexToNode(idx))
        
        return route
    
    def optimize(
        self,
        addresses: List[AddressWithCoordinates],
        depot_index: int = 0
    ) -> Tuple[List[int], float, int]:
        """Optimize route order
        
        Returns: (route, distance_km, computation_time_ms)
        """
        if len(addresses) < 2:
            raise ValueError("At least 2 addresses required")
        
        start = time.time()
        
        coords = [(a.latitude, a.longitude) for a in addresses]
        
        # Try OR-Tools first, fallback to nearest neighbor
        try:
            if self._ortools_available:
                route = self._ortools_route(addresses, depot_index)
            else:
                route = self._nearest_neighbor_route(addresses, depot_index)
        except Exception as e:
            logger.warning(f"Primary optimization failed, using nearest neighbor: {str(e)}")
            route = self._nearest_neighbor_route(addresses, depot_index)
        
        # Calculate distance
        total_dist = self.distance_calc.calculate_route_distance(
            [coords[i] for i in route]
        )
        
        time_ms = int((time.time() - start) * 1000)
        
        logger.info(f"Route optimized in {time_ms}ms, distance={total_dist:.2f}km")
        
        return route, total_dist, time_ms

route_optimizer = RouteOptimizer()
