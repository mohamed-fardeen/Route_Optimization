import pytest
import json
from unittest.mock import MagicMock, patch
from app.services.cache_service import CacheService

class TestCacheService:
    """Test cache service functionality"""
    
    @patch('redis.from_url')
    def test_cache_service_initialization(self, mock_redis):
        """Test cache service initialization"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        
        cache = CacheService()
        
        assert cache.redis_available is True
        mock_redis.assert_called_once()
    
    @patch('redis.from_url')
    def test_cache_service_initialization_failure(self, mock_redis):
        """Test cache service initialization when Redis unavailable"""
        mock_redis.side_effect = Exception("Connection failed")
        
        cache = CacheService()
        
        assert cache.redis_available is False
        assert cache.redis_client is None
    
    @patch('redis.from_url')
    def test_get_geocoded_hit(self, mock_redis):
        """Test getting cached geocoding result"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        
        cached_data = {"latitude": 28.6139, "longitude": 77.2090}
        mock_client.get.return_value = json.dumps(cached_data)
        
        cache = CacheService()
        result = cache.get_geocoded("Delhi, India")
        
        assert result is not None
        assert result["latitude"] == 28.6139
        assert result["longitude"] == 77.2090
    
    @patch('redis.from_url')
    def test_get_geocoded_miss(self, mock_redis):
        """Test cache miss for geocoding"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.get.return_value = None
        
        cache = CacheService()
        result = cache.get_geocoded("Unknown, Place")
        
        assert result is None
    
    @patch('redis.from_url')
    def test_set_geocoded(self, mock_redis):
        """Test setting cached geocoding result"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        
        cache = CacheService()
        cache.set_geocoded("Delhi, India", 28.6139, 77.2090)
        
        mock_client.setex.assert_called_once()
        args = mock_client.setex.call_args
        assert "geocode:Delhi, India" in str(args)
    
    @patch('redis.from_url')
    def test_get_route_hit(self, mock_redis):
        """Test getting cached route result"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        
        route_data = {"stops": 5, "total_distance_km": 50}
        mock_client.get.return_value = json.dumps(route_data)
        
        cache = CacheService()
        result = cache.get_route("route_key_123")
        
        assert result is not None
        assert result["total_distance_km"] == 50
    
    @patch('redis.from_url')
    def test_set_route(self, mock_redis):
        """Test setting cached route result"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        
        cache = CacheService()
        route_data = {"stops": 3, "total_distance_km": 30}
        cache.set_route("route_key_456", route_data)
        
        mock_client.setex.assert_called_once()
        args = mock_client.setex.call_args
        assert "route:route_key_456" in str(args)
    
    @patch('redis.from_url')
    def test_is_available_true(self, mock_redis):
        """Test checking if cache is available"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        
        cache = CacheService()
        assert cache.is_available() is True
    
    @patch('redis.from_url')
    def test_is_available_false(self, mock_redis):
        """Test checking if cache is unavailable"""
        mock_redis.side_effect = Exception("Connection failed")
        
        cache = CacheService()
        assert cache.is_available() is False
    
    @patch('redis.from_url')
    def test_cache_graceful_failure_get(self, mock_redis):
        """Test cache gracefully handles errors on get"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.get.side_effect = Exception("Redis error")
        
        cache = CacheService()
        result = cache.get_geocoded("Delhi, India")
        
        # Should return None instead of raising exception
        assert result is None
    
    @patch('redis.from_url')
    def test_cache_graceful_failure_set(self, mock_redis):
        """Test cache gracefully handles errors on set"""
        mock_client = MagicMock()
        mock_redis.return_value = mock_client
        mock_client.ping.return_value = True
        mock_client.setex.side_effect = Exception("Redis error")
        
        cache = CacheService()
        # Should not raise exception
        cache.set_geocoded("Delhi, India", 28.6139, 77.2090)

class TestCacheServiceWhenRedisUnavailable:
    """Test cache service behavior when Redis is unavailable"""
    
    @patch('redis.from_url')
    def test_get_geocoded_redis_unavailable(self, mock_redis):
        """Test get returns None when Redis unavailable"""
        mock_redis.side_effect = Exception("Connection failed")
        
        cache = CacheService()
        result = cache.get_geocoded("Delhi, India")
        
        assert result is None
    
    @patch('redis.from_url')
    def test_set_geocoded_redis_unavailable(self, mock_redis):
        """Test set does nothing when Redis unavailable"""
        mock_redis.side_effect = Exception("Connection failed")
        
        cache = CacheService()
        # Should not raise exception
        cache.set_geocoded("Delhi, India", 28.6139, 77.2090)
    
    @patch('redis.from_url')
    def test_get_route_redis_unavailable(self, mock_redis):
        """Test get_route returns None when Redis unavailable"""
        mock_redis.side_effect = Exception("Connection failed")
        
        cache = CacheService()
        result = cache.get_route("route_key")
        
        assert result is None
    
    @patch('redis.from_url')
    def test_set_route_redis_unavailable(self, mock_redis):
        """Test set_route does nothing when Redis unavailable"""
        mock_redis.side_effect = Exception("Connection failed")
        
        cache = CacheService()
        # Should not raise exception
        cache.set_route("route_key", {"stops": 5})
