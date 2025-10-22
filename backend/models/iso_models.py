"""
Universal ISO Standard Data Models
Phase 2: Multi-ISO Platform Core

Database models for any ISO standard (9001, 14001, 27001, 45001, etc.)
"""
from sqlalchemy import Column, String, Text, Integer, Boolean, DateTime, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Optional, List, Dict
from enum import Enum

Base = declarative_base()


class StandardCategory(str, Enum):
    """ISO standard categories"""
    QUALITY = "quality"              # ISO 9001
    ENVIRONMENTAL = "environmental"  # ISO 14001
    SECURITY = "security"            # ISO 27001
    SAFETY = "safety"                # ISO 45001
    ENERGY = "energy"                # ISO 50001
    FOOD_SAFETY = "food_safety"      # ISO 22000
    OTHER = "other"


class ClauseType(str, Enum):
    """Types of clauses within an ISO standard"""
    REQUIREMENT = "requirement"      # Must comply
    GUIDANCE = "guidance"            # Recommended practice
    INFORMATIVE = "informative"      # Background info
    NORMATIVE = "normative"          # Mandatory reference


# Many-to-many relationship table for workspace standards
workspace_standards = Table(
    'workspace_standards',
    Base.metadata,
    Column('workspace_id', String(50), ForeignKey('workspaces.id')),
    Column('standard_id', String(50), ForeignKey('iso_standards.id'))
)


class ISOStandard(Base):
    """
    Universal model for any ISO standard
    """
    __tablename__ = 'iso_standards'
    
    # Core identification
    id = Column(String(50), primary_key=True)  # e.g., "ISO-9001-2015"
    name = Column(String(200), nullable=False)  # e.g., "ISO 9001:2015"
    full_title = Column(Text)  # Full official title
    
    # Classification
    iso_number = Column(String(10), nullable=False, index=True)  # e.g., "9001"
    year = Column(Integer, nullable=False)  # e.g., 2015
    category = Column(String(50), nullable=False)  # StandardCategory enum
    
    # Metadata
    description = Column(Text)
    purpose = Column(Text)
    scope = Column(Text)
    keywords = Column(JSON)  # List of search keywords
    
    # Structure info
    total_clauses = Column(Integer, default=0)
    has_annexes = Column(Boolean, default=False)
    structure_levels = Column(Integer, default=3)  # How deep the clause hierarchy goes
    
    # Source tracking
    source_file = Column(String(500))  # Original uploaded file
    import_method = Column(String(50))  # manual, ai_import, template
    imported_by = Column(String(100))
    imported_at = Column(DateTime, default=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)
    is_template = Column(Boolean, default=False)  # Pre-configured template
    version = Column(String(20), default="1.0")
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    clauses = relationship("ISOClause", back_populates="standard", cascade="all, delete-orphan")
    templates = relationship("StandardTemplate", back_populates="standard")
    workspaces = relationship("Workspace", secondary=workspace_standards, back_populates="standards")
    
    def __repr__(self):
        return f"<ISOStandard {self.name}>"


class ISOClause(Base):
    """
    Individual clause within an ISO standard
    Supports hierarchical structure (e.g., 4.1, 4.1.1, 4.1.1.1)
    """
    __tablename__ = 'iso_clauses'
    
    # Core identification
    id = Column(String(50), primary_key=True)  # e.g., "ISO-9001-2015-4.1"
    standard_id = Column(String(50), ForeignKey('iso_standards.id'), nullable=False, index=True)
    
    # Clause structure
    clause_number = Column(String(20), nullable=False, index=True)  # e.g., "4.1", "4.1.1"
    parent_clause_id = Column(String(50), ForeignKey('iso_clauses.id'))  # For hierarchy
    level = Column(Integer, default=1)  # Depth in hierarchy (1, 2, 3, etc.)
    sequence = Column(Integer, default=0)  # Order within parent
    
    # Content
    title = Column(Text, nullable=False)
    content = Column(Text)  # Full clause text
    summary = Column(Text)  # AI-generated summary
    requirements = Column(JSON)  # List of specific requirements
    
    # Classification
    clause_type = Column(String(50), default="requirement")  # ClauseType enum
    is_mandatory = Column(Boolean, default=True)
    is_documentable = Column(Boolean, default=True)  # Requires documentation
    
    # Context
    keywords = Column(JSON)  # Search keywords for this clause
    related_clauses = Column(JSON)  # IDs of related clauses
    examples = Column(JSON)  # Industry examples
    
    # Template generation
    has_template = Column(Boolean, default=False)
    template_variables = Column(JSON)  # Variables needed for template
    
    # AI Enhancement
    embedding_vector = Column(JSON)  # Vector for semantic search
    ai_generated = Column(Boolean, default=False)
    ai_confidence = Column(Integer, default=0)  # 0-100
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    standard = relationship("ISOStandard", back_populates="clauses")
    parent_clause = relationship("ISOClause", remote_side=[id], backref="sub_clauses")
    templates = relationship("StandardTemplate", back_populates="clause")
    
    def __repr__(self):
        return f"<ISOClause {self.clause_number}: {self.title}>"


