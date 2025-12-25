from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.models import User, Route, OptimizationHistory
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class CRUDUser:
    """CRUD operations for User model"""
    
    @staticmethod
    def get_by_api_key(db: Session, api_key: str):
        """Get user by API key"""
        return db.query(User).filter(User.api_key == api_key).first()
    
    @staticmethod
    def get_by_id(db: Session, user_id: int):
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def create(db: Session, business_name: str, contact_name: str, email: str, 
               phone: str, api_key: str, subscription_plan: str = "free"):
        """Create new user"""
        user = User(
            business_name=business_name,
            contact_name=contact_name,
            email=email,
            phone=phone,
            api_key=api_key,
            subscription_plan=subscription_plan,
            created_at=datetime.utcnow()
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user

class CRUDRoute:
    """CRUD operations for Route model"""
    
    @staticmethod
    def create(db: Session, route_id: str, user_id: int, total_distance_km: float,
               total_cost_inr: float, cost_saved_inr: float, route_data: str):
        """Create new route"""
        route = Route(
            route_id=route_id,
            user_id=user_id,
            total_distance_km=total_distance_km,
            total_cost_inr=total_cost_inr,
            cost_saved_inr=cost_saved_inr,
            route_data=route_data,
            optimization_date=datetime.utcnow(),
            created_at=datetime.utcnow()
        )
        db.add(route)
        db.commit()
        db.refresh(route)
        return route
    
    @staticmethod
    def get_user_routes(db: Session, user_id: int, limit: int = 100):
        """Get all routes for a user, ordered by date descending"""
        return db.query(Route).filter(
            Route.user_id == user_id
        ).order_by(desc(Route.optimization_date)).limit(limit).all()
    
    @staticmethod
    def get_by_route_id(db: Session, route_id: str):
        """Get route by route ID"""
        return db.query(Route).filter(Route.route_id == route_id).first()
    
    @staticmethod
    def delete(db: Session, route_id: str, user_id: int):
        """Delete route (ensure user ownership)"""
        route = db.query(Route).filter(
            Route.route_id == route_id,
            Route.user_id == user_id
        ).first()
        if route:
            db.delete(route)
            db.commit()
            return True
        return False
    
    @staticmethod
    def get_user_stats(db: Session, user_id: int):
        """Get user's route statistics"""
        routes = db.query(Route).filter(Route.user_id == user_id).all()
        
        if not routes:
            return {
                "total_routes": 0,
                "total_distance_km": 0,
                "total_cost_saved_inr": 0,
                "average_distance_km": 0,
                "routes_this_month": 0
            }
        
        total_routes = len(routes)
        total_distance_km = sum(r.total_distance_km for r in routes)
        total_cost_saved_inr = sum(r.cost_saved_inr for r in routes)
        average_distance_km = total_distance_km / total_routes if total_routes > 0 else 0
        
        # Count routes from this month
        now = datetime.utcnow()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        routes_this_month = len([r for r in routes if r.optimization_date >= month_start])
        
        return {
            "total_routes": total_routes,
            "total_distance_km": round(total_distance_km, 2),
            "total_cost_saved_inr": round(total_cost_saved_inr, 2),
            "average_distance_km": round(average_distance_km, 2),
            "routes_this_month": routes_this_month
        }

class CRUDOptimization:
    """CRUD operations for OptimizationHistory model"""
    
    @staticmethod
    def create(db: Session, request_id: str, user_id: int, addresses_count: int,
               computation_time_ms: int, quality_score: float, success: bool = True,
               error_message: str = None):
        """Create optimization history record"""
        history = OptimizationHistory(
            request_id=request_id,
            user_id=user_id,
            addresses_count=addresses_count,
            computation_time_ms=computation_time_ms,
            quality_score=quality_score,
            success=success,
            error_message=error_message,
            created_at=datetime.utcnow()
        )
        db.add(history)
        db.commit()
        db.refresh(history)
        return history
    
    @staticmethod
    def get_user_history(db: Session, user_id: int, limit: int = 100):
        """Get optimization history for user"""
        return db.query(OptimizationHistory).filter(
            OptimizationHistory.user_id == user_id
        ).order_by(desc(OptimizationHistory.created_at)).limit(limit).all()
    
    @staticmethod
    def get_by_request_id(db: Session, request_id: str):
        """Get history by request ID"""
        return db.query(OptimizationHistory).filter(
            OptimizationHistory.request_id == request_id
        ).first()
