import pytest
from unittest.mock import patch, MagicMock
from app.services.geocoder import GeocoderService
from app.models.address import AddressInput

@pytest.fixture
def service():
    return GeocoderService()

def test_address_with_coords(service):
    """Existing coords preserved"""
    addr = AddressInput(
        id=1, name="Test", street="123 Main",
        city="Delhi", latitude=28.6139, longitude=77.2090
    )
    result = service.geocode_address(addr)
    assert result.latitude == 28.6139

def test_caching(service):
    """Results cached"""
    addr = AddressInput(id=1, name="T", street="123", city="Delhi")
    with patch.object(service.geolocator, 'geocode') as m:
        m.return_value = MagicMock(latitude=28.6, longitude=77.2)
        r1 = service.geocode_address(addr)
        r2 = service.geocode_address(addr)
        assert m.call_count == 1

def test_geocode_multiple_addresses(service):
    """Geocode multiple addresses"""
    addresses = [
        AddressInput(id=1, name="A1", street="123", city="Delhi"),
        AddressInput(id=2, name="A2", street="456", city="Mumbai")
    ]
    
    with patch.object(service.geolocator, 'geocode') as m:
        m.return_value = MagicMock(latitude=28.6, longitude=77.2)
        geocoded, failed = service.geocode_addresses(addresses)
        assert len(geocoded) == 2
        assert len(failed) == 0

def test_geocode_failure_handling(service):
    """Handle geocoding failures gracefully"""
    addr = AddressInput(id=1, name="T", street="Invalid", city="City")
    
    with patch.object(service.geolocator, 'geocode') as m:
        m.return_value = None
        result = service.geocode_address(addr)
        assert result is None

def test_geocode_exception_handling(service):
    """Handle exceptions during geocoding"""
    addr = AddressInput(id=1, name="T", street="123", city="Delhi")
    
    with patch.object(service.geolocator, 'geocode') as m:
        m.side_effect = Exception("Connection error")
        result = service.geocode_address(addr)
        assert result is None

def test_rate_limiting(service):
    """Rate limiting with time.sleep"""
    addr = AddressInput(id=1, name="T", street="123", city="Delhi")
    
    with patch('app.services.geocoder.time.sleep') as mock_sleep:
        with patch.object(service.geolocator, 'geocode') as m:
            m.return_value = MagicMock(latitude=28.6, longitude=77.2)
            service.geocode_address(addr)
            mock_sleep.assert_called_once_with(1)

def test_address_with_postal_code(service):
    """Postal code included in query"""
    addr = AddressInput(
        id=1, name="T", street="123", city="Delhi",
        postal_code="110001"
    )
    
    with patch.object(service.geolocator, 'geocode') as m:
        m.return_value = MagicMock(latitude=28.6, longitude=77.2)
        service.geocode_address(addr)
        # Verify postal code was included in address string
        call_args = m.call_args[0][0]
        assert "110001" in call_args