class StandardTemplate(Base):
    """
    Document template for an ISO clause
    Generated from clause requirements
    """
    __tablename__ = 'standard_templates'
    
    # Core identification
    id = Column(String(50), primary_key=True)
    standard_id = Column(String(50), ForeignKey('iso_standards.id'), nullable=False, index=True)
    clause_id = Column(String(50), ForeignKey('iso_clauses.id'), nullable=False, index=True)
    
    # Template info
    template_name = Column(String(200), nullable=False)
    template_path = Column(String(500))  # File path if stored as file
    template_content = Column(Text, nullable=False)  # Jinja2 template
    
    # Configuration
    variables = Column(JSON)  # {var_name: {type, description, required}}
    format = Column(String(50), default="markdown")  # markdown, html, docx
    category = Column(String(100))  # Process, Policy, Procedure, etc.
    
    # Metadata
    description = Column(Text)
    usage_notes = Column(Text)
    example_output = Column(Text)
    
    # Generation
    generation_method = Column(String(50))  # manual, ai_generated, imported
    generated_by = Column(String(100))
    ai_model = Column(String(100))  # Which AI model generated it
    
    # Status
    is_active = Column(Boolean, default=True)
    is_approved = Column(Boolean, default=False)
    version = Column(String(20), default="1.0")
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationships
    standard = relationship("ISOStandard", back_populates="templates")
    clause = relationship("ISOClause", back_populates="templates")
    
    def __repr__(self):
        return f"<StandardTemplate {self.template_name}>"


class Workspace(Base):
    """
    Client workspace - multi-tenant isolation
    Each client gets their own workspace with assigned ISO standards
    """
    __tablename__ = 'workspaces'
    
    # Core identification
    id = Column(String(50), primary_key=True)
    client_name = Column(String(200), nullable=False)
    
    # Company info
    industry = Column(String(100))
    company_size = Column(String(50))  # small, medium, large
    country = Column(String(100))
    description = Column(Text)
    
    # Configuration
    active_standards = Column(JSON)  # List of standard IDs
    settings = Column(JSON)  # Custom settings per workspace
    branding = Column(JSON)  # Logo, colors, etc.
    
    # Plan & Limits
    plan = Column(String(50), default="free")  # free, basic, premium, enterprise
    max_users = Column(Integer, default=5)
    max_documents = Column(Integer, default=100)
    ai_quota = Column(Integer, default=1000)  # AI requests per month
    
    # Status
    is_active = Column(Boolean, default=True)
    is_trial = Column(Boolean, default=False)
    trial_expires = Column(DateTime)
    
    # Contact
    contact_email = Column(String(200))
    contact_phone = Column(String(50))
    admin_user_id = Column(String(50))
    
    # Owner (Phase 3: Link to authenticated users)
    owner_id = Column(String(50), ForeignKey('users.id'), nullable=True, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    last_accessed = Column(DateTime)
    
    # Relationships
    standards = relationship("ISOStandard", secondary=workspace_standards, back_populates="workspaces")
    documents = relationship("GeneratedDocument", back_populates="workspace")
    owner = relationship("User", back_populates="workspaces")
    
    def __repr__(self):
        return f"<Workspace {self.client_name}>"


class GeneratedDocument(Base):
    """
    Track all generated documents per workspace
    """
    __tablename__ = 'generated_documents'
    
    # Core identification
    id = Column(String(50), primary_key=True)
    workspace_id = Column(String(50), ForeignKey('workspaces.id'), nullable=False, index=True)
    
    # Document info
    document_name = Column(String(500), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)  # bytes
    format = Column(String(50))  # markdown, pdf, docx
    
    # Generation details
    standard_id = Column(String(50), ForeignKey('iso_standards.id'))
    clauses_included = Column(JSON)  # List of clause numbers
    generation_time_ms = Column(Integer)
    
    # AI Enhancement
    ai_enhanced = Column(Boolean, default=False)
    ai_provider = Column(String(50))  # local, mistral, openai
    enhancement_level = Column(String(50))  # light, moderate, comprehensive
    
    # Status
    status = Column(String(50), default="completed")  # pending, completed, failed
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=func.now())
    accessed_at = Column(DateTime)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="documents")
    
    def __repr__(self):
        return f"<GeneratedDocument {self.document_name}>"
