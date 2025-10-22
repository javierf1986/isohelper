"""
User Authentication and Authorization Models
Phase 3: Enterprise & Security Features

Database models for user management, authentication, and RBAC.
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
from enum import Enum
from backend.models.iso_models import Base


class UserRole(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"          # Full system access
    USER = "user"            # Standard user access
    VIEWER = "viewer"        # Read-only access
    AUDITOR = "auditor"      # Special read-only for compliance


class User(Base):
    """
    User model for authentication and authorization.
    
    Fields:
        id: Unique user identifier (UUID)
        email: User email (unique, used for login)
        hashed_password: Bcrypt hashed password
        full_name: User's full name
        role: User role for RBAC (admin/user/viewer/auditor)
        is_active: Account active status
        is_verified: Email verification status
        created_at: Account creation timestamp
        updated_at: Last update timestamp
        last_login: Last successful login timestamp
        workspaces: Related workspaces (one-to-many)
    """
    __tablename__ = "users"

    id = Column(String(50), primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(50), nullable=False, default=UserRole.USER.value)
    is_active = Column(Boolean, default=True, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    workspaces = relationship("Workspace", back_populates="owner")
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
    
    def to_dict(self):
        """Convert to dictionary (exclude password)"""
        return {
            "id": self.id,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "created_at": self.created_at.isoformat() if self.created_at is not None else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at is not None else None,
            "last_login": self.last_login.isoformat() if self.last_login is not None else None,
        }


class RefreshToken(Base):
    """
    Refresh token model for JWT token rotation.
    
    Fields:
        id: Unique token identifier
        user_id: Foreign key to users table
        token: Hashed refresh token
        expires_at: Token expiration timestamp
        created_at: Token creation timestamp
        is_revoked: Token revocation status
        user: Related user (many-to-one)
    """
    __tablename__ = "refresh_tokens"

    id = Column(String(50), primary_key=True)
    user_id = Column(String(50), ForeignKey('users.id'), nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    is_revoked = Column(Boolean, default=False, nullable=False)
    
    # Relationships
    user = relationship("User")
    
    def __repr__(self):
        return f"<RefreshToken {self.id} for user {self.user_id}>"
