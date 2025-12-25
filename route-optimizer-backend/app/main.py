from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
from datetime import datetime
from app.config import settings
from app.routers import optimize, health, upload, history
from app.database.connection import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="RouteOptimizer API",
    description="AI-powered route optimization",
    version="1.0.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Error: {str(exc)}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

@app.on_event("startup")
def startup_event():
    """Initialize database on app startup"""
    try:
        init_db()
        logger.info("Application started")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}")

app.include_router(health.router, prefix="/api/health")
app.include_router(optimize.router, prefix="/api/optimize")
app.include_router(upload.router, prefix="/api/upload")
app.include_router(history.router)

@app.get("/")
async def root():
    return {
        "message": "RouteOptimizer API",
        "version": "1.0.0",
        "docs": "/api/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host=settings.HOST, port=settings.PORT, reload=settings.DEBUG)
