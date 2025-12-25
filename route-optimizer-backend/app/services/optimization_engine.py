import time
import hashlib
import json
from typing import List, Tuple, Dict, Any, Optional
import numpy as np
import requests
from app.services.cache_service import cache_service
from app.services.distance_calculator import DistanceCalculator

class OptimizationEngine:
    def __init__(self, osrm_base: str = "https://router.project-osrm.org", request_timeout: int = 10):
        self.osrm_base = osrm_base.rstrip("/")
        self.request_timeout = request_timeout
        self.distance_calc = DistanceCalculator()
        self._ortools_available = self._check_ortools()

    def _check_ortools(self) -> bool:
        try:
            from ortools.constraint_solver import pywrapcp, routing_enums_pb2
            return True
        except Exception:
            return False

    def _coords_to_str(self, coords: List[Tuple[float, float]]) -> str:
        return ";".join([f"{c[1]},{c[0]}" for c in coords])

    def _hash_key(self, payload: Any) -> str:
        data = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(data.encode("utf-8")).hexdigest()

    def _osrm_table(self, coords: List[Tuple[float, float]]) -> Dict[str, List[List[float]]]:
        key = f"osrm:table:{self._hash_key({'coords': coords})}"
        cached = cache_service.get_route(key)
        if cached:
            return cached
        url = f"{self.osrm_base}/table/v1/driving/{self._coords_to_str(coords)}?annotations=distance,duration"
        r = requests.get(url, timeout=self.request_timeout)
        r.raise_for_status()
        data = r.json()
        result = {"distances": data.get("distances", []), "durations": data.get("durations", [])}
        cache_service.set_route(key, result, ttl=3600)
        return result

    def _osrm_route(self, ordered_coords: List[Tuple[float, float]]) -> Optional[Dict[str, Any]]:
        url = f"{self.osrm_base}/route/v1/driving/{self._coords_to_str(ordered_coords)}?overview=full&geometries=geojson"
        r = requests.get(url, timeout=self.request_timeout)
        if not r.ok:
            return None
        data = r.json()
        if data.get("code") != "Ok" or not data.get("routes"):
            return None
        route = data["routes"][0]
        return {
            "geometry": route.get("geometry"),
            "legs": route.get("legs", []),
            "distance": route.get("distance", 0.0),
            "duration": route.get("duration", 0.0),
        }

    def _guided_local_search_vrp(
        self,
        distances: List[List[float]],
        vehicles: int,
        depot_index: int,
        time_limit_seconds: int,
    ) -> List[List[int]]:
        from ortools.constraint_solver import pywrapcp, routing_enums_pb2
        n = len(distances)
        manager = pywrapcp.RoutingIndexManager(n, vehicles, depot_index)
        routing = pywrapcp.RoutingModel(manager)
        def transit_cb(from_index, to_index):
            i = manager.IndexToNode(from_index)
            j = manager.IndexToNode(to_index)
            return int(distances[i][j])
        transit_cb_idx = routing.RegisterTransitCallback(transit_cb)
        routing.SetArcCostEvaluatorOfAllVehicles(transit_cb_idx)
        search = pywrapcp.DefaultRoutingSearchParameters()
        search.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
        search.local_search_metaheuristic = routing_enums_pb2.LocalSearchMetaheuristic.GUIDED_LOCAL_SEARCH
        search.time_limit.seconds = max(1, time_limit_seconds)
        search.log_search = False
        search.use_multi_armed_bandit = True
        search.lns_time_limit.seconds = 1
        search.number_of_search_workers = 8
        assignment = routing.SolveWithParameters(search)
        if assignment is None:
            return []
        routes: List[List[int]] = []
        for v in range(vehicles):
            idx = routing.Start(v)
            route = []
            while not routing.IsEnd(idx):
                route.append(manager.IndexToNode(idx))
                idx = assignment.Value(routing.NextVar(idx))
            route.append(manager.IndexToNode(idx))
            routes.append(route)
        return routes

    def _grid_nearest_neighbor(
        self, coords: List[Tuple[float, float]], depot_index: int
    ) -> List[int]:
        n = len(coords)
        if n < 2:
            return list(range(n))
        lat = np.array([c[0] for c in coords])
        lng = np.array([c[1] for c in coords])
        min_lat, max_lat = float(lat.min()), float(lat.max())
        min_lng, max_lng = float(lng.min()), float(lng.max())
        g = max(1e-6, (max_lat - min_lat + max_lng - min_lng) / 50.0)
        buckets: Dict[Tuple[int, int], List[int]] = {}
        for i in range(n):
            bx = int((lat[i] - min_lat) / g)
            by = int((lng[i] - min_lng) / g)
            buckets.setdefault((bx, by), []).append(i)
        def neighbors(ix, iy):
            for dx in (-1, 0, 1):
                for dy in (-1, 0, 1):
                    yield (ix + dx, iy + dy)
        visited = set([depot_index])
        route = [depot_index]
        cur = depot_index
        while len(visited) < n:
            cx = int((lat[cur] - min_lat) / g)
            cy = int((lng[cur] - min_lng) / g)
            candidates = []
            for bx, by in neighbors(cx, cy):
                candidates.extend(buckets.get((bx, by), []))
            best = None
            best_d = float("inf")
            for j in candidates:
                if j in visited:
                    continue
                d = self.distance_calc.haversine_distance(lat[cur], lng[cur], lat[j], lng[j])
                if d < best_d:
                    best_d = d
                    best = j
            if best is None:
                for j in range(n):
                    if j in visited:
                        continue
                    d = self.distance_calc.haversine_distance(lat[cur], lng[cur], lat[j], lng[j])
                    if d < best_d:
                        best_d = d
                        best = j
            visited.add(best)
            route.append(best)
            cur = best
        route.append(depot_index)
        return route

    def _cluster_assign(
        self, coords: List[Tuple[float, float]], vehicles: int
    ) -> List[List[int]]:
        n = len(coords)
        vehicles = max(1, min(vehicles, n))
        centroids = np.array(coords)[np.linspace(0, n - 1, vehicles).astype(int)]
        points = np.array(coords)
        for _ in range(10):
            dists = np.linalg.norm(points[:, None, :] - centroids[None, :, :], axis=2)
            assign = dists.argmin(axis=1)
            for k in range(vehicles):
                cluster = points[assign == k]
                if len(cluster) > 0:
                    centroids[k] = cluster.mean(axis=0)
        result: List[List[int]] = [[] for _ in range(vehicles)]
        dists = np.linalg.norm(points[:, None, :] - centroids[None, :, :], axis=2)
        assign = dists.argmin(axis=1)
        for i in range(n):
            result[assign[i]].append(i)
        return result

    def optimize(
        self,
        addresses: List[Tuple[float, float]],
        vehicles: int = 1,
        depot_index: int = 0,
        time_limit_seconds: int = 2,
    ) -> Dict[str, Any]:
        start = time.time()
        coords = list(addresses)
        key = f"route:{self._hash_key({'coords': coords, 'vehicles': vehicles, 'depot': depot_index})}"
        cached = cache_service.get_route(key)
        if cached:
            cached["computation_time_ms"] = int((time.time() - start) * 1000)
            return cached
        table = self._osrm_table(coords)
        distances = table["distances"]
        if self._ortools_available:
            routes = self._guided_local_search_vrp(distances, vehicles, depot_index, time_limit_seconds)
            if not routes:
                clusters = self._cluster_assign(coords, vehicles)
                routes = []
                for cl in clusters:
                    if depot_index not in cl:
                        cl = [depot_index] + cl
                    sub_coords = [coords[i] for i in cl]
                    order = self._grid_nearest_neighbor(sub_coords, 0)
                    routes.append([cl[i] for i in order])
        else:
            clusters = self._cluster_assign(coords, vehicles)
            routes = []
            for cl in clusters:
                if depot_index not in cl:
                    cl = [depot_index] + cl
                sub_coords = [coords[i] for i in cl]
                order = self._grid_nearest_neighbor(sub_coords, 0)
                routes.append([cl[i] for i in order])
        total_m = 0.0
        for r in routes:
            for i in range(len(r) - 1):
                total_m += distances[r[i]][r[i + 1]]
        total_km = round((total_m / 1000.0), 2)
        polyline: List[List[Tuple[float, float]]]
        polyline = []
        for r in routes:
            ordered = [coords[i] for i in r]
            res = self._osrm_route(ordered)
            if res and res.get("geometry"):
                pts = res["geometry"]["coordinates"]
                polyline.append([(p[1], p[0]) for p in pts])
            else:
                polyline.append(ordered)
        result = {
            "routes": routes,
            "path": polyline,
            "total_distance_km": total_km,
            "total_cost_inr": self.distance_calc.distance_to_cost(total_km),
            "total_time_min": self.distance_calc.distance_to_time(total_km),
            "computation_time_ms": int((time.time() - start) * 1000),
        }
        cache_service.set_route(key, result, ttl=600)
        return result

optimization_engine = OptimizationEngine()
