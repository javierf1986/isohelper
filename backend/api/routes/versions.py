"""
Document Version Control API Routes
Endpoints for version management, approvals, and audit trails
"""

from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from backend.database.database import get_db
from backend.models.user_models import User
from backend.models.version_models import VersionStatus, ChangeType
from backend.services.version_service import VersionService
from backend.api.dependencies import get_current_user

router = APIRouter(prefix="/api/v1/versions", tags=["versions"])


# ===== Request/Response Models =====

class VersionCreateRequest(BaseModel):
    """Request model for creating a new version"""
    document_id: str
    title: str
    content: str
    change_type: ChangeType = Field(default=ChangeType.MINOR)
    change_summary: Optional[str] = None
    iso_standard_id: Optional[str] = None


class VersionResponse(BaseModel):
    """Response model for version data"""
    id: str
    document_id: str
    version_number: int
    version_label: str
    title: str
    status: str
    change_type: str
    change_summary: Optional[str]
    content_hash: str
    created_by: str
    approved_by: Optional[str]
    approved_at: Optional[str]
    created_at: str
    updated_at: str
    iso_standard_id: Optional[str]
    
    class Config:
        from_attributes = True


class VersionDetailResponse(VersionResponse):
    """Detailed version response with content"""
    content: str
    content_diff: Optional[dict]


class ApprovalRequest(BaseModel):
    """Request for version approval"""
    comment: Optional[str] = None


class RejectionRequest(BaseModel):
    """Request for version rejection"""
    reason: str


class RollbackRequest(BaseModel):
    """Request for version rollback"""
    reason: str


class CompareRequest(BaseModel):
    """Request to compare two versions"""
    version_id_1: str
    version_id_2: str


class AuditLogResponse(BaseModel):
    """Response model for audit log entries"""
    id: str
    version_id: str
    action: str
    action_description: Optional[str]
    actor_id: str
    changes_made: Optional[dict]
    metadata: Optional[dict]
    created_at: str
    
    class Config:
        from_attributes = True


# ===== Version Management Endpoints =====

