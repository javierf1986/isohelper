"""
Language Models
Phase 4: Multi-language Support

Database models for internationalization and translation management.
"""
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Language(Base):
    """Supported languages in the system"""
    __tablename__ = "languages"
    
    code = Column(String(10), primary_key=True)  # e.g., 'en', 'es', 'fr'
    name = Column(String(100), nullable=False)  # e.g., 'English', 'Español'
    native_name = Column(String(100), nullable=False)  # e.g., 'English', 'Español'
    is_active = Column(Boolean, default=True)
    is_rtl = Column(Boolean, default=False)  # Right-to-left languages
    flag_emoji = Column(String(10))  # e.g., '🇺🇸', '🇪🇸'
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    translations = relationship("Translation", back_populates="language")
    user_preferences = relationship("UserLanguagePreference", back_populates="language")


class TranslationKey(Base):
    """Translation keys for system strings"""
    __tablename__ = "translation_keys"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String(255), unique=True, nullable=False)  # e.g., 'dashboard.welcome'
    category = Column(String(50))  # e.g., 'ui', 'email', 'clause'
    default_text = Column(Text, nullable=False)  # Default English text
    description = Column(Text)  # Context for translators
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    translations = relationship("Translation", back_populates="key")


class Translation(Base):
    """Translations for different languages"""
    __tablename__ = "translations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key_id = Column(String(36), ForeignKey("translation_keys.id"), nullable=False)
    language_code = Column(String(10), ForeignKey("languages.code"), nullable=False)
    translated_text = Column(Text, nullable=False)
    is_verified = Column(Boolean, default=False)  # Reviewed by native speaker
    translated_by = Column(String(36), ForeignKey("users.id"))
    translated_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    key = relationship("TranslationKey", back_populates="translations")
    language = relationship("Language", back_populates="translations")


class ISOClauseTranslation(Base):
    """Translations for ISO clause content"""
    __tablename__ = "iso_clause_translations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    clause_id = Column(String(50), ForeignKey("iso_clauses.id"), nullable=False)
    language_code = Column(String(10), ForeignKey("languages.code"), nullable=False)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    content = Column(Text, nullable=False)
    requirements = Column(JSON)  # Translated requirements list
    translated_by = Column(String(36), ForeignKey("users.id"))
    is_official = Column(Boolean, default=False)  # Official ISO translation
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    clause = relationship("ISOClause")
    language = relationship("Language")


class UserLanguagePreference(Base):
    """User language preferences"""
    __tablename__ = "user_language_preferences"
    
    user_id = Column(String(36), ForeignKey("users.id"), primary_key=True)
    language_code = Column(String(10), ForeignKey("languages.code"), nullable=False)
    date_format = Column(String(20), default="MM/DD/YYYY")
    time_format = Column(String(10), default="12h")  # '12h' or '24h'
    timezone = Column(String(50), default="UTC")
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User")
    language = relationship("Language", back_populates="user_preferences")
