from pydantic import BaseModel, Field
from typing import List
from datetime import datetime

class RouteStop(BaseModel):
    """Single stop in route"""
    sequence: int = Field(...)
    address_id: int
    address_name: str
    street: str
    city: str
    latitude: float
    longitude: float
    distance_from_previous_km: float = Field(..., ge=0)
    time_from_previous_min: float = Field(..., ge=0)
    cumulative_distance_km: float = Field(..., ge=0)
    cumulative_time_min: float = Field(..., ge=0)

class Route(BaseModel):
    """Complete optimized route"""
    route_id: str
    stops: List[RouteStop] = Field(..., min_items=2)
    total_distance_km: float = Field(..., ge=0)
    total_time_min: float = Field(..., ge=0)
    total_cost_inr: float = Field(..., ge=0)
    optimization_algorithm: str = "or-tools"
    computation_time_ms: int = Field(..., ge=0)
    created_at: datetime = Field(default_factory=datetime.utcnow)

class OptimizationMetrics(BaseModel):
    """Optimization quality metrics"""
    distance_saved_km: float = Field(..., ge=0)
    distance_saved_percent: float = Field(..., ge=0, le=100)
    cost_saved_inr: float = Field(..., ge=0)
    cost_saved_percent: float = Field(..., ge=0, le=100)
    time_saved_min: float = Field(..., ge=0)
