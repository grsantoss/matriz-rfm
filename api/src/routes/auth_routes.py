# RFM Insights - Authentication Routes

from fastapi import APIRouter, Depends, HTTPException, status, Form
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from typing import Optional, Dict, Any

# Import response utilities
from .api_utils import success_response, error_response
from .schemas import ResponseSuccess, ResponseError, UserResponse, TokenResponse

from backend import models
from .database import get_db
from .auth import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_user,
    get_current_active_user
)
from config import config

# Create router
router = APIRouter()

# Token endpoint
@router.post("/token", response_model=ResponseSuccess[TokenResponse], description="Authenticate user and return access token")
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Authenticate user and return access token"""
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=access_token_expires
    )
    
    token_data = {
        "access_token": access_token, 
        "token_type": "bearer",
        "expires_in": config.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
    
    return success_response(
        data=token_data,
        message="Authentication successful"
    )

# Register endpoint
@router.post("/register", status_code=status.HTTP_201_CREATED, response_model=ResponseSuccess, description="Register a new user")
async def register_user(user_data: dict, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    existing_user = db.query(models.User).filter(models.User.email == user_data["email"]).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado"
        )
    
    # Create new user
    hashed_password = get_password_hash(user_data["password"])
    new_user = models.User(
        email=user_data["email"],
        password=hashed_password,
        name=user_data.get("name", ""),
        company=user_data.get("company", ""),
        is_active=True,
        is_admin=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return success_response(message="Usuário cadastrado com sucesso")

# User profile endpoint
@router.get("/me", response_model=ResponseSuccess[UserResponse], description="Get current user profile")
async def get_user_profile(current_user = Depends(get_current_active_user)):
    """Get current user profile"""
    user_data = {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "company": current_user.company,
        "is_admin": current_user.is_admin
    }
    
    return success_response(
        data=user_data,
        message="User profile retrieved successfully"
    )

# Update user profile endpoint
@router.put("/me", response_model=ResponseSuccess, description="Update current user profile")
async def update_user_profile(
    user_data: dict,
    current_user = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    # Update user fields
    if "name" in user_data:
        current_user.name = user_data["name"]
    if "company" in user_data:
        current_user.company = user_data["company"]
    
    # Update password if provided
    if "password" in user_data and user_data["password"]:
        current_user.password = get_password_hash(user_data["password"])
    
    db.commit()
    db.refresh(current_user)
    
    return success_response(message="Perfil atualizado com sucesso")

# Password reset request endpoint
@router.post("/password-reset", response_model=ResponseSuccess, description="Request password reset")
async def request_password_reset(email_data: dict, db: Session = Depends(get_db)):
    """Request password reset"""
    email = email_data.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email não fornecido"
        )
    
    # Check if user exists
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        # Don't reveal that the user doesn't exist
        return success_response(message="Se o email estiver cadastrado, você receberá um link para redefinir sua senha")
    
    # In a real application, generate a reset token and send email
    # For this example, we'll just return a success message
    
    return success_response(message="Se o email estiver cadastrado, você receberá um link para redefinir sua senha")

# Password reset confirmation endpoint
@router.post("/password-reset/confirm", response_model=ResponseSuccess, description="Reset password with token")
async def reset_password(reset_data: dict, db: Session = Depends(get_db)):
    """Reset password with token"""
    token = reset_data.get("token")
    new_password = reset_data.get("new_password")
    
    if not token or not new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token ou nova senha não fornecidos"
        )
    
    # In a real application, validate the token and find the user
    # For this example, we'll just return a success message
    
    return success_response(message="Senha redefinida com sucesso")