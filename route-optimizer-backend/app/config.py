from pydantic_settings import BaseSettings
from typing import Optional, List

class Settings(BaseSettings):
    # App
    APP_NAME: str = "RouteOptimizer"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    ENVIRONMENT: str = "development"
    
    # Database
    DATABASE_URL: str = "postgresql://route_user:route_pass@localhost:5432/route_optimizer"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_POOL_RECYCLE: int = 3600  # Recycle connections after 1 hour
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600  # Cache TTL in seconds (1 hour)
    
    # APIs
    GOOGLE_MAPS_API_KEY: Optional[str] = None
    
    # Optimization
    ALGORITHM_TIMEOUT: int = 30
    MAX_ADDRESSES: int = 1000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
