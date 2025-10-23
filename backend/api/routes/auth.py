"""
Authentication API Routes
Phase 3: Enterprise & Security Features

Endpoints for user registration, login, token management, and profile.
"""
from datetime import timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from backend.services.auth_service import (
    AuthService,
    InvalidCredentialsError,
    UserNotFoundError,
    AuthenticationError
)
from backend.models.user_models import User, UserRole
from backend.api.dependencies import get_db, get_current_user, get_current_active_user, require_admin
from config.settings import settings


router = APIRouter(prefix="/auth", tags=["Authentication"])


# ===== Request/Response Models =====

class RegisterRequest(BaseModel):
    """User registration request"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., min_length=8, max_length=72, description="Password (8-72 characters)")
    full_name: Optional[str] = Field(None, description="User's full name")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!",
                "full_name": "John Doe"
            }
        }


class LoginRequest(BaseModel):
    """User login request"""
    email: str = Field(..., description="User email address")
    password: str = Field(..., description="User password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "email": "user@example.com",
                "password": "SecurePassword123!"
            }
        }


class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token for token rotation")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "refresh_token": "550e8400-e29b-41d4-a716-446655440000",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class UserResponse(BaseModel):
    """User profile response"""
    id: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    created_at: Optional[str]
    last_login: Optional[str]
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "full_name": "John Doe",
                "role": "user",
                "is_active": True,
                "is_verified": False,
                "created_at": "2025-10-22T10:30:00",
                "last_login": "2025-10-22T14:45:00"
            }
        }


class ChangePasswordRequest(BaseModel):
    """Change password request"""
    old_password: str = Field(..., description="Current password")
    new_password: str = Field(..., min_length=8, description="New password (min 8 characters)")


class RefreshTokenRequest(BaseModel):
    """Refresh token request"""
    refresh_token: str = Field(..., description="Refresh token to exchange for new access token")


# ===== Authentication Endpoints =====

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: RegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new user account.
    
    - **email**: User email (must be unique)
    - **password**: Strong password (min 8 characters)
    - **full_name**: Optional full name
    
    Returns user profile without password.
    """
    try:
        user = AuthService.create_user(
            db=db,
            email=request.email,
            password=request.password,
            full_name=request.full_name,
            role=UserRole.USER  # Default role
        )
        
        return user.to_dict()
    
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=TokenResponse)
async def login(
    request: LoginRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user and return JWT tokens.
    
    - **email**: User email
    - **password**: User password
    
    Returns access token (30 min) and refresh token (7 days).
    """
    try:
        user = AuthService.authenticate_user(db, request.email, request.password)
        
        # Create access token
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = AuthService.create_access_token(
            data={"sub": user.id, "email": user.email, "role": user.role},
            expires_delta=access_token_expires
        )
        
        # Create refresh token
        refresh_token = AuthService.create_refresh_token(db, user.id)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60  # Convert to seconds
        }
    
    except (InvalidCredentialsError, UserNotFoundError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get current authenticated user's profile.
    
    Requires valid JWT token in Authorization header.
    """
    return current_user.to_dict()


@router.put("/me", response_model=UserResponse)
async def update_current_user_profile(
    full_name: Optional[str] = None,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile.
    
    - **full_name**: Update full name
    """
    updates = {}
    if full_name is not None:
        updates["full_name"] = full_name
    
    if updates:
        user = AuthService.update_user(db, current_user.id, **updates)
        return user.to_dict()
    
    return current_user.to_dict()


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """
    Change current user's password.
    
    - **old_password**: Current password for verification
    - **new_password**: New password to set
    """
    try:
        AuthService.change_password(
            db,
            current_user.id,
            request.old_password,
            request.new_password
        )
        
        return {"message": "Password changed successfully"}
    
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request: RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    
    - **refresh_token**: Valid refresh token from login
    
    Returns new access token and refresh token.
    """
    # TODO: Implement refresh token validation
    # For now, return error
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Refresh token endpoint not yet implemented"
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    refresh_token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Logout user by revoking refresh token.
    
    - **refresh_token**: Refresh token to revoke
    """
    success = AuthService.revoke_refresh_token(db, refresh_token)
    
    if success:
        return {"message": "Logged out successfully"}
    
    return {"message": "Token already revoked or not found"}


# ===== Admin Endpoints =====

@router.get("/users", response_model=list[UserResponse])
async def list_users(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 100
):
    """
    List all users (Admin only).
    
    - **skip**: Number of records to skip (pagination)
    - **limit**: Maximum number of records to return
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return [user.to_dict() for user in users]


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    role: UserRole,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Update user's role (Admin only).
    
    - **user_id**: User ID to update
    - **role**: New role (admin, user, viewer, auditor)
    """
    try:
        user = AuthService.update_user(db, user_id, role=role.value)
        return user.to_dict()
    
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Deactivate user account (Admin only).
    
    - **user_id**: User ID to deactivate
    """
    try:
        user = AuthService.update_user(db, user_id, is_active=False)
        return {"message": f"User {user.email} deactivated successfully"}
    
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
