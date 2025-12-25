import json
import redis
from app.config import settings
from typing import Optional, List
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """Redis-based caching service for geocoding and routes"""
    
    GEOCODE_PREFIX = "geocode:"
    ROUTE_PREFIX = "route:"
    
    def __init__(self):
        """Initialize Redis connection"""
        self.redis_available = False
        try:
            self.redis_client = redis.from_url(
                settings.REDIS_URL,
                decode_responses=True,
                socket_connect_timeout=5
            )
            # Test connection
            self.redis_client.ping()
            self.redis_available = True
            logger.info("Redis cache initialized successfully")
        except Exception as e:
            logger.warning(f"Redis cache unavailable: {str(e)}. Continuing without cache.")
            self.redis_client = None
            self.redis_available = False
    
    def get_geocoded(self, address: str) -> Optional[dict]:
        """
        Get cached geocoding result for an address
        
        Args:
            address: Full address string (street, city, postal_code)
        
        Returns:
            dict with latitude/longitude or None if not cached/unavailable
        """
        if not self.redis_available:
            return None
        
        try:
            key = f"{self.GEOCODE_PREFIX}{address}"
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Error retrieving from cache: {str(e)}")
        
        return None
    
    def set_geocoded(self, address: str, latitude: float, longitude: float, ttl: Optional[int] = None):
        """
        Cache geocoding result for an address
        
        Args:
            address: Full address string
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            ttl: Time to live in seconds (default: CACHE_TTL from settings)
        """
        if not self.redis_available:
            return
        
        try:
            key = f"{self.GEOCODE_PREFIX}{address}"
            value = json.dumps({"latitude": latitude, "longitude": longitude})
            ttl = ttl or settings.CACHE_TTL
            self.redis_client.setex(key, ttl, value)
        except Exception as e:
            logger.warning(f"Error setting cache: {str(e)}")
    
    def get_route(self, route_key: str) -> Optional[dict]:
        """
        Get cached route optimization result
        
        Args:
            route_key: Cache key for the route (e.g., hash of addresses)
        
        Returns:
            dict with route data or None if not cached/unavailable
        """
        if not self.redis_available:
            return None
        
        try:
            key = f"{self.ROUTE_PREFIX}{route_key}"
            cached = self.redis_client.get(key)
            if cached:
                return json.loads(cached)
        except Exception as e:
            logger.warning(f"Error retrieving route from cache: {str(e)}")
        
        return None
    
    def set_route(self, route_key: str, route_data: dict, ttl: Optional[int] = None):
        """
        Cache route optimization result
        
        Args:
            route_key: Cache key for the route
            route_data: Route data dict to cache
            ttl: Time to live in seconds (default: CACHE_TTL from settings)
        """
        if not self.redis_available:
            return
        
        try:
            key = f"{self.ROUTE_PREFIX}{route_key}"
            value = json.dumps(route_data)
            ttl = ttl or settings.CACHE_TTL
            self.redis_client.setex(key, ttl, value)
        except Exception as e:
            logger.warning(f"Error setting route cache: {str(e)}")
    
    def invalidate_user_routes(self, user_id: int):
        """
        Invalidate all cached routes for a user (e.g., after adding new address)
        
        Args:
            user_id: User ID whose routes to invalidate
        """
        if not self.redis_available:
            return
        
        try:
            pattern = f"{self.ROUTE_PREFIX}user:{user_id}:*"
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
        except Exception as e:
            logger.warning(f"Error invalidating user routes: {str(e)}")
    
    def is_available(self) -> bool:
        """Check if Redis cache is available"""
        return self.redis_available

# Global cache service instance
cache_service = CacheService()
