# RFM Insights - API Utilities

from fastapi import HTTPException, Request
from typing import Any, Dict, List, Optional, Type, TypeVar, Union, Generic
from pydantic import BaseModel

from .schemas import ResponseSuccess, ResponseError, ResponseWarning, PaginatedResponseSuccess

# Type variable for generic response functions
T = TypeVar('T')

# API version constants
API_V1 = "v1"
CURRENT_API_VERSION = API_V1

def get_api_prefix(version: str = CURRENT_API_VERSION) -> str:
    """
    Get the API prefix for the specified version
    
    Args:
        version: API version string (default: current version)
        
    Returns:
        API prefix string (e.g., "/api/v1")
    """
    return f"/api/{version}"

def success_response(data: Optional[T] = None, message: str = "Operation successful") -> ResponseSuccess[T]:
    """
    Create a standardized success response
    
    Args:
        data: Response data (optional)
        message: Success message
        
    Returns:
        ResponseSuccess object
    """
    return ResponseSuccess(message=message, data=data)

def error_response(message: str, error_code: Optional[str] = None, details: Optional[Dict[str, Any]] = None) -> ResponseError:
    """
    Create a standardized error response
    
    Args:
        message: Error message
        error_code: Error code for client reference (optional)
        details: Additional error details (optional)
        
    Returns:
        ResponseError object
    """
    return ResponseError(message=message, error_code=error_code, details=details)

def warning_response(message: str, data: Optional[T] = None, warnings: List[str] = None) -> ResponseWarning[T]:
    """
    Create a standardized warning response
    
    Args:
        message: Warning message
        data: Response data (optional)
        warnings: List of warning messages (optional)
        
    Returns:
        ResponseWarning object
    """
    if warnings is None:
        warnings = []
    return ResponseWarning(message=message, data=data, warnings=warnings)

def paginated_response(
    data: List[T], 
    total: int, 
    page: int, 
    page_size: int,
    message: str = "Data retrieved successfully"
) -> PaginatedResponseSuccess[List[T]]:
    """
    Create a standardized paginated response
    
    Args:
        data: List of items for the current page
        total: Total number of items
        page: Current page number
        page_size: Number of items per page
        message: Success message
        
    Returns:
        PaginatedResponseSuccess object
    """
    pages = (total + page_size - 1) // page_size if page_size > 0 else 0
    return PaginatedResponseSuccess(
        message=message,
        data=data,
        total=total,
        page=page,
        page_size=page_size,
        pages=pages
    )

def http_exception_handler(request: Request, exc: HTTPException) -> ResponseError:
    """
    Convert HTTPException to standardized error response
    
    Args:
        request: FastAPI request object
        exc: HTTPException instance
        
    Returns:
        ResponseError object
    """
    return error_response(
        message=str(exc.detail),
        error_code=f"HTTP_{exc.status_code}",
        details={"path": request.url.path}
    )

def exception_handler(request: Request, exc: Exception) -> ResponseError:
    """
    Convert generic Exception to standardized error response
    
    Args:
        request: FastAPI request object
        exc: Exception instance
        
    Returns:
        ResponseError object
    """
    return error_response(
        message="Internal Server Error",
        error_code="INTERNAL_ERROR",
        details={
            "path": request.url.path,
            "error_type": exc.__class__.__name__,
            "error_detail": str(exc)
        }
    )