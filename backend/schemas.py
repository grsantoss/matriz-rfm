# RFM Insights - API Response Schemas

from typing import TypeVar, Generic, Optional, List, Dict, Any, Union
from pydantic import BaseModel, Field

# Generic type for response data
T = TypeVar('T')

class ResponseBase(BaseModel):
    """Base model for all API responses"""
    status: str = Field(..., description="Status of the response (success, error, warning)")
    message: str = Field(..., description="Human-readable message about the response")

class ResponseSuccess(ResponseBase, Generic[T]):
    """Success response model with data"""
    status: str = "success"
    data: Optional[T] = Field(None, description="Response data")

class ResponseError(ResponseBase):
    """Error response model"""
    status: str = "error"
    error_code: Optional[str] = Field(None, description="Error code for client reference")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

class ResponseWarning(ResponseBase, Generic[T]):
    """Warning response model with data"""
    status: str = "warning"
    data: Optional[T] = Field(None, description="Response data")
    warnings: List[str] = Field([], description="List of warning messages")

class PaginatedResponseSuccess(ResponseSuccess[T]):
    """Paginated success response model"""
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    pages: int = Field(..., description="Total number of pages")

# Common response models for specific data types
class UserResponse(BaseModel):
    """User data response model"""
    id: int
    email: str
    name: str
    company: Optional[str] = None
    is_admin: bool

class TokenResponse(BaseModel):
    """Token response model"""
    access_token: str
    token_type: str
    expires_in: int

# Example of how to use these models in FastAPI endpoints:
"""
from fastapi import APIRouter, Depends, HTTPException
from typing import List

router = APIRouter()

@router.get("/users", response_model=ResponseSuccess[List[UserResponse]])
async def get_users():
    # Your logic here
    users = [...]  # Get users from database
    return ResponseSuccess(message="Users retrieved successfully", data=users)

@router.get("/users/{user_id}", response_model=ResponseSuccess[UserResponse])
async def get_user(user_id: int):
    # Your logic here
    try:
        user = ...  # Get user from database
        return ResponseSuccess(message="User retrieved successfully", data=user)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
"""