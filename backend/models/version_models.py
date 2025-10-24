"""
Version Control Models
Models for document versioning, approval workflows, and audit logging
"""

from sqlalchemy import Column, String, Integer, DateTime, Text, Boolean, ForeignKey, JSON, Enum as SQLEnum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import enum
from .user_models import Base


class VersionStatus(str, enum.Enum):
    """Version status enumeration"""
    DRAFT = "draft"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    ARCHIVED = "archived"


class ApprovalStatus(str, enum.Enum):
    """Approval status enumeration"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CANCELLED = "cancelled"


class ChangeType(str, enum.Enum):
    """Change type enumeration"""
    MINOR = "minor"
    MAJOR = "major"
    CRITICAL = "critical"


class DocumentVersion(Base):
    """
    Document Version Model
    Tracks all versions of generated documents with content hashing and diff storage
    """
    __tablename__ = "document_versions"

    id = Column(String, primary_key=True)
    document_id = Column(String, nullable=False, index=True)  # Reference to original document
    version_number = Column(Integer, nullable=False)  # Sequential version number
    version_label = Column(String, nullable=True)  # e.g., "v1.0", "v1.1", "v2.0"
    
    # Version metadata
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)  # Full document content
    content_hash = Column(String(64), nullable=False)  # SHA-256 hash for integrity
    content_diff = Column(JSON, nullable=True)  # JSON diff from previous version
    
    # Status and type
    status = Column(SQLEnum(VersionStatus), default=VersionStatus.DRAFT, nullable=False)
    change_type = Column(SQLEnum(ChangeType), default=ChangeType.MINOR, nullable=False)
    change_summary = Column(Text, nullable=True)  # Description of changes
    
    # Multi-tenant and user tracking
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    created_by = Column(String, ForeignKey("users.id"), nullable=False)
    approved_by = Column(String, ForeignKey("users.id"), nullable=True)
    approved_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # ISO standard reference
    iso_standard_id = Column(String, nullable=True)
    
    # Relationships
    workspace = relationship("Workspace", back_populates="document_versions")
    creator = relationship("User", foreign_keys=[created_by])
    approver = relationship("User", foreign_keys=[approved_by])
    approval_workflows = relationship("ApprovalWorkflow", back_populates="document_version", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="document_version", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<DocumentVersion(id={self.id}, document_id={self.document_id}, version={self.version_number}, status={self.status})>"


class ApprovalWorkflow(Base):
    """
    Approval Workflow Model
    Multi-step approval process for document versions
    """
    __tablename__ = "approval_workflows"

    id = Column(String, primary_key=True)
    version_id = Column(String, ForeignKey("document_versions.id"), nullable=False, index=True)
    
    # Workflow metadata
    workflow_name = Column(String, nullable=False)  # e.g., "Quality Manager Review", "Director Approval"
    step_order = Column(Integer, nullable=False)  # Sequential step number
    
    # Approver info
    approver_id = Column(String, ForeignKey("users.id"), nullable=False)
    approver_role = Column(String, nullable=True)  # Required role for approval
    
    # Status and decision
    status = Column(SQLEnum(ApprovalStatus), default=ApprovalStatus.PENDING, nullable=False)
    decision_comment = Column(Text, nullable=True)
    decided_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Multi-tenant
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    
    # Relationships
    document_version = relationship("DocumentVersion", back_populates="approval_workflows")
    approver = relationship("User")
    workspace = relationship("Workspace", back_populates="approval_workflows")
    
    def __repr__(self):
        return f"<ApprovalWorkflow(id={self.id}, version_id={self.version_id}, status={self.status}, step={self.step_order})>"


class AuditLog(Base):
    """
    Audit Log Model
    Complete audit trail for all version-related activities
    """
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True)
    version_id = Column(String, ForeignKey("document_versions.id"), nullable=False, index=True)
    
    # Action details
    action = Column(String, nullable=False)  # e.g., "created", "approved", "rejected", "rollback"
    action_description = Column(Text, nullable=True)
    actor_id = Column(String, ForeignKey("users.id"), nullable=False)
    
    # Changes tracked
    changes_made = Column(JSON, nullable=True)  # JSON object with change details
    extra_metadata = Column(JSON, nullable=True)  # Additional metadata (renamed from metadata to avoid SQLAlchemy conflict)
    
    # IP and session tracking
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
    
    # Timestamp
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    
    # Multi-tenant
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    
    # Relationships
    document_version = relationship("DocumentVersion", back_populates="audit_logs")
    actor = relationship("User")
    workspace = relationship("Workspace", back_populates="audit_logs")
    
    def __repr__(self):
        return f"<AuditLog(id={self.id}, action={self.action}, actor_id={self.actor_id}, created_at={self.created_at})>"


class ChangeRequest(Base):
    """
    Change Request Model
    Formal requests for document changes before version creation
    """
    __tablename__ = "change_requests"

    id = Column(String, primary_key=True)
    document_id = Column(String, nullable=False, index=True)
    
    # Request details
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    justification = Column(Text, nullable=True)
    change_type = Column(SQLEnum(ChangeType), default=ChangeType.MINOR, nullable=False)
    
    # Status
    status = Column(String, nullable=False, default="open")  # open, approved, rejected, implemented
    priority = Column(String, nullable=True)  # low, medium, high, critical
    
    # People involved
    requester_id = Column(String, ForeignKey("users.id"), nullable=False)
    assigned_to = Column(String, ForeignKey("users.id"), nullable=True)
    approved_by = Column(String, ForeignKey("users.id"), nullable=True)
    
    # Dates
    requested_date = Column(DateTime, server_default=func.now(), nullable=False)
    target_implementation_date = Column(DateTime, nullable=True)
    implemented_date = Column(DateTime, nullable=True)
    
    # Version link (once implemented)
    implemented_version_id = Column(String, ForeignKey("document_versions.id"), nullable=True)
    
    # Multi-tenant
    workspace_id = Column(String, ForeignKey("workspaces.id"), nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    requester = relationship("User", foreign_keys=[requester_id])
    assignee = relationship("User", foreign_keys=[assigned_to])
    approver = relationship("User", foreign_keys=[approved_by])
    implemented_version = relationship("DocumentVersion", foreign_keys=[implemented_version_id])
    workspace = relationship("Workspace", back_populates="change_requests")
    
    def __repr__(self):
        return f"<ChangeRequest(id={self.id}, title={self.title}, status={self.status})>"
