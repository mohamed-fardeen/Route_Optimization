from fastapi import APIRouter, HTTPException
from app.models.optimization_result import OptimizationRequest, OptimizationResponse
from app.models.route import Route, RouteStop, OptimizationMetrics
from app.services.geocoder import geocoder
from app.services.route_optimizer import route_optimizer
from app.services.distance_calculator import DistanceCalculator
from datetime import datetime
import uuid
import logging

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("", response_model=OptimizationResponse)
async def optimize_route(request: OptimizationRequest):
    """Optimize delivery route - main endpoint"""
    request_id = str(uuid.uuid4())
    
    try:
        logger.info(f"[{request_id}] Request: {len(request.addresses)} addresses")
        
        # Validate
        if len(request.addresses) < 2:
            raise HTTPException(status_code=400, detail="Min 2 addresses")
        if len(request.addresses) > 1000:
            raise HTTPException(status_code=400, detail="Max 1000 addresses")
        
        # Geocode
        logger.info(f"[{request_id}] Geocoding...")
        geocoded, failed_idx = geocoder.geocode_addresses(request.addresses)
        
        if len(geocoded) < 2:
            raise HTTPException(status_code=400, detail="Failed geocoding")
        
        # Optimize
        logger.info(f"[{request_id}] Optimizing...")
        opt_route, total_dist, comp_time = route_optimizer.optimize(geocoded)
        
        # Build response
        coords = [(a.latitude, a.longitude) for a in geocoded]
        stops = []
        cum_dist, cum_time = 0, 0
        
        for idx, addr_idx in enumerate(opt_route[:-1]):
            next_idx = opt_route[idx + 1]
            addr = geocoded[addr_idx]
            
            dist = DistanceCalculator.haversine_distance(
                coords[addr_idx][0], coords[addr_idx][1],
                coords[next_idx][0], coords[next_idx][1]
            )
            time_min = dist / 30 * 60
            cum_dist += dist
            cum_time += time_min
            
            stops.append(RouteStop(
                sequence=idx,
                address_id=addr.id,
                address_name=addr.name,
                street=addr.street,
                city=addr.city,
                latitude=addr.latitude,
                longitude=addr.longitude,
                distance_from_previous_km=dist,
                time_from_previous_min=time_min,
                cumulative_distance_km=cum_dist,
                cumulative_time_min=cum_time
            ))
        
        # Worst case = 30% worse than optimal
        worst_case = total_dist * 1.3
        saved_km = worst_case - total_dist
        saved_cost = saved_km * 12
        
        metrics = OptimizationMetrics(
            distance_saved_km=max(0, saved_km),
            distance_saved_percent=max(0, (saved_km/worst_case*100)) if worst_case > 0 else 0,
            cost_saved_inr=max(0, saved_cost),
            cost_saved_percent=max(0, (saved_cost/(worst_case*12)*100)) if worst_case > 0 else 0,
            time_saved_min=max(0, saved_km/30*60)
        )
        
        route = Route(
            route_id=request_id,
            stops=stops,
            total_distance_km=total_dist,
            total_time_min=cum_time,
            total_cost_inr=total_dist * 12,
            computation_time_ms=comp_time
        )
        
        resp = OptimizationResponse(
            request_id=request_id,
            status="success",
            route=route,
            metrics=metrics,
            timestamp=datetime.utcnow(),
            computation_time_ms=comp_time
        )
        
        logger.info(f"[{request_id}] Success! Saved ₹{saved_cost:.0f}")
        return resp
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[{request_id}] Error: {str(e)}")
        return OptimizationResponse(
            request_id=request_id,
            status="error",
            error_message=str(e),
            timestamp=datetime.utcnow(),
            computation_time_ms=0
        )
