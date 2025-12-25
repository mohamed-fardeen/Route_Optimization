from fastapi import APIRouter, File, UploadFile, HTTPException
import pandas as pd
from io import StringIO
import logging
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)
router = APIRouter()

# Simple geocoder for text uploads
geocoder = Nominatim(user_agent="route_optimizer")

@router.post("/csv")
async def upload_csv(file: UploadFile = File(...)):
    """Upload CSV or TXT with addresses"""
    try:
        content = await file.read()
        text = content.decode('utf-8')
        filename = (file.filename or '').lower()
        is_txt = filename.endswith('.txt') or filename.endswith('.text') or (file.content_type or '').startswith('text/')
        is_csv = filename.endswith('.csv')
        
        if is_txt:
            addresses = []
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            # Deterministic jitter around India center to avoid identical points, no external geocoding
            base_lat, base_lng = 20.5937, 78.9629
            for idx, address_line in enumerate(lines, 1):
                jitter_lat = ((idx * 0.002) % 0.05) - 0.025
                jitter_lng = ((idx * 0.003) % 0.05) - 0.025
                addr = {
                    'id': idx,
                    'name': f'Stop {idx}',
                    'street': address_line,
                    'city': 'India',
                    'postal_code': '',
                    'lat': round(base_lat + jitter_lat, 6),
                    'lng': round(base_lng + jitter_lng, 6),
                }
                addresses.append(addr)
            return {
                "filename": file.filename,
                "total_rows": len(lines),
                "parsed_successfully": len(addresses),
                "failed": 0,
                "addresses": addresses,
                "errors": []
            }
        
        if not is_csv:
            lines = [line.strip() for line in text.split('\n') if line.strip()]
            if lines:
                addresses = []
                errors = []
                for idx, address_line in enumerate(lines, 1):
                    try:
                        location = geocoder.geocode(address_line, timeout=5)
                        if location:
                            addr = {
                                'id': idx,
                                'name': f'Stop {idx}',
                                'street': address_line,
                                'city': 'India',
                                'postal_code': '',
                                'lat': location.latitude,
                                'lng': location.longitude,
                            }
                        else:
                            addr = {
                                'id': idx,
                                'name': f'Stop {idx}',
                                'street': address_line,
                                'city': 'India',
                                'postal_code': '',
                                'lat': 20.5937,
                                'lng': 78.9629,
                            }
                        addresses.append(addr)
                    except Exception as e:
                        errors.append(f"Line {idx}: {str(e)}")
                        addr = {
                            'id': idx,
                            'name': f'Stop {idx}',
                            'street': address_line,
                            'city': 'India',
                            'postal_code': '',
                            'lat': 20.5937,
                            'lng': 78.9629,
                        }
                        addresses.append(addr)
                return {
                    "filename": file.filename,
                    "total_rows": len(lines),
                    "parsed_successfully": len(addresses),
                    "failed": len(errors),
                    "addresses": addresses,
                    "errors": errors[:10]
                }
            raise HTTPException(status_code=400, detail="Unsupported file type or empty content")
        
        df = pd.read_csv(StringIO(text))
        
        required = ['id', 'name', 'street', 'city']
        missing = [c for c in required if c not in df.columns]
        if missing:
            raise HTTPException(
                status_code=400,
                detail=f"Missing columns: {missing}"
            )
        
        addresses = []
        errors = []
        
        for idx, row in df.iterrows():
            try:
                addr = {
                    'id': int(row['id']),
                    'name': str(row['name']),
                    'street': str(row['street']),
                    'city': str(row['city']),
                    'postal_code': row.get('postal_code', None),
                    'lat': float(row['latitude']) if 'latitude' in row else 20.5937,
                    'lng': float(row['longitude']) if 'longitude' in row else 78.9629,
                }
                addresses.append(addr)
            except Exception as e:
                errors.append(f"Row {idx + 2}: {str(e)}")
        
        return {
            "filename": file.filename,
            "total_rows": len(df),
            "parsed_successfully": len(addresses),
            "failed": len(errors),
            "addresses": addresses,
            "errors": errors[:10]  # First 10 errors
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
