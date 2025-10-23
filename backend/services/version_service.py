"""
Version Control Service
Business logic for document versioning, approvals, and audit logging
"""

import hashlib
import json
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, desc

from backend.models.version_models import (
    DocumentVersion, ApprovalWorkflow, AuditLog, ChangeRequest,
    VersionStatus, ApprovalStatus, ChangeType
)
from backend.models.user_models import User


class VersionService:
    """Service for document version management"""
    
    @staticmethod
    def _calculate_content_hash(content: str) -> str:
        """Calculate SHA-256 hash of content"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    @staticmethod
    def _calculate_diff(old_content: str, new_content: str) -> Dict[str, Any]:
        """
        Calculate simple diff between two content strings
        Returns a JSON-serializable diff structure
        """
        old_lines = old_content.split('\n')
        new_lines = new_content.split('\n')
        
        diff = {
            "changes": [],
            "added_lines": 0,
            "removed_lines": 0,
            "modified_lines": 0
        }
        
        # Simple line-by-line diff (can be enhanced with difflib)
        max_lines = max(len(old_lines), len(new_lines))
        for i in range(max_lines):
            old_line = old_lines[i] if i < len(old_lines) else None
            new_line = new_lines[i] if i < len(new_lines) else None
            
            if old_line is None and new_line is not None:
                diff["changes"].append({"type": "added", "line": i + 1, "content": new_line})
                diff["added_lines"] += 1
            elif new_line is None and old_line is not None:
                diff["changes"].append({"type": "removed", "line": i + 1, "content": old_line})
                diff["removed_lines"] += 1
            elif old_line != new_line:
                diff["changes"].append({
                    "type": "modified",
                    "line": i + 1,
                    "old": old_line,
                    "new": new_line
                })
                diff["modified_lines"] += 1
        
        return diff
    
    @staticmethod
    def create_version(
        db: Session,
        document_id: str,
        title: str,
        content: str,
        workspace_id: str,
        created_by: str,
        change_type: ChangeType = ChangeType.MINOR,
        change_summary: Optional[str] = None,
        iso_standard_id: Optional[str] = None
    ) -> DocumentVersion:
        """
        Create a new document version
        Automatically calculates hash, version number, and diff from previous version
        """
        import uuid
        
        # Get previous version
        previous_version = db.query(DocumentVersion).filter(
            and_(
                DocumentVersion.document_id == document_id,
                DocumentVersion.workspace_id == workspace_id
            )
        ).order_by(desc(DocumentVersion.version_number)).first()
        
        # Calculate version number
        version_number = 1 if not previous_version else previous_version.version_number + 1
        
        # Calculate content hash
        content_hash = VersionService._calculate_content_hash(content)
        
        # Calculate diff if there's a previous version
        content_diff = None
        if previous_version:
            content_diff = VersionService._calculate_diff(previous_version.content, content)
        
        # Generate version label
        if change_type == ChangeType.MAJOR:
            version_label = f"v{version_number}.0"
        elif change_type == ChangeType.CRITICAL:
            version_label = f"v{version_number}.0-critical"
        else:
            version_label = f"v{version_number}.{0 if not previous_version else version_number}"
        
        # Create version
        version = DocumentVersion(
            id=str(uuid.uuid4()),
            document_id=document_id,
            version_number=version_number,
            version_label=version_label,
            title=title,
            content=content,
            content_hash=content_hash,
            content_diff=content_diff,
            status=VersionStatus.DRAFT,
            change_type=change_type,
            change_summary=change_summary,
            workspace_id=workspace_id,
            created_by=created_by,
            iso_standard_id=iso_standard_id
        )
        
        db.add(version)
        db.commit()
        db.refresh(version)
        
        # Create audit log
        VersionService.log_action(
            db=db,
            version_id=version.id,
            action="created",
            action_description=f"Version {version_label} created",
            actor_id=created_by,
            workspace_id=workspace_id
        )
        
        return version
    
    @staticmethod
    def get_version(
        db: Session,
        version_id: str,
        workspace_id: str
    ) -> Optional[DocumentVersion]:
        """Get a specific version by ID"""
        return db.query(DocumentVersion).filter(
            and_(
                DocumentVersion.id == version_id,
                DocumentVersion.workspace_id == workspace_id
            )
        ).first()
    
    @staticmethod
    def get_document_versions(
        db: Session,
        document_id: str,
        workspace_id: str,
        limit: int = 50
    ) -> List[DocumentVersion]:
        """Get all versions for a document"""
        return db.query(DocumentVersion).filter(
            and_(
                DocumentVersion.document_id == document_id,
                DocumentVersion.workspace_id == workspace_id
            )
        ).order_by(desc(DocumentVersion.version_number)).limit(limit).all()
    
    @staticmethod
    def compare_versions(
        db: Session,
        version_id_1: str,
        version_id_2: str,
        workspace_id: str
    ) -> Dict[str, Any]:
        """
        Compare two versions and return diff
        """
        version1 = VersionService.get_version(db, version_id_1, workspace_id)
        version2 = VersionService.get_version(db, version_id_2, workspace_id)
        
        if not version1 or not version2:
            raise ValueError("One or both versions not found")
        
        diff = VersionService._calculate_diff(version1.content, version2.content)
        
        return {
            "version1": {
                "id": version1.id,
                "version_number": version1.version_number,
                "version_label": version1.version_label,
                "created_at": version1.created_at.isoformat()
            },
            "version2": {
                "id": version2.id,
                "version_number": version2.version_number,
                "version_label": version2.version_label,
                "created_at": version2.created_at.isoformat()
            },
            "diff": diff
        }
    
    @staticmethod
    def approve_version(
        db: Session,
        version_id: str,
        approver_id: str,
        workspace_id: str,
        comment: Optional[str] = None
    ) -> DocumentVersion:
        """Approve a version"""
        version = VersionService.get_version(db, version_id, workspace_id)
        
        if not version:
            raise ValueError(f"Version {version_id} not found")
        
        if version.status not in [VersionStatus.DRAFT, VersionStatus.PENDING_APPROVAL]:
            raise ValueError(f"Version cannot be approved in status: {version.status}")
        
        # Update version
        version.status = VersionStatus.APPROVED
        version.approved_by = approver_id
        version.approved_at = datetime.utcnow()
        
        db.commit()
        db.refresh(version)
        
        # Log approval
        VersionService.log_action(
            db=db,
            version_id=version_id,
            action="approved",
            action_description=f"Version {version.version_label} approved" + (f": {comment}" if comment else ""),
            actor_id=approver_id,
            workspace_id=workspace_id
        )
        
        return version
    
    @staticmethod
    def reject_version(
        db: Session,
        version_id: str,
        rejector_id: str,
        workspace_id: str,
        reason: str
    ) -> DocumentVersion:
        """Reject a version"""
        version = VersionService.get_version(db, version_id, workspace_id)
        
        if not version:
            raise ValueError(f"Version {version_id} not found")
        
        version.status = VersionStatus.REJECTED
        
        db.commit()
        db.refresh(version)
        
        # Log rejection
        VersionService.log_action(
            db=db,
            version_id=version_id,
            action="rejected",
            action_description=f"Version {version.version_label} rejected: {reason}",
            actor_id=rejector_id,
            workspace_id=workspace_id
        )
        
        return version
    
    @staticmethod
    def rollback_to_version(
        db: Session,
        version_id: str,
        user_id: str,
        workspace_id: str,
        reason: str
    ) -> DocumentVersion:
        """
        Rollback to a previous version by creating a new version with old content
        """
        old_version = VersionService.get_version(db, version_id, workspace_id)
        
        if not old_version:
            raise ValueError(f"Version {version_id} not found")
        
        # Create new version with old content
        new_version = VersionService.create_version(
            db=db,
            document_id=old_version.document_id,
            title=old_version.title,
            content=old_version.content,
            workspace_id=workspace_id,
            created_by=user_id,
            change_type=ChangeType.MAJOR,
            change_summary=f"Rollback to version {old_version.version_label}: {reason}",
            iso_standard_id=old_version.iso_standard_id
        )
        
        # Log rollback
        VersionService.log_action(
            db=db,
            version_id=new_version.id,
            action="rollback",
            action_description=f"Rolled back to version {old_version.version_label}",
            actor_id=user_id,
            workspace_id=workspace_id,
            changes_made={"rollback_from_version": version_id}
        )
        
        return new_version
    
    @staticmethod
    def log_action(
        db: Session,
        version_id: str,
        action: str,
        actor_id: str,
        workspace_id: str,
        action_description: Optional[str] = None,
        changes_made: Optional[Dict] = None,
        metadata: Optional[Dict] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None
    ) -> AuditLog:
        """Create an audit log entry"""
        import uuid
        
        log = AuditLog(
            id=str(uuid.uuid4()),
            version_id=version_id,
            action=action,
            action_description=action_description,
            actor_id=actor_id,
            workspace_id=workspace_id,
            changes_made=changes_made,
            metadata=metadata,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return log
    
    @staticmethod
    def get_audit_trail(
        db: Session,
        version_id: str,
        workspace_id: str
    ) -> List[AuditLog]:
        """Get complete audit trail for a version"""
        return db.query(AuditLog).filter(
            and_(
                AuditLog.version_id == version_id,
                AuditLog.workspace_id == workspace_id
            )
        ).order_by(AuditLog.created_at).all()
