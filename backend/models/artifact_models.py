"""
Artifact Models for Compliance Management
Phase 4.3: NC, CA, Audits, Management Reviews, Training, Customer Complaints
"""
import enum
from datetime import datetime, date
from sqlalchemy import (
    Column, String, Integer, Float, Boolean, Date, DateTime,
    Text, ForeignKey, Enum as SQLEnum
)
from backend.database.base import Base


# ===== Enums =====

class NCStatus(str, enum.Enum):
    """Non-Conformity Status"""
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    VERIFIED = "verified"
    CLOSED = "closed"


class NCSeverity(str, enum.Enum):
    """Non-Conformity Severity"""
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class CAStatus(str, enum.Enum):
    """Corrective Action Status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    EFFECTIVE = "effective"
    NOT_EFFECTIVE = "not_effective"


class AuditType(str, enum.Enum):
    """Internal Audit Type"""
    PROCESS = "process"
    PRODUCT = "product"
    SYSTEM = "system"
    COMPLIANCE = "compliance"


class AuditStatus(str, enum.Enum):
    """Audit Status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    REPORT_ISSUED = "report_issued"


# ===== Models =====

class NonConformity(Base):
    """Track quality issues and deviations"""
    __tablename__ = "non_conformities"
    
    id = Column(String(36), primary_key=True)
    nc_number = Column(String(50), unique=True, nullable=False, index=True)  # NC-2024-001
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    
    # Basic Information
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    detected_date = Column(Date, nullable=False, index=True)
    detected_location = Column(String(255))
    
    # Classification
    severity = Column(SQLEnum(NCSeverity), nullable=False, index=True)
    status = Column(SQLEnum(NCStatus), nullable=False, default=NCStatus.OPEN, index=True)
    category = Column(String(100), index=True)  # e.g., "Product Quality", "Process", "Documentation"
    
    # ISO Reference
    iso_standard_id = Column(String(36), ForeignKey("iso_standards.id"))
    iso_clause_number = Column(String(20))
    
    # Root Cause Analysis
    root_cause = Column(Text)
    contributing_factors = Column(Text)  # JSON array
    ai_root_cause_analysis = Column(Text)  # AI-generated insights
    
    # Impact Assessment
    impact_description = Column(Text)
    potential_cost = Column(Float)
    customer_affected = Column(Boolean, default=False)
    
    # Assignment & Tracking
    reported_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    assigned_to = Column(String(36), ForeignKey("users.id"))
    verified_by = Column(String(36), ForeignKey("users.id"))
    
    # Dates
    target_closure_date = Column(Date)
    actual_closure_date = Column(Date)
    verified_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CorrectiveAction(Base):
    """Actions to eliminate causes of non-conformities"""
    __tablename__ = "corrective_actions"
    
    id = Column(String(36), primary_key=True)
    ca_number = Column(String(50), unique=True, nullable=False, index=True)  # CA-2024-001
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    nc_id = Column(String(36), ForeignKey("non_conformities.id"), index=True)
    
    # Basic Information
    title = Column(String(500), nullable=False)
    description = Column(Text, nullable=False)
    action_plan = Column(Text, nullable=False)
    ai_generated_plan = Column(Text)  # AI-suggested action plan
    
    # Status & Priority
    status = Column(SQLEnum(CAStatus), nullable=False, default=CAStatus.PLANNED, index=True)
    priority = Column(String(20), default="medium")  # low, medium, high, urgent
    
    # Assignment
    assigned_to = Column(String(36), ForeignKey("users.id"), nullable=False)
    verified_by = Column(String(36), ForeignKey("users.id"))
    
    # Planning
    planned_start_date = Column(Date, nullable=False)
    planned_completion_date = Column(Date, nullable=False, index=True)
    actual_start_date = Column(Date)
    actual_completion_date = Column(Date)
    
    # Resource Tracking
    estimated_cost = Column(Float)
    actual_cost = Column(Float)
    estimated_hours = Column(Float)
    actual_hours = Column(Float)
    
    # Effectiveness Verification
    effectiveness_check_date = Column(Date)
    effectiveness_criteria = Column(Text)
    effectiveness_results = Column(Text)
    is_effective = Column(Boolean)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class InternalAudit(Base):
    """Internal audit schedule and findings"""
    __tablename__ = "internal_audits"
    
    id = Column(String(36), primary_key=True)
    audit_number = Column(String(50), unique=True, nullable=False, index=True)  # AUDIT-2024-Q1-01
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    
    # Basic Information
    title = Column(String(500), nullable=False)
    audit_type = Column(SQLEnum(AuditType), nullable=False)
    status = Column(SQLEnum(AuditStatus), nullable=False, default=AuditStatus.PLANNED, index=True)
    
    # Scope
    scope_description = Column(Text, nullable=False)
    iso_standard_id = Column(String(36), ForeignKey("iso_standards.id"))
    clauses_covered = Column(Text)  # JSON array of clause numbers
    departments = Column(Text)  # JSON array
    
    # Schedule
    planned_date = Column(Date, nullable=False, index=True)
    actual_date = Column(Date)
    duration_hours = Column(Float)
    
    # Team
    lead_auditor = Column(String(36), ForeignKey("users.id"), nullable=False)
    auditors = Column(Text)  # JSON array of user IDs
    auditees = Column(Text)  # JSON array of auditee names/positions
    
    # Findings
    major_findings = Column(Integer, default=0)
    minor_findings = Column(Integer, default=0)
    observations = Column(Integer, default=0)
    findings_summary = Column(Text)
    
    # Documentation
    report_path = Column(String(1000))
    report_issued_date = Column(Date)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ManagementReview(Base):
    """Management review meetings and decisions"""
    __tablename__ = "management_reviews"
    
    id = Column(String(36), primary_key=True)
    review_number = Column(String(50), unique=True, nullable=False, index=True)  # MR-2024-Q1
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    
    # Basic Information
    title = Column(String(500), nullable=False)
    review_date = Column(Date, nullable=False, index=True)
    duration_hours = Column(Float)
    
    # Participants
    chairman = Column(String(36), ForeignKey("users.id"), nullable=False)
    attendees = Column(Text)  # JSON array of user IDs and names
    
    # Agenda & Topics
    agenda = Column(Text)  # JSON array of agenda items
    qms_performance = Column(Text)  # QMS performance review
    nc_ca_status = Column(Text)  # NC/CA status summary
    audit_results = Column(Text)  # Internal/external audit results
    customer_feedback = Column(Text)  # Customer satisfaction data
    resource_adequacy = Column(Text)  # Resource evaluation
    improvement_opportunities = Column(Text)  # Continual improvement
    
    # Outputs
    decisions = Column(Text)  # JSON array of decisions
    action_items = Column(Text)  # JSON array of action items
    
    # Documentation
    minutes_path = Column(String(1000))
    minutes_approved = Column(Boolean, default=False)
    approved_by = Column(String(36), ForeignKey("users.id"))
    approved_at = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TrainingRecord(Base):
    """Employee training and competency tracking"""
    __tablename__ = "training_records"
    
    id = Column(String(36), primary_key=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    employee_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Training Information
    training_title = Column(String(500), nullable=False)
    training_type = Column(String(100))  # Internal, External, On-the-job, E-learning
    training_provider = Column(String(255))
    training_location = Column(String(255))
    
    # Schedule
    training_date = Column(Date, nullable=False, index=True)
    duration_hours = Column(Float)
    
    # Competency
    competency_area = Column(String(255))
    skills_covered = Column(Text)  # JSON array
    
    # Assessment
    assessment_required = Column(Boolean, default=False)
    assessment_score = Column(Float)
    passing_score = Column(Float)
    passed = Column(Boolean)
    
    # Certification
    certificate_number = Column(String(100))
    certificate_path = Column(String(1000))
    valid_from = Column(Date)
    valid_until = Column(Date)
    
    # ISO Reference
    iso_clause_reference = Column(String(50))  # e.g., "7.2 Competence"
    
    # Notes
    notes = Column(Text)
    trainer_name = Column(String(255))
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class CustomerComplaint(Base):
    """Customer complaint tracking and resolution"""
    __tablename__ = "customer_complaints"
    
    id = Column(String(36), primary_key=True)
    complaint_number = Column(String(50), unique=True, nullable=False, index=True)  # CC-2024-001
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    
    # Customer & Product
    customer_name = Column(String(255), nullable=False, index=True)
    customer_contact = Column(String(255))
    product_service = Column(String(255))
    order_number = Column(String(100))
    
    # Complaint Details
    complaint_date = Column(Date, nullable=False, index=True)
    complaint_description = Column(Text, nullable=False)
    complaint_category = Column(String(100))  # Product Quality, Delivery, Service, etc.
    severity = Column(SQLEnum(NCSeverity), nullable=False)
    
    # Investigation
    investigation_findings = Column(Text)
    root_cause = Column(Text)
    related_nc_id = Column(String(36), ForeignKey("non_conformities.id"))
    related_ca_id = Column(String(36), ForeignKey("corrective_actions.id"))
    
    # Resolution
    resolution_description = Column(Text)
    resolution_date = Column(Date)
    immediate_action = Column(Text)
    preventive_action = Column(Text)
    
    # Customer Response
    customer_notification_date = Column(Date)
    customer_satisfaction = Column(String(50))  # satisfied, neutral, unsatisfied
    customer_feedback = Column(Text)
    
    # Assignment
    assigned_to = Column(String(36), ForeignKey("users.id"))
    resolved_by = Column(String(36), ForeignKey("users.id"))
    
    # Dates
    target_resolution_date = Column(Date)
    actual_resolution_date = Column(Date)
    
    # Status
    status = Column(String(20), default="open", index=True)  # open, investigating, resolved, closed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
