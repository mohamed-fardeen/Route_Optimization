from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    business_name = Column(String(255), unique=True)
    contact_name = Column(String(255))
    email = Column(String(255), unique=True)
    phone = Column(String(20))
    api_key = Column(String(255), unique=True, index=True)
    subscription_plan = Column(String(50), default="free")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class Address(Base):
    """Address model for storing delivery locations"""
    __tablename__ = "addresses"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, index=True)
    name = Column(String(255))
    street = Column(String(255))
    city = Column(String(100))
    postal_code = Column(String(20), nullable=True)
    latitude = Column(Float)
    longitude = Column(Float)
    phone = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class Route(Base):
    """Route model for storing optimization results"""
    __tablename__ = "routes"
    
    id = Column(Integer, primary_key=True)
    route_id = Column(String(50), unique=True, index=True)
    user_id = Column(Integer, index=True)
    optimization_date = Column(DateTime, default=datetime.utcnow)
    total_distance_km = Column(Float)
    total_cost_inr = Column(Float)
    cost_saved_inr = Column(Float)
    route_data = Column(Text)  # JSON string
    created_at = Column(DateTime, default=datetime.utcnow)

class OptimizationHistory(Base):
    """History model for tracking optimizations"""
    __tablename__ = "optimization_history"
    
    id = Column(Integer, primary_key=True)
    request_id = Column(String(50), unique=True, index=True)
    user_id = Column(Integer, index=True)
    addresses_count = Column(Integer)
    computation_time_ms = Column(Integer)
    quality_score = Column(Float)
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

