from pydantic import BaseModel, Field, field_validator
from typing import Optional

class AddressInput(BaseModel):
    """Input address from client"""
    id: int = Field(..., description="Unique address ID")
    name: str = Field(..., min_length=1, max_length=255)
    street: str = Field(..., min_length=1, max_length=255)
    city: str = Field(..., min_length=1, max_length=100)
    postal_code: Optional[str] = Field(None, max_length=20)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    phone: Optional[str] = Field(None, max_length=20)
    
    @field_validator('street', 'city', mode='before')
    @classmethod
    def validate_not_empty(cls, v):
        if isinstance(v, str):
            v = v.strip()
            if not v:
                raise ValueError('Cannot be empty')
        return v

class AddressWithCoordinates(AddressInput):
    """Address with geocoded coordinates"""
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    geocoding_confidence: float = Field(default=0.95)
    geocoding_provider: str = "nominatim"
