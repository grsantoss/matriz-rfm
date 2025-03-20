# RFM Insights - Database Models

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Float, DateTime, Text, JSON, Index, CheckConstraint, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from datetime import datetime

from .database import Base

# Function to generate UUID
def generate_uuid():
    return str(uuid.uuid4())

# User model
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    company_name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_admin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    messages = relationship("Message", back_populates="user")
    rfm_analyses = relationship("RFMAnalysis", back_populates="user")
    api_keys = relationship("APIKey", back_populates="user")
    
    # Additional indexes
    __table_args__ = (
        Index('idx_user_company_name', company_name),
        Index('idx_user_created_at', created_at),
    )

# Message model
class Message(Base):
    __tablename__ = "messages"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    message_type = Column(String, nullable=False)  # sms, whatsapp, email
    company_name = Column(String, nullable=False)
    company_website = Column(String, nullable=True)
    company_description = Column(Text, nullable=True)
    segment = Column(String, nullable=False)
    objective = Column(String, nullable=False)
    seasonality = Column(String, nullable=True)
    tone = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    regeneration_attempts = Column(Integer, default=0, nullable=False)
    parent_id = Column(String, ForeignKey("messages.id"), nullable=True)
    sequence_number = Column(Integer, default=1, nullable=False)
    sequence_total = Column(Integer, default=1, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="messages")
    pdf = relationship("MessagePDF", back_populates="message", uselist=False)
    parent = relationship("Message", remote_side=[id], backref="regenerations")
    
    # Additional indexes and constraints
    __table_args__ = (
        Index('idx_message_user_id', user_id),
        Index('idx_message_type', message_type),
        Index('idx_message_segment', segment),
        Index('idx_message_created_at', created_at),
        CheckConstraint("message_type IN ('sms', 'whatsapp', 'email')", name="ck_message_type_valid"),
        CheckConstraint("regeneration_attempts >= 0", name="ck_regeneration_attempts_positive"),
    )

# Message PDF model
class MessagePDF(Base):
    __tablename__ = "message_pdfs"

    id = Column(String, primary_key=True, default=generate_uuid)
    message_id = Column(String, ForeignKey("messages.id"), nullable=False, unique=True)
    file_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    message = relationship("Message", back_populates="pdf")
    
    # Additional indexes
    __table_args__ = (
        Index('idx_message_pdf_created_at', created_at),
    )

# RFM Analysis model
class RFMAnalysis(Base):
    __tablename__ = "rfm_analyses"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    segment_type = Column(String, nullable=False)  # ecommerce, subscription, etc.
    file_name = Column(String, nullable=False)
    record_count = Column(Integer, nullable=False)
    column_mapping = Column(JSON, nullable=False)  # Stores column mapping as JSON
    segment_counts = Column(JSON, nullable=False)  # Stores segment counts as JSON
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="rfm_analyses")
    insights = relationship("AIInsight", back_populates="rfm_analysis")
    
    # Additional indexes and constraints
    __table_args__ = (
        Index('idx_rfm_analysis_user_id', user_id),
        Index('idx_rfm_analysis_segment_type', segment_type),
        Index('idx_rfm_analysis_created_at', created_at),
        UniqueConstraint('user_id', 'name', name='uq_user_analysis_name'),
        CheckConstraint("record_count > 0", name="ck_record_count_positive"),
    )

# AI Insight model
class AIInsight(Base):
    __tablename__ = "ai_insights"

    id = Column(String, primary_key=True, default=generate_uuid)
    rfm_analysis_id = Column(String, ForeignKey("rfm_analyses.id"), nullable=False)
    segment = Column(String, nullable=True)  # If segment-specific
    business_type = Column(String, nullable=True)  # If business-specific
    insight_type = Column(String, nullable=False)  # general, segment_specific, business_specific
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationships
    rfm_analysis = relationship("RFMAnalysis", back_populates="insights")
    
    # Additional indexes and constraints
    __table_args__ = (
        Index('idx_ai_insight_rfm_analysis_id', rfm_analysis_id),
        Index('idx_ai_insight_insight_type', insight_type),
        Index('idx_ai_insight_created_at', created_at),
        CheckConstraint("insight_type IN ('general', 'segment_specific', 'business_specific')", name="ck_insight_type_valid"),
    )

# API Key model
class APIKey(Base):
    __tablename__ = "api_keys"

    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    key = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    last_used_at = Column(DateTime, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="api_keys")
    
    # Additional indexes
    __table_args__ = (
        Index('idx_api_key_user_id', user_id),
        Index('idx_api_key_created_at', created_at),
        Index('idx_api_key_last_used_at', last_used_at),
    )