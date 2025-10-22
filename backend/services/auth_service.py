"""
Authentication Service
Phase 3: Enterprise & Security Features

Handles user authentication, JWT token management, password hashing, and RBAC.
"""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from sqlalchemy import or_
import uuid

from backend.models.user_models import User, UserRole, RefreshToken
from config.settings import settings

# Password hashing context with automatic truncation for bcrypt's 72-byte limit
pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__truncate_error=False  # Auto-truncate passwords longer than 72 bytes
)


class AuthenticationError(Exception):
    """Base exception for authentication errors"""
    pass


class InvalidCredentialsError(AuthenticationError):
    """Raised when credentials are invalid"""
    pass


class UserNotFoundError(AuthenticationError):
    """Raised when user is not found"""
    pass


class TokenExpiredError(AuthenticationError):
    """Raised when token is expired"""
    pass


class InsufficientPermissionsError(AuthenticationError):
    """Raised when user lacks required permissions"""
    pass


class AuthService:
    """
    Authentication and authorization service.
    
    Provides:
    - Password hashing and verification
    - JWT access token creation and validation
    - Refresh token management
    - User CRUD operations
    - Role-based access control (RBAC)
    """
    
    @staticmethod
    def hash_password(password: str) -> str:
        """
        Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        # Passlib's bcrypt is configured to auto-truncate at 72 bytes
        return pwd_context.hash(password)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """
        Verify a password against its hash.
        
        Args:
            plain_password: Plain text password to verify
            hashed_password: Hashed password to compare against
            
        Returns:
            True if password matches, False otherwise
        """
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Payload data to encode in token (user_id, email, role)
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(db: Session, user_id: str) -> str:
        """
        Create a refresh token and store it in database.
        
        Args:
            db: Database session
            user_id: User ID to create token for
            
        Returns:
            Refresh token string
        """
        token_id = str(uuid.uuid4())
        token = str(uuid.uuid4())
        
        expires_at = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        
        refresh_token = RefreshToken(
            id=token_id,
            user_id=user_id,
            token=pwd_context.hash(token),  # Hash the token before storing
            expires_at=expires_at
        )
        
        db.add(refresh_token)
        db.commit()
        
        return token
    
    @staticmethod
    def verify_token(token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string
            
        Returns:
            Decoded token payload
            
        Raises:
            TokenExpiredError: If token is expired
            AuthenticationError: If token is invalid
        """
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            return payload
        except JWTError as e:
            if "expired" in str(e).lower():
                raise TokenExpiredError("Token has expired")
            raise AuthenticationError(f"Invalid token: {str(e)}")
    
    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        """
        Authenticate user with email and password.
        
        Args:
            db: Database session
            email: User email
            password: Plain text password
            
        Returns:
            Authenticated user object
            
        Raises:
            InvalidCredentialsError: If credentials are invalid
            UserNotFoundError: If user doesn't exist
        """
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")
        
        if not user.is_active:
            raise InvalidCredentialsError("User account is inactive")
        
        if not AuthService.verify_password(password, user.hashed_password):
            raise InvalidCredentialsError("Invalid password")
        
        # Update last login
        user.last_login = datetime.utcnow()
        db.commit()
        
        return user
    
    @staticmethod
    def create_user(
        db: Session,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        role: UserRole = UserRole.USER
    ) -> User:
        """
        Create a new user.
        
        Args:
            db: Database session
            email: User email (must be unique)
            password: Plain text password (will be hashed)
            full_name: User's full name
            role: User role (default: USER)
            
        Returns:
            Created user object
            
        Raises:
            ValueError: If user with email already exists
        """
        # Check if user exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError(f"User with email {email} already exists")
        
        user_id = str(uuid.uuid4())
        hashed_password = AuthService.hash_password(password)
        
        user = User(
            id=user_id,
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
            role=role.value
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: str) -> Optional[User]:
        """Get user by ID"""
        return db.query(User).filter(User.id == user_id).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        """Get user by email"""
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def update_user(
        db: Session,
        user_id: str,
        **updates
    ) -> User:
        """
        Update user fields.
        
        Args:
            db: Database session
            user_id: User ID to update
            **updates: Fields to update
            
        Returns:
            Updated user object
            
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        # Update allowed fields
        allowed_fields = ['full_name', 'role', 'is_active', 'is_verified']
        for field, value in updates.items():
            if field in allowed_fields and hasattr(user, field):
                setattr(user, field, value)
        
        db.commit()
        db.refresh(user)
        
        return user
    
    @staticmethod
    def change_password(db: Session, user_id: str, old_password: str, new_password: str) -> bool:
        """
        Change user password.
        
        Args:
            db: Database session
            user_id: User ID
            old_password: Current password for verification
            new_password: New password to set
            
        Returns:
            True if password changed successfully
            
        Raises:
            UserNotFoundError: If user doesn't exist
            InvalidCredentialsError: If old password is incorrect
        """
        user = AuthService.get_user_by_id(db, user_id)
        if not user:
            raise UserNotFoundError(f"User {user_id} not found")
        
        if not AuthService.verify_password(old_password, user.hashed_password):
            raise InvalidCredentialsError("Current password is incorrect")
        
        user.hashed_password = AuthService.hash_password(new_password)
        db.commit()
        
        return True
    
    @staticmethod
    def check_permission(user: User, required_role: UserRole) -> bool:
        """
        Check if user has required role or higher.
        
        Role hierarchy: ADMIN > USER > VIEWER, AUDITOR
        
        Args:
            user: User object
            required_role: Minimum required role
            
        Returns:
            True if user has permission
        """
        role_hierarchy = {
            UserRole.ADMIN: 3,
            UserRole.USER: 2,
            UserRole.AUDITOR: 1,
            UserRole.VIEWER: 1
        }
        
        user_level = role_hierarchy.get(UserRole(user.role), 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level
    
    @staticmethod
    def revoke_refresh_token(db: Session, token: str) -> bool:
        """
        Revoke a refresh token.
        
        Args:
            db: Database session
            token: Refresh token to revoke
            
        Returns:
            True if token was revoked
        """
        # Find matching token
        refresh_tokens = db.query(RefreshToken).filter(RefreshToken.is_revoked == False).all()
        
        for rt in refresh_tokens:
            if pwd_context.verify(token, rt.token):
                rt.is_revoked = True
                db.commit()
                return True
        
        return False
    
    @staticmethod
    def cleanup_expired_tokens(db: Session) -> int:
        """
        Remove expired refresh tokens from database.
        
        Args:
            db: Database session
            
        Returns:
            Number of tokens deleted
        """
        now = datetime.utcnow()
        expired_tokens = db.query(RefreshToken).filter(
            or_(
                RefreshToken.expires_at < now,
                RefreshToken.is_revoked == True
            )
        ).all()
        
        count = len(expired_tokens)
        
        for token in expired_tokens:
            db.delete(token)
        
        db.commit()
        
        return count
