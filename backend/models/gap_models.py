"""
Gap Analysis Models
Supports AI-powered document analysis and compliance gap identification
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from backend.models.user_models import Base


class AnalysisStatus(enum.Enum):
    """Status of gap analysis"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GapSeverity(enum.Enum):
    """Severity level of identified gaps"""
    CRITICAL = "critical"  # Missing mandatory requirement
    MAJOR = "major"        # Significant gap affecting compliance
    MINOR = "minor"        # Small gap or improvement opportunity
    OBSERVATION = "observation"  # Note for improvement


class RoadmapItemStatus(enum.Enum):
    """Status of roadmap implementation items"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ON_HOLD = "on_hold"


class GapAnalysis(Base):
    """Main gap analysis record"""
    __tablename__ = "gap_analyses"
    
    id = Column(String(36), primary_key=True)
    analysis_number = Column(String(50), unique=True, nullable=False, index=True)  # GA-2024-001
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    
    # Document Information
    document_name = Column(String(500), nullable=False)
    document_path = Column(String(1000))  # Path to uploaded document
    document_type = Column(String(50))  # PDF, DOCX, TXT
    file_size = Column(Integer)  # Size in bytes
    
    # ISO Standard Reference
    iso_standard_id = Column(String(36), ForeignKey("iso_standards.id"), nullable=False)
    iso_version = Column(String(50))  # e.g., "2015"
    
    # Analysis Status
    status = Column(SQLEnum(AnalysisStatus), default=AnalysisStatus.PENDING, nullable=False, index=True)
    progress_percent = Column(Integer, default=0)  # 0-100
    
    # Analysis Results Summary
    total_requirements = Column(Integer, default=0)
    total_gaps = Column(Integer, default=0)
    critical_gaps = Column(Integer, default=0)
    major_gaps = Column(Integer, default=0)
    minor_gaps = Column(Integer, default=0)
    observations = Column(Integer, default=0)
    
    # Compliance Scoring
    compliance_score = Column(Float)  # 0-100
    coverage_percent = Column(Float)  # Percentage of requirements with evidence
    
    # AI Analysis Metadata
    ai_model_used = Column(String(100))  # e.g., "gpt-4-turbo"
    analysis_tokens = Column(Integer)  # Total tokens used
    analysis_duration = Column(Integer)  # Seconds
    
    # Text Content (extracted from document)
    extracted_text = Column(Text)  # Full text extracted from document
    text_length = Column(Integer)  # Character count
    
    # Error Information
    error_message = Column(Text)  # If analysis failed
    
    # User & Timestamps
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    
    # Relationships
    gaps = relationship("Gap", back_populates="analysis", cascade="all, delete-orphan")
    roadmap_items = relationship("RoadmapItem", back_populates="analysis", cascade="all, delete-orphan")


class Gap(Base):
    """Individual compliance gap identified in analysis"""
    __tablename__ = "gaps"
    
    id = Column(String(36), primary_key=True)
    analysis_id = Column(String(36), ForeignKey("gap_analyses.id"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    
    # ISO Requirement Reference
    iso_clause = Column(String(50), nullable=False)  # e.g., "4.4.2"
    iso_clause_title = Column(String(500))
    iso_requirement = Column(Text)  # Full text of ISO requirement
    
    # Gap Details
    severity = Column(SQLEnum(GapSeverity), nullable=False, index=True)
    gap_description = Column(Text, nullable=False)  # What is missing/inadequate
    current_state = Column(Text)  # What exists currently
    required_state = Column(Text)  # What should exist per ISO
    
    # Impact Assessment
    impact_description = Column(Text)  # Business/compliance impact
    risk_level = Column(String(20))  # low, medium, high, critical
    
    # Evidence
    evidence_found = Column(Text)  # Text excerpts that partially address requirement
    evidence_score = Column(Float)  # 0-100, how much evidence exists
    
    # AI Analysis
    ai_confidence = Column(Float)  # 0-1, AI's confidence in gap identification
    ai_reasoning = Column(Text)  # Why AI identified this as a gap
    
    # Remediation Guidance
    recommended_action = Column(Text)  # What to do to close gap
    implementation_effort = Column(String(20))  # low, medium, high
    estimated_cost = Column(Float)
    estimated_hours = Column(Float)
    priority_score = Column(Integer)  # 1-10, based on severity × impact
    
    # Relationships to other artifacts
    related_nc_id = Column(String(36), ForeignKey("non_conformities.id"))
    related_ca_id = Column(String(36), ForeignKey("corrective_actions.id"))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analysis = relationship("GapAnalysis", back_populates="gaps")
    evidence_items = relationship("ComplianceEvidence", back_populates="gap", cascade="all, delete-orphan")


class ComplianceEvidence(Base):
    """Evidence supporting compliance (or lack thereof)"""
    __tablename__ = "compliance_evidence"
    
    id = Column(String(36), primary_key=True)
    gap_id = Column(String(36), ForeignKey("gaps.id"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    
    # Evidence Details
    evidence_type = Column(String(100))  # document, procedure, record, observation
    evidence_text = Column(Text)  # Actual text/content
    source_document = Column(String(500))  # Which document it came from
    page_number = Column(Integer)
    
    # Analysis
    relevance_score = Column(Float)  # 0-1, how relevant to requirement
    adequacy_score = Column(Float)  # 0-1, how well it addresses requirement
    ai_extracted = Column(String(1), default='Y')  # Y/N, was this found by AI
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    gap = relationship("Gap", back_populates="evidence_items")


class RoadmapItem(Base):
    """Implementation roadmap items for closing gaps"""
    __tablename__ = "roadmap_items"
    
    id = Column(String(36), primary_key=True)
    analysis_id = Column(String(36), ForeignKey("gap_analyses.id"), nullable=False, index=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    
    # Roadmap Item Details
    item_number = Column(String(50))  # RI-001, RI-002
    title = Column(String(500), nullable=False)
    description = Column(Text)
    
    # Priority & Effort
    priority = Column(Integer)  # 1-10
    impact = Column(String(20))  # low, medium, high, critical
    effort = Column(String(20))  # low, medium, high
    complexity = Column(String(20))  # simple, moderate, complex
    
    # Resource Estimates
    estimated_cost = Column(Float)
    estimated_hours = Column(Float)
    estimated_duration_days = Column(Integer)
    
    # Dependencies
    dependencies = Column(JSON)  # Array of roadmap_item_ids that must be completed first
    blocks = Column(JSON)  # Array of roadmap_item_ids that depend on this
    
    # Assignment
    assigned_to = Column(String(36), ForeignKey("users.id"))
    responsible_department = Column(String(200))
    
    # Status & Progress
    status = Column(SQLEnum(RoadmapItemStatus), default=RoadmapItemStatus.NOT_STARTED, nullable=False)
    progress_percent = Column(Integer, default=0)  # 0-100
    
    # Milestones & Dates
    milestone = Column(String(200))  # e.g., "Phase 1: Documentation", "Phase 2: Training"
    planned_start_date = Column(DateTime)
    planned_completion_date = Column(DateTime)
    actual_start_date = Column(DateTime)
    actual_completion_date = Column(DateTime)
    
    # Gap References
    gap_ids = Column(JSON)  # Array of gap_ids this item addresses
    gap_count = Column(Integer, default=0)  # Number of gaps this closes
    
    # Deliverables
    deliverables = Column(JSON)  # Array of expected deliverables
    completion_criteria = Column(Text)
    
    # Notes
    notes = Column(Text)
    risks = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    analysis = relationship("GapAnalysis", back_populates="roadmap_items")
