from fastapi import APIRouter
from datetime import datetime

router = APIRouter()

@router.get("/live")
async def liveness_check():
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/ready")
async def readiness_check():
    return {
        "status": "ready",
        "timestamp": datetime.utcnow().isoformat()
    }