@router.post("/", response_model=VersionDetailResponse, status_code=status.HTTP_201_CREATED)
async def create_version(
    request: VersionCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new document version
    
    - Automatically calculates version number, hash, and diff
    - Creates audit log entry
    - Returns complete version details
    """
    try:
        version = VersionService.create_version(
            db=db,
            document_id=request.document_id,
            title=request.title,
            content=request.content,
            workspace_id=current_user.workspace_id,
            created_by=current_user.id,
            change_type=request.change_type,
            change_summary=request.change_summary,
            iso_standard_id=request.iso_standard_id
        )
        
        return VersionDetailResponse(
            id=version.id,
            document_id=version.document_id,
            version_number=version.version_number,
            version_label=version.version_label,
            title=version.title,
            content=version.content,
            status=version.status.value,
            change_type=version.change_type.value,
            change_summary=version.change_summary,
            content_hash=version.content_hash,
            content_diff=version.content_diff,
            created_by=version.created_by,
            approved_by=version.approved_by,
            approved_at=version.approved_at.isoformat() if version.approved_at else None,
            created_at=version.created_at.isoformat(),
            updated_at=version.updated_at.isoformat(),
            iso_standard_id=version.iso_standard_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create version: {str(e)}"
        )


@router.get("/document/{document_id}", response_model=List[VersionResponse])
async def get_document_versions(
    document_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all versions for a specific document
    
    - Returns versions in descending order (newest first)
    - Limited to workspace access
    """
    versions = VersionService.get_document_versions(
        db=db,
        document_id=document_id,
        workspace_id=current_user.workspace_id,
        limit=limit
    )
    
    return [
        VersionResponse(
            id=v.id,
            document_id=v.document_id,
            version_number=v.version_number,
            version_label=v.version_label,
            title=v.title,
            status=v.status.value,
            change_type=v.change_type.value,
            change_summary=v.change_summary,
            content_hash=v.content_hash,
            created_by=v.created_by,
            approved_by=v.approved_by,
            approved_at=v.approved_at.isoformat() if v.approved_at else None,
            created_at=v.created_at.isoformat(),
            updated_at=v.updated_at.isoformat(),
            iso_standard_id=v.iso_standard_id
        )
        for v in versions
    ]


@router.get("/{version_id}", response_model=VersionDetailResponse)
async def get_version(
    version_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific version by ID
    
    - Includes full content and diff data
    """
    version = VersionService.get_version(
        db=db,
        version_id=version_id,
        workspace_id=current_user.workspace_id
    )
    
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Version {version_id} not found"
        )
    
    return VersionDetailResponse(
        id=version.id,
        document_id=version.document_id,
        version_number=version.version_number,
        version_label=version.version_label,
        title=version.title,
        content=version.content,
        status=version.status.value,
        change_type=version.change_type.value,
        change_summary=version.change_summary,
        content_hash=version.content_hash,
        content_diff=version.content_diff,
        created_by=version.created_by,
        approved_by=version.approved_by,
        approved_at=version.approved_at.isoformat() if version.approved_at else None,
        created_at=version.created_at.isoformat(),
        updated_at=version.updated_at.isoformat(),
        iso_standard_id=version.iso_standard_id
    )


# ===== Version Comparison =====

@router.post("/compare", response_model=dict)
async def compare_versions(
    request: CompareRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Compare two versions and return diff
    
    - Shows added, removed, and modified lines
    - Returns metadata for both versions
    """
    try:
        comparison = VersionService.compare_versions(
            db=db,
            version_id_1=request.version_id_1,
            version_id_2=request.version_id_2,
            workspace_id=current_user.workspace_id
        )
        return comparison
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ===== Approval Workflow =====

@router.post("/{version_id}/approve", response_model=VersionResponse)
async def approve_version(
    version_id: str,
    request: ApprovalRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Approve a version
    
    - Changes status to APPROVED
    - Records approver and timestamp
    - Creates audit log entry
    """
    try:
        version = VersionService.approve_version(
            db=db,
            version_id=version_id,
            approver_id=current_user.id,
            workspace_id=current_user.workspace_id,
            comment=request.comment
        )
        
        return VersionResponse(
            id=version.id,
            document_id=version.document_id,
            version_number=version.version_number,
            version_label=version.version_label,
            title=version.title,
            status=version.status.value,
            change_type=version.change_type.value,
            change_summary=version.change_summary,
            content_hash=version.content_hash,
            created_by=version.created_by,
            approved_by=version.approved_by,
            approved_at=version.approved_at.isoformat() if version.approved_at else None,
            created_at=version.created_at.isoformat(),
            updated_at=version.updated_at.isoformat(),
            iso_standard_id=version.iso_standard_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{version_id}/reject", response_model=VersionResponse)
async def reject_version(
    version_id: str,
    request: RejectionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Reject a version
    
    - Changes status to REJECTED
    - Records reason in audit log
    """
    try:
        version = VersionService.reject_version(
            db=db,
            version_id=version_id,
            rejector_id=current_user.id,
            workspace_id=current_user.workspace_id,
            reason=request.reason
        )
        
        return VersionResponse(
            id=version.id,
            document_id=version.document_id,
            version_number=version.version_number,
            version_label=version.version_label,
            title=version.title,
            status=version.status.value,
            change_type=version.change_type.value,
            change_summary=version.change_summary,
            content_hash=version.content_hash,
            created_by=version.created_by,
            approved_by=version.approved_by,
            approved_at=version.approved_at.isoformat() if version.approved_at else None,
            created_at=version.created_at.isoformat(),
            updated_at=version.updated_at.isoformat(),
            iso_standard_id=version.iso_standard_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


# ===== Version Rollback =====

@router.post("/{version_id}/rollback", response_model=VersionDetailResponse)
async def rollback_to_version(
    version_id: str,
    request: RollbackRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Rollback to a previous version
    
    - Creates a new version with old content
    - Preserves history (doesn't delete newer versions)
    - Records rollback in audit log
    """
    try:
        new_version = VersionService.rollback_to_version(
            db=db,
            version_id=version_id,
            user_id=current_user.id,
            workspace_id=current_user.workspace_id,
            reason=request.reason
        )
        
        return VersionDetailResponse(
            id=new_version.id,
            document_id=new_version.document_id,
            version_number=new_version.version_number,
            version_label=new_version.version_label,
            title=new_version.title,
            content=new_version.content,
            status=new_version.status.value,
            change_type=new_version.change_type.value,
            change_summary=new_version.change_summary,
            content_hash=new_version.content_hash,
            content_diff=new_version.content_diff,
            created_by=new_version.created_by,
            approved_by=new_version.approved_by,
            approved_at=new_version.approved_at.isoformat() if new_version.approved_at else None,
            created_at=new_version.created_at.isoformat(),
            updated_at=new_version.updated_at.isoformat(),
            iso_standard_id=new_version.iso_standard_id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


# ===== Audit Trail =====

@router.get("/{version_id}/audit-trail", response_model=List[AuditLogResponse])
async def get_audit_trail(
    version_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get complete audit trail for a version
    
    - Shows all actions (created, approved, rejected, rollback)
    - Includes actor information and timestamps
    - Ordered chronologically
    """
    logs = VersionService.get_audit_trail(
        db=db,
        version_id=version_id,
        workspace_id=current_user.workspace_id
    )
    
    return [
        AuditLogResponse(
            id=log.id,
            version_id=log.version_id,
            action=log.action,
            action_description=log.action_description,
            actor_id=log.actor_id,
            changes_made=log.changes_made,
            metadata=log.metadata,
            created_at=log.created_at.isoformat()
        )
        for log in logs
    ]
