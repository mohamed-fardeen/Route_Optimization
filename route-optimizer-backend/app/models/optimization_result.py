from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from app.models.address import AddressInput
from app.models.route import Route, OptimizationMetrics

class OptimizationRequest(BaseModel):
    """Optimization request"""
    addresses: List[AddressInput] = Field(
        ..., min_items=2, max_items=1000
    )
    depot_name: str = Field(default="Office")
    optimize_for: str = Field(default="distance")

class OptimizationResponse(BaseModel):
    """Optimization response"""
    request_id: str
    status: str
    route: Optional[Route] = None
    metrics: Optional[OptimizationMetrics] = None
    error_message: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    computation_time_ms: int
