from app.services.route_optimizer import route_optimizer
from app.models.address import AddressWithCoordinates
import time

# Create 100 addresses
addresses = [
    AddressWithCoordinates(
        id=i, name=f"Stop{i}", street=f"Street{i}", city="Delhi",
        latitude=28.6139 + (i * 0.01), longitude=77.2090 + (i * 0.01)
    )
    for i in range(100)
]

start = time.time()
route, distance, comp_time = route_optimizer.optimize(addresses)
elapsed = time.time() - start

print(f"100 stops optimization:")
print(f"  Computation time: {comp_time}ms")
print(f"  Total distance: {distance:.2f} km")
print(f"  Route length: {len(route)}")
print(f"  Performance: {'✓ PASS (<500ms)' if comp_time < 500 else '✗ FAIL (>500ms)'}")
