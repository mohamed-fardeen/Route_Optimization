from geopy.geocoders import Nominatim
from app.models.address import AddressInput, AddressWithCoordinates
from typing import List, Optional, Tuple
import logging
import time

logger = logging.getLogger(__name__)

class GeocoderService:
    """Service for geocoding addresses using Nominatim"""
    
    def __init__(self, user_agent="route_optimizer_1.0"):
        self.geolocator = Nominatim(user_agent=user_agent, timeout=10)
        self.cache = {}
    
    def geocode_address(self, addr: AddressInput) -> Optional[AddressWithCoordinates]:
        """Convert address to coordinates"""
        
        # Return if already has coordinates
        if addr.latitude and addr.longitude:
            return AddressWithCoordinates(**addr.model_dump())
        
        # Check cache
        key = f"{addr.street.lower()},{addr.city.lower()}"
        if key in self.cache:
            lat, lng = self.cache[key]
            data = addr.model_dump(exclude={"latitude", "longitude"})
            return AddressWithCoordinates(
                latitude=lat, longitude=lng, **data
            )
        
        try:
            time.sleep(1)  # Nominatim rate limit
            full_addr = f"{addr.street}, {addr.city}"
            if addr.postal_code:
                full_addr += f", {addr.postal_code}"
            
            loc = self.geolocator.geocode(full_addr)
            if not loc:
                logger.warning(f"No geocode: {key}")
                return None
            
            self.cache[key] = (loc.latitude, loc.longitude)
            logger.info(f"Geocoded: {key}")
            
            data = addr.model_dump(exclude={"latitude", "longitude"})
            return AddressWithCoordinates(
                latitude=loc.latitude,
                longitude=loc.longitude,
                **data
            )
        except Exception as e:
            logger.error(f"Geocode error: {str(e)}")
            return None
    
    def geocode_addresses(
        self, addresses: List[AddressInput]
    ) -> Tuple[List[AddressWithCoordinates], List[int]]:
        """Geocode multiple addresses"""
        geocoded, failed = [], []
        for idx, addr in enumerate(addresses):
            res = self.geocode_address(addr)
            if res:
                geocoded.append(res)
            else:
                failed.append(idx)
        return geocoded, failed

geocoder = GeocoderService()
