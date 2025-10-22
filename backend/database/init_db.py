"""
Database Initialization for Multi-ISO Platform
Phase 2: Universal ISO data model setup
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.models.iso_models import Base, ISOStandard, ISOClause, StandardTemplate, Workspace
from config.settings import settings
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database(drop_existing: bool = False):
    """
    Initialize the database with universal ISO models
    
    Args:
        drop_existing: If True, drops all existing tables first (CAUTION!)
    """
    logger.info("🗄️  Initializing Multi-ISO Platform Database...")
    
    # Create engine
    engine = create_engine(settings.DATABASE_URL, echo=True)
    
    # Drop existing tables if requested
    if drop_existing:
        logger.warning("⚠️  Dropping existing tables...")
        Base.metadata.drop_all(engine)
        logger.info("✅ Existing tables dropped")
    
    # Create all tables
    logger.info("📊 Creating database tables...")
    Base.metadata.create_all(engine)
    logger.info("✅ Database tables created successfully!")
    
    # Log created tables
    logger.info("\n📋 Created tables:")
    for table in Base.metadata.sorted_tables:
        logger.info(f"   - {table.name}")
    
    return engine


def get_session():
    """Get database session"""
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    return Session()


if __name__ == "__main__":
    import sys
    
    # Check for --drop flag
    drop = "--drop" in sys.argv
    
    if drop:
        confirm = input("⚠️  This will DROP all existing tables. Type 'yes' to confirm: ")
        if confirm.lower() != "yes":
            print("Aborted.")
            sys.exit(0)
    
    # Initialize database
    engine = init_database(drop_existing=drop)
    logger.info("\n✅ Database initialization complete!")
    logger.info(f"📍 Database URL: {settings.DATABASE_URL}")
