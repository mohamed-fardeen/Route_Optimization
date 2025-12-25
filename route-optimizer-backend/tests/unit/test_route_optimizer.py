import pytest
from app.services.route_optimizer import RouteOptimizer
from app.models.address import AddressWithCoordinates

@pytest.fixture
def optimizer():
    return RouteOptimizer(timeout_seconds=5)

@pytest.fixture
def addresses():
    return [
        AddressWithCoordinates(
            id=0, name="Office", street="Office", city="Delhi",
            latitude=28.6139, longitude=77.2090
        ),
        AddressWithCoordinates(
            id=1, name="A1", street="123", city="Delhi",
            latitude=28.6145, longitude=77.2100
        ),
        AddressWithCoordinates(
            id=2, name="A2", street="456", city="Delhi",
            latitude=28.6150, longitude=77.2110
        ),
    ]

def test_optimize(optimizer, addresses):
    route, dist, time_ms = optimizer.optimize(addresses)
    # Route includes depot at start and end, so length is n+1
    assert len(route) == 4  # 3 addresses + return to depot
    assert route[0] == 0
    assert route[-1] == 0
    assert dist > 0
    assert time_ms < 5000

def test_needs_two_addresses(optimizer):
    with pytest.raises(ValueError):
        optimizer.optimize([])

def test_single_address(optimizer):
    with pytest.raises(ValueError):
        addresses = [
            AddressWithCoordinates(
                id=0, name="Office", street="Office", city="Delhi",
                latitude=28.6139, longitude=77.2090
            )
        ]
        optimizer.optimize(addresses)

def test_multiple_addresses(optimizer):
    """Test with more addresses"""
    addresses = [
        AddressWithCoordinates(
            id=i, name=f"Stop{i}", street=f"Street{i}", city="Delhi",
            latitude=28.6139 + (i * 0.001), longitude=77.2090 + (i * 0.001)
        )
        for i in range(5)
    ]
    route, dist, time_ms = optimizer.optimize(addresses)
    assert len(route) == 6  # 5 addresses + return to depot
    assert route[0] == 0
    assert route[-1] == 0
    assert dist > 0
    assert time_ms < 5000

def test_closed_loop_route(optimizer, addresses):
    """Route must start and end at depot"""
    route, dist, time_ms = optimizer.optimize(addresses)
    assert route[0] == route[-1]

def test_all_addresses_visited(optimizer, addresses):
    """Each address visited exactly once"""
    route, dist, time_ms = optimizer.optimize(addresses)
    # First element is depot, last is return to depot
    assert set(route[:-1]) == {0, 1, 2}
    assert route.count(0) == 2  # Start and end at depot
