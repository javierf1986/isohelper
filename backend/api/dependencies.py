"""
Authentication Middleware and Dependencies
Phase 3: Enterprise & Security Features

FastAPI dependencies for JWT authentication and role-based access control.
"""
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from backend.services.auth_service import AuthService, AuthenticationError, TokenExpiredError
from backend.models.user_models import User, UserRole
from backend.database.database import SessionLocal


# Security scheme
security = HTTPBearer()


def get_db():
    """Database dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token from Authorization header
        db: Database session
        
    Returns:
        Current authenticated user
        
    Raises:
        HTTPException: 401 if token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        token = credentials.credentials
        payload = AuthService.verify_token(token)
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
        
    except TokenExpiredError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except AuthenticationError:
        raise credentials_exception
    
    user = AuthService.get_user_by_id(db, user_id)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency to ensure user is active.
    
    Args:
        current_user: Current user from get_current_user
        
    Returns:
        Active user
        
    Raises:
        HTTPException: 403 if user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    return current_user


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: Session = Depends(get_db)
) -> Optional[User]:
    """
    Dependency for optional authentication (returns None if no token).
    
    Args:
        credentials: Optional HTTP Bearer token
        db: Database session
        
    Returns:
        User if authenticated, None otherwise
    """
    if not credentials:
        return None
    
    try:
        token = credentials.credentials
        payload = AuthService.verify_token(token)
        user_id: str = payload.get("sub")
        
        if user_id:
            return AuthService.get_user_by_id(db, user_id)
    except (AuthenticationError, TokenExpiredError):
        pass
    
    return None


class RoleChecker:
    """
    Dependency class for role-based access control.
    
    Usage:
        @app.get("/admin")
        async def admin_route(user: User = Depends(RoleChecker([UserRole.ADMIN]))):
            ...
    """
    
    def __init__(self, allowed_roles: list[UserRole]):
        self.allowed_roles = allowed_roles
    
    async def __call__(
        self,
        current_user: User = Depends(get_current_user)
    ) -> User:
        """
        Check if user has required role.
        
        Args:
            current_user: Current authenticated user
            
        Returns:
            User if authorized
            
        Raises:
            HTTPException: 403 if user lacks required role
        """
        user_role = UserRole(current_user.role)
        
        if user_role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"User role '{user_role.value}' is not authorized. Required: {[r.value for r in self.allowed_roles]}"
            )
        
        return current_user


# Convenience dependencies for common role checks
require_admin = RoleChecker([UserRole.ADMIN])
require_user = RoleChecker([UserRole.ADMIN, UserRole.USER])
require_viewer = RoleChecker([UserRole.ADMIN, UserRole.USER, UserRole.VIEWER, UserRole.AUDITOR])
