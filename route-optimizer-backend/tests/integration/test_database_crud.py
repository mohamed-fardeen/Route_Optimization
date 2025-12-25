import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database.connection import SessionLocal
from app.database.models import Base
from app.database.crud import CRUDUser, CRUDRoute
import uuid
import json

client = TestClient(app)

@pytest.fixture
def db_session():
    """Create a test database session"""
    # Setup
    Base.metadata.create_all(bind=None)
    session = SessionLocal()
    
    yield session
    
    # Teardown
    session.close()

@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = CRUDUser.create(
        db=db_session,
        business_name="Test Delivery",
        contact_name="John Doe",
        email="john@test.com",
        phone="+919876543210",
        api_key="test_api_key_12345",
        subscription_plan="premium"
    )
    return user

class TestDatabaseCRUD:
    """Test CRUD operations"""
    
    def test_create_user(self, db_session):
        """Test creating a user"""
        user = CRUDUser.create(
            db=db_session,
            business_name="FastCourierCo",
            contact_name="Jane Smith",
            email="jane@courier.com",
            phone="+919123456789",
            api_key="api_key_001",
            subscription_plan="premium"
        )
        
        assert user.id is not None
        assert user.business_name == "FastCourierCo"
        assert user.api_key == "api_key_001"
        assert user.subscription_plan == "premium"
    
    def test_get_user_by_api_key(self, db_session, test_user):
        """Test retrieving user by API key"""
        retrieved = CRUDUser.get_by_api_key(db_session, "test_api_key_12345")
        
        assert retrieved is not None
        assert retrieved.id == test_user.id
        assert retrieved.business_name == "Test Delivery"
    
    def test_get_user_by_api_key_invalid(self, db_session):
        """Test retrieving non-existent user"""
        retrieved = CRUDUser.get_by_api_key(db_session, "invalid_key")
        assert retrieved is None
    
    def test_create_route(self, db_session, test_user):
        """Test creating a route record"""
        route = CRUDRoute.create(
            db=db_session,
            route_id=str(uuid.uuid4()),
            user_id=test_user.id,
            total_distance_km=45.5,
            total_cost_inr=546.0,
            cost_saved_inr=120.5,
            route_data=json.dumps({"stops": 5})
        )
        
        assert route.id is not None
        assert route.user_id == test_user.id
        assert route.total_distance_km == 45.5
        assert route.cost_saved_inr == 120.5
    
    def test_get_user_routes(self, db_session, test_user):
        """Test retrieving user's routes"""
        # Create multiple routes
        for i in range(3):
            CRUDRoute.create(
                db=db_session,
                route_id=f"route_{i}",
                user_id=test_user.id,
                total_distance_km=10 + i * 5,
                total_cost_inr=100 + i * 50,
                cost_saved_inr=10 + i * 5,
                route_data=json.dumps({"stops": i})
            )
        
        routes = CRUDRoute.get_user_routes(db_session, test_user.id, limit=10)
        
        assert len(routes) == 3
        assert routes[0].user_id == test_user.id
    
    def test_delete_route(self, db_session, test_user):
        """Test deleting a route"""
        route = CRUDRoute.create(
            db=db_session,
            route_id="delete_test_route",
            user_id=test_user.id,
            total_distance_km=20.0,
            total_cost_inr=240.0,
            cost_saved_inr=50.0,
            route_data=json.dumps({"stops": 2})
        )
        
        success = CRUDRoute.delete(db_session, "delete_test_route", test_user.id)
        assert success is True
        
        retrieved = CRUDRoute.get_by_route_id(db_session, "delete_test_route")
        assert retrieved is None
    
    def test_get_user_stats(self, db_session, test_user):
        """Test getting user statistics"""
        # Create some routes
        for i in range(2):
            CRUDRoute.create(
                db=db_session,
                route_id=f"stat_route_{i}",
                user_id=test_user.id,
                total_distance_km=30.0,
                total_cost_inr=360.0,
                cost_saved_inr=100.0,
                route_data=json.dumps({"stops": 5})
            )
        
        stats = CRUDRoute.get_user_stats(db_session, test_user.id)
        
        assert stats["total_routes"] == 2
        assert stats["total_distance_km"] == 60.0
        assert stats["total_cost_saved_inr"] == 200.0
        assert stats["average_distance_km"] == 30.0

class TestHistoryEndpoints:
    """Test history API endpoints"""
    
    def test_get_routes_unauthorized(self):
        """Test get routes with invalid API key"""
        response = client.get("/api/history/routes?api_key=invalid_key")
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid API key"
    
    def test_get_routes_requires_api_key(self):
        """Test get routes requires API key parameter"""
        response = client.get("/api/history/routes")
        assert response.status_code == 422  # Missing required parameter
    
    def test_get_analytics_unauthorized(self):
        """Test get analytics with invalid API key"""
        response = client.get("/api/history/analytics?api_key=invalid_key")
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid API key"
    
    def test_delete_route_unauthorized(self):
        """Test delete route with invalid API key"""
        response = client.delete("/api/history/routes/test_route?api_key=invalid_key")
        assert response.status_code == 401

class TestHistoryIntegration:
    """Integration tests for history endpoints"""
    
    def test_history_workflow(self):
        """Test complete history workflow"""
        # Note: These tests would require actual database setup with the test client
        # For now, we validate the endpoint structure
        
        # Get routes with invalid key should fail
        response = client.get("/api/history/routes?api_key=invalid")
        assert response.status_code in [401, 422]
        
        # Analytics endpoint should exist
        response = client.get("/api/history/analytics?api_key=invalid")
        assert response.status_code in [401, 422]
        
        # Delete endpoint should exist
        response = client.delete("/api/history/routes/test?api_key=invalid")
        assert response.status_code in [401, 422, 404]
