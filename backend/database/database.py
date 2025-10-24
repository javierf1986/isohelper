"""
Database Session Management
Phase 3: Enterprise & Security Features

Provides database engine and session management for the application.
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from config.settings import settings

# Create database engine
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {},
    echo=False  # Set to True for SQL query logging
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """
    Get database session.
    
    Yields:
        Database session
        
    Usage in FastAPI:
        @app.get("/")
        def read_root(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database tables.
    Creates all tables defined in models.
    """
    from backend.models.iso_models import Base
    from backend.models.user_models import User, RefreshToken
    from backend.models.language_models import Language, Translation, UserLanguagePreference, TranslationKey
    from backend.models.version_models import DocumentVersion, ApprovalWorkflow, AuditLog, ChangeRequest
    from backend.models.artifact_models import (
        NonConformity, CorrectiveAction, InternalAudit,
        ManagementReview, TrainingRecord, CustomerComplaint
    )
    
    Base.metadata.create_all(bind=engine)
