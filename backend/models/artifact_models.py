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
from backend.models.iso_models import Base


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


class ObjectiveStatus(str, enum.Enum):
    """Quality Objective Status"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    ACHIEVED = "achieved"
    DELAYED = "delayed"
    CANCELLED = "cancelled"


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
    
    # Cost Tracking
    estimated_cost = Column(Float)  # Estimated audit cost
    actual_cost = Column(Float)  # Actual audit cost
    auditor_hours = Column(Float)  # Total auditor hours
    
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
    
    # Cost Tracking
    meeting_cost = Column(Float)  # Meeting facility/logistics cost
    preparation_hours = Column(Float)  # Total preparation hours
    
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
    
    # Employee Information (for training matrix)
    employee_name = Column(String(255))
    employee_number = Column(String(100))
    job_role = Column(String(255))  # For training matrix by role
    department = Column(String(255))
    
    # Training Information
    training_title = Column(String(500), nullable=False)
    training_type = Column(String(100))  # Internal, External, On-the-job, E-learning
    training_provider = Column(String(255))
    training_location = Column(String(255))
    
    # Schedule
    training_date = Column(Date, nullable=False, index=True)
    duration_hours = Column(Float)
    
    # Enhanced Expiry Tracking
    expiry_date = Column(Date, index=True)  # When training/certification expires
    reminder_sent = Column(Boolean, default=False)  # Track if expiry reminder sent
    
    # Competency
    competency_area = Column(String(255))
    skills_covered = Column(Text)  # JSON array
    competence_achieved = Column(Boolean, default=False)  # Was competence demonstrated?
    evaluation_method = Column(String(255))  # How competence was evaluated
    
    # Assessment
    assessment_required = Column(Boolean, default=False)
    assessment_score = Column(Float)
    evaluation_score = Column(Float)  # Overall evaluation score
    passing_score = Column(Float)
    passed = Column(Boolean)
    
    # Certification
    certificate_number = Column(String(100))
    certificate_path = Column(String(1000))
    valid_from = Column(Date)
    valid_until = Column(Date)
    
    # ISO Reference
    iso_clause_reference = Column(String(50))  # e.g., "7.2 Competence"
    
    # Cost Tracking
    training_cost = Column(Float)  # Total training cost
    instructor_fee = Column(Float)  # Instructor/trainer fee
    material_cost = Column(Float)  # Training materials cost
    venue_cost = Column(Float)  # Venue rental cost
    
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
    
    # Cost Tracking
    resolution_cost = Column(Float)  # Cost to resolve complaint
    compensation_amount = Column(Float)  # Compensation paid to customer
    investigation_hours = Column(Float)  # Investigation time
    
    # Assignment
    assigned_to = Column(String(36), ForeignKey("users.id"))
    resolved_by = Column(String(36), ForeignKey("users.id"))
    
    # Dates
    target_resolution_date = Column(Date)


class QualityObjective(Base):
    """Track quality objectives and their achievement (ISO 6.2)"""
    __tablename__ = "quality_objectives"
    
    id = Column(String(36), primary_key=True)
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    
    # Basic Information
    title = Column(String(500), nullable=False)
    description = Column(Text)
    objective_number = Column(String(50), unique=True, nullable=False, index=True)  # OBJ-2025-001
    
    # Measurement
    target_value = Column(String(255))  # e.g., "95% on-time delivery", "< 2% defect rate"
    current_value = Column(String(255))  # Current achievement
    unit_of_measure = Column(String(100))  # %, count, hours, etc.
    measurement_method = Column(Text)  # How to measure this objective
    measurement_frequency = Column(String(100))  # monthly, quarterly, annually
    
    # Status & Progress
    status = Column(SQLEnum(ObjectiveStatus), nullable=False, default=ObjectiveStatus.PLANNED, index=True)
    progress_percentage = Column(Float, default=0.0)  # 0-100
    
    # Responsibility
    responsible_person = Column(String(36), ForeignKey("users.id"), nullable=False)
    department = Column(String(255))
    
    # Timeline
    start_date = Column(Date)
    target_date = Column(Date, nullable=False, index=True)
    achieved_date = Column(Date)
    
    # ISO Context
    iso_standard_id = Column(String(36), ForeignKey("iso_standards.id"))
    related_clause = Column(String(20))  # e.g., "6.2.1", "9.1.1"
    
    # Linkages
    linked_processes = Column(Text)  # JSON array of process IDs
    linked_risks = Column(Text)  # JSON array of risk IDs
    
    # Evidence & Documentation
    evidence = Column(Text)  # JSON array of document references
    progress_notes = Column(Text)  # JSON array of progress updates with dates
    
    # Review
    last_review_date = Column(Date)
    next_review_date = Column(Date)
    review_comments = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class RequirementsReview(Base):
    """
    Product/Service Requirements Review Records
    ISO 8.2.3 - Review of requirements for products and services
    """
    __tablename__ = "requirements_reviews"
    
    id = Column(String(36), primary_key=True)
    review_number = Column(String(50), unique=True, nullable=False, index=True)  # RR-2024-001
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    
    # Customer & Contract Information
    customer_name = Column(String(255), nullable=False, index=True)
    customer_contact = Column(String(255))
    product_service_name = Column(String(500), nullable=False)
    contract_number = Column(String(100), index=True)
    order_number = Column(String(100))
    
    # Review Details
    review_date = Column(Date, nullable=False, index=True)
    reviewed_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    # Requirements
    customer_requirements = Column(Text, nullable=False)  # JSON or text description
    regulatory_requirements = Column(Text)  # Applicable legal/regulatory requirements
    statutory_requirements = Column(Text)  # Other statutory requirements
    delivery_requirements = Column(Text)  # Schedule, delivery dates, logistics
    
    # Organization Capability
    capability_to_meet = Column(Boolean, default=True)  # Can we meet requirements?
    capability_assessment = Column(Text)  # Assessment notes
    resource_availability = Column(Text)  # Resources needed and availability
    
    # Differences & Clarifications
    differences_from_previous = Column(Text)  # Differences from previous contracts
    unresolved_issues = Column(Text)  # Issues not resolved before contract acceptance
    clarifications_needed = Column(Text)  # Customer clarifications requested
    
    # Review Result
    review_result = Column(String(50), nullable=False)  # APPROVED, CONDITIONAL, REJECTED
    approval_conditions = Column(Text)  # Conditions if conditional approval
    rejection_reasons = Column(Text)  # Reasons if rejected
    
    # Participants
    review_participants = Column(Text)  # JSON array of participant names/roles
    customer_representative = Column(String(255))
    
    # Evidence & Documentation
    supporting_documents = Column(Text)  # JSON array of document references
    meeting_minutes = Column(Text)  # Meeting notes if review conducted in meeting
    
    # Follow-up
    follow_up_actions = Column(Text)  # JSON array of actions required
    contract_signed_date = Column(Date)
    
    # ISO Reference
    iso_standard_id = Column(String(36), ForeignKey("iso_standards.id"))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)


class QualityPolicy(Base):
    """
    Quality Policy Management with Versioning
    ISO 5.2 - Quality policy
    """
    __tablename__ = "quality_policies"
    
    id = Column(String(36), primary_key=True)
    policy_number = Column(String(50), unique=True, nullable=False, index=True)  # QP-001-v2
    workspace_id = Column(String(36), ForeignKey("workspaces.id"), nullable=False, index=True)
    
    # Version Control
    version = Column(String(20), nullable=False, index=True)  # v1.0, v2.0
    version_number = Column(Integer, nullable=False)  # Integer for sorting
    previous_version_id = Column(String(36), ForeignKey("quality_policies.id"))  # Link to previous version
    
    # Policy Content
    policy_title = Column(String(500), nullable=False)
    policy_statement = Column(Text, nullable=False)  # The actual policy text
    scope = Column(Text)  # Where this policy applies
    purpose = Column(Text)  # Why this policy exists
    
    # Commitments
    quality_commitments = Column(Text)  # JSON array of specific commitments
    customer_focus_commitment = Column(Text)
    improvement_commitment = Column(Text)
    compliance_commitment = Column(Text)
    
    # Responsibilities
    policy_owner = Column(String(36), ForeignKey("users.id"), nullable=False)
    department = Column(String(255))
    
    # Dates
    effective_date = Column(Date, nullable=False, index=True)
    review_date = Column(Date)  # Next scheduled review
    superseded_date = Column(Date)  # Date when replaced by new version
    
    # Approval
    approved_by = Column(String(36), ForeignKey("users.id"))  # Top management
    approval_date = Column(Date)
    approval_signature_path = Column(String(1000))  # Path to signed document
    
    # Communication & Awareness
    communication_plan = Column(Text)  # How policy will be communicated
    communicated_to = Column(Text)  # JSON array of communication records
    awareness_training_required = Column(Boolean, default=True)
    awareness_evidence = Column(Text)  # JSON array of evidence (training records, etc.)
    
    # Availability
    document_location = Column(String(1000))  # Where policy document is stored
    publicly_available = Column(Boolean, default=False)
    external_url = Column(String(500))  # URL if published externally
    
    # Change Management
    change_reason = Column(Text)  # Why this version was created
    changes_summary = Column(Text)  # Summary of changes from previous version
    impact_assessment = Column(Text)  # Assessment of impact of changes
    
    # Review History
    last_review_date = Column(Date)
    review_frequency_months = Column(Integer, default=12)  # How often to review
    review_notes = Column(Text)
    
    # Status
    status = Column(String(50), nullable=False, default="DRAFT")  # DRAFT, APPROVED, ACTIVE, SUPERSEDED, ARCHIVED
    
    # ISO Reference
    iso_standard_id = Column(String(36), ForeignKey("iso_standards.id"))
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_by = Column(String(36), ForeignKey("users.id"), nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)



    actual_resolution_date = Column(Date)
    
    # Status
    status = Column(String(20), default="open", index=True)  # open, investigating, resolved, closed
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
