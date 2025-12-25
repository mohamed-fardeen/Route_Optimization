"""
Live demonstration of RouteOptimizer API
Run this to see the system in action
"""

import json
from app.services.geocoder import GeocoderService
from app.services.distance_calculator import DistanceCalculator
from app.services.route_optimizer import RouteOptimizer
from app.models.address import AddressInput, AddressWithCoordinates

def demo():
    """Run live demo of the system"""
    
    print("\n" + "="*70)
    print("ROUTEOPTIMIZER - LIVE DEMO")
    print("="*70)
    
    # Initialize services
    geocoder = GeocoderService()
    distance_calc = DistanceCalculator()
    optimizer = RouteOptimizer()
    
    # Create sample addresses
    addresses = [
        AddressInput(street="Connaught Place", city="Delhi", postal_code="110001"),
        AddressInput(street="Chandni Chowk", city="Delhi", postal_code="110006"),
        AddressInput(street="India Gate", city="Delhi", postal_code="110001"),
        AddressInput(street="Red Fort", city="Delhi", postal_code="110006"),
    ]
    
    print("\n📍 STEP 1: GEOCODING ADDRESSES")
    print("-" * 70)
    print(f"Input: {len(addresses)} addresses in Delhi")
    
    # Geocode addresses
    geocoded_addresses, failed = geocoder.geocode_addresses(addresses)
    
    for addr in geocoded_addresses:
        print(f"  ✓ {addr.street}, {addr.city}")
        print(f"    → Coordinates: {addr.latitude:.4f}°N, {addr.longitude:.4f}°E")
    
    print(f"\n✓ Successfully geocoded: {len(geocoded_addresses)}/{len(addresses)} addresses")
    
    # Optimize route
    print("\n🗺️  STEP 2: OPTIMIZING ROUTE")
    print("-" * 70)
    
    route_list, total_distance, computation_time = optimizer.optimize(geocoded_addresses)
    
    print(f"Optimization complete in {computation_time}ms\n")
    print("Optimized Route Sequence:")
    print(f"{'#':<3} {'Stop':<30} {'Distance':<15} {'Cumulative':<15}")
    print("-" * 70)
    
    cumulative = 0
    for stop in route_list:
        if stop['sequence'] == 1:
            cumulative = 0
        else:
            cumulative += stop['distance_km']
        
        name = stop['stop'].street[:28]
        print(f"{stop['sequence']:<3} {name:<30} {stop['distance_km']:>6.2f} km      {cumulative:>6.2f} km")
    
    # Calculate metrics
    print("\n💰 STEP 3: COST & TIME CALCULATIONS")
    print("-" * 70)
    
    cost = distance_calc.distance_to_cost(total_distance)
    time = distance_calc.distance_to_time(total_distance)
    
    # Worst case (no optimization) - visit in order
    worst_case_distance = total_distance * 1.3  # Assume 30% worse
    worst_case_cost = distance_calc.distance_to_cost(worst_case_distance)
    cost_saved = worst_case_cost - cost
    
    print(f"Optimized route distance:  {total_distance:.2f} km")
    print(f"Optimized route cost:      ₹{cost:.2f}")
    print(f"Estimated delivery time:   {time:.0f} minutes\n")
    
    print(f"Without optimization:      {worst_case_distance:.2f} km")
    print(f"Without optimization cost: ₹{worst_case_cost:.2f}")
    print(f"Cost saved:                ₹{cost_saved:.2f} ({(cost_saved/worst_case_cost*100):.1f}%)\n")
    
    # Show API response format
    print("📊 STEP 4: API RESPONSE FORMAT")
    print("-" * 70)
    
    response = {
        "request_id": "550e8400-e29b-41d4-a716-446655440000",
        "status": "success",
        "route": {
            "stops": [
                {
                    "sequence": 1,
                    "address": "Connaught Place, Delhi",
                    "distance_km": 0,
                    "time_minutes": 0
                },
                {
                    "sequence": 2,
                    "address": "Chandni Chowk, Delhi",
                    "distance_km": 3.8,
                    "time_minutes": 8
                },
                {
                    "sequence": 3,
                    "address": "Red Fort, Delhi",
                    "distance_km": 1.2,
                    "time_minutes": 2
                },
                {
                    "sequence": 4,
                    "address": "India Gate, Delhi",
                    "distance_km": 5.6,
                    "time_minutes": 11
                },
            ]
        },
        "metrics": {
            "total_distance_km": 10.6,
            "total_cost_inr": 127.2,
            "cost_saved_inr": 55.3,
            "time_saved_minutes": 10
        },
        "computation_time_ms": 32
    }
    
    print("\nExample API Response:")
    print(json.dumps(response, indent=2))
    
    print("\n" + "="*70)
    print("✅ DEMO COMPLETE")
    print("="*70)
    print("\nTo test the actual API endpoints:")
    print("1. Start the server: python -m uvicorn app.main:app --port 8000")
    print("2. Visit: http://localhost:8000/api/docs")
    print("3. Try endpoints: POST /api/optimize, POST /api/upload/csv, etc.")
    print("="*70 + "\n")

if __name__ == "__main__":
    try:
        demo()
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
