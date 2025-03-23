# RFM Insights - Pydantic Schemas

from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, Dict, List, Any
from datetime import datetime
import re

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    company_name: str = Field(..., min_length=2, max_length=100)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

    @validator('password')
    def validate_password(cls, v):
        if not re.match(r'^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$', v):
            raise ValueError('Password must contain at least one letter and one number')
        return v

class UserUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=100)
    company_name: Optional[str] = Field(None, min_length=2, max_length=100)
    password: Optional[str] = Field(None, min_length=8)

class UserResponse(UserBase):
    id: str
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class RFMAnalysisBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = None

class RFMAnalysisCreate(RFMAnalysisBase):
    parameters: Dict[str, Any]

class RFMAnalysisResponse(RFMAnalysisBase):
    id: str
    user_id: str
    file_name: str
    analysis_date: datetime
    parameters: Dict[str, Any]
    results: Dict[str, Any]
    segment_counts: Dict[str, int]
    total_customers: int

    class Config:
        orm_mode = True

class AIInsightBase(BaseModel):
    segment: Optional[str] = None
    insight_type: str
    content: str

class AIInsightCreate(AIInsightBase):
    analysis_id: str

class AIInsightResponse(AIInsightBase):
    id: str
    analysis_id: str
    created_at: datetime

    class Config:
        orm_mode = True

class APIKeyBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=50)

class APIKeyCreate(APIKeyBase):
    expires_at: Optional[datetime] = None

class APIKeyResponse(APIKeyBase):
    id: str
    key: str
    user_id: str
    is_active: bool
    created_at: datetime
    last_used: Optional[datetime]
    expires_at: Optional[datetime]

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None 