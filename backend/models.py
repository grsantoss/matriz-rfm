# RFM Insights - Database Models

from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Boolean, 
    ForeignKey, Text, JSON, Index, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from .database import Base

def generate_uuid():
    """Generate a UUID string."""
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relationships
    rfm_analyses = relationship("RFMAnalysis", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")

    __table_args__ = (
        Index('idx_user_email', email),
        Index('idx_user_company', company_name),
    )

class RFMAnalysis(Base):
    __tablename__ = "rfm_analyses"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text)
    original_file_name = Column(String, nullable=False)
    original_file_path = Column(String, nullable=False)
    processed_file_path = Column(String, nullable=False)  # Path to the processed file with results
    analysis_date = Column(DateTime, default=func.now())
    parameters = Column(JSON, nullable=False)  # Store analysis parameters
    results = Column(JSON, nullable=False)     # Store overall analysis results
    segment_counts = Column(JSON, nullable=False)  # Store segment distribution
    total_customers = Column(Integer, nullable=False)
    column_mapping = Column(JSON, nullable=False)  # Maps original columns to required fields
    
    # Relationships
    user = relationship("User", back_populates="rfm_analyses")
    insights = relationship("AIInsight", back_populates="analysis")
    customer_records = relationship("CustomerRecord", back_populates="analysis")

    __table_args__ = (
        Index('idx_rfm_user_date', user_id, analysis_date),
        UniqueConstraint('user_id', 'name', name='uq_user_analysis_name'),
    )

class CustomerRecord(Base):
    __tablename__ = "customer_records"

    id = Column(String, primary_key=True, default=generate_uuid)
    analysis_id = Column(String, ForeignKey("rfm_analyses.id"), nullable=False)
    customer_id = Column(String, nullable=False)  # Original customer identifier
    recency_value = Column(Float, nullable=False)
    frequency_value = Column(Integer, nullable=False)
    monetary_value = Column(Float, nullable=False)
    recency_score = Column(Integer, nullable=False)
    frequency_score = Column(Integer, nullable=False)
    monetary_score = Column(Integer, nullable=False)
    rfm_score = Column(Integer, nullable=False)
    segment = Column(String, nullable=False)
    original_data = Column(JSON, nullable=False)  # Store original row data
    created_at = Column(DateTime, default=func.now())

    # Relationships
    analysis = relationship("RFMAnalysis", back_populates="customer_records")

    __table_args__ = (
        Index('idx_customer_analysis', analysis_id),
        Index('idx_customer_segment', segment),
        UniqueConstraint('analysis_id', 'customer_id', name='uq_analysis_customer'),
    )

class AIInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(String, primary_key=True, default=generate_uuid)
    analysis_id = Column(String, ForeignKey("rfm_analyses.id"), nullable=False)
    segment = Column(String)  # Optional: specific segment this insight is for
    insight_type = Column(String, nullable=False)  # e.g., 'general', 'segment_specific'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now())

    # Relationships
    analysis = relationship("RFMAnalysis", back_populates="insights")

    __table_args__ = (
        Index('idx_insight_analysis', analysis_id),
        Index('idx_insight_segment', segment),
    )

class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    key = Column(String, unique=True, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    last_used = Column(DateTime)
    expires_at = Column(DateTime)

    # Relationships
    user = relationship("User", back_populates="api_keys")

    __table_args__ = (
        Index('idx_apikey_user', user_id),
        Index('idx_apikey_key', key),
    ) 