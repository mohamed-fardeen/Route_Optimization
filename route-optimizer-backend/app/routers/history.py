from fastapi import APIRouter, Query, HTTPException, Depends, status
from sqlalchemy.orm import Session
from app.database.connection import get_db
from app.database.crud import CRUDUser, CRUDRoute, CRUDOptimization
from typing import Optional
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/history", tags=["History"])

@router.get("/routes")
async def get_user_routes(
    api_key: str = Query(..., description="API key for authentication"),
    limit: int = Query(100, ge=1, le=1000, description="Number of routes to return"),
    db: Session = Depends(get_db)
):
    """
    Get user's optimization history
    
    Requires API key authentication via query parameter
    """
    # Authenticate user
    user = CRUDUser.get_by_api_key(db, api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Get user's routes
    routes = CRUDRoute.get_user_routes(db, user.id, limit=limit)
    
    # Format response
    route_list = [
        {
            "route_id": route.route_id,
            "optimization_date": route.optimization_date.isoformat(),
            "total_distance_km": route.total_distance_km,
            "total_cost_inr": route.total_cost_inr,
            "cost_saved_inr": route.cost_saved_inr
        }
        for route in routes
    ]
    
    return {
        "status": "success",
        "total_routes": len(route_list),
        "routes": route_list
    }

@router.get("/analytics")
async def get_user_analytics(
    api_key: str = Query(..., description="API key for authentication"),
    db: Session = Depends(get_db)
):
    """
    Get user's analytics dashboard data
    
    Returns total routes, cost saved, distance, monthly stats
    Requires API key authentication via query parameter
    """
    # Authenticate user
    user = CRUDUser.get_by_api_key(db, api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Get user statistics
    stats = CRUDRoute.get_user_stats(db, user.id)
    
    return {
        "status": "success",
        "user": {
            "business_name": user.business_name,
            "subscription_plan": user.subscription_plan
        },
        "analytics": stats
    }

@router.delete("/routes/{route_id}")
async def delete_route(
    route_id: str,
    api_key: str = Query(..., description="API key for authentication"),
    db: Session = Depends(get_db)
):
    """
    Delete a route from history
    
    Requires API key authentication and route ownership
    """
    # Authenticate user
    user = CRUDUser.get_by_api_key(db, api_key)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    # Delete route (with ownership check)
    success = CRUDRoute.delete(db, route_id, user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Route not found or unauthorized"
        )
    
    return {
        "status": "success",
        "message": f"Route {route_id} deleted successfully"
    }
