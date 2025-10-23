"""
Simplified Workspace Service for Multi-Tenant Management

Simplified version that matches the actual Workspace model schema.
Focuses on core CRUD operations without complex user management.
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from backend.models.iso_models import Workspace, ISOStandard, GeneratedDocument
import uuid
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class WorkspaceService:
    """Simplified workspace management service"""
    
    def __init__(self, session: Session):
        self.session = session
    
    # =================================================================
    # Core CRUD Operations
    # =================================================================
    
    def create_workspace(
        self,
        client_name: str,
        contact_email: str,
        description: Optional[str] = None,
        owner_id: Optional[str] = None,
        **kwargs
    ) -> Workspace:
        """Create a new workspace with optional owner"""
        workspace = Workspace(
            id=str(uuid.uuid4()),
            client_name=client_name,
            contact_email=contact_email,
            description=description,
            owner_id=owner_id,  # Link to authenticated user
            is_active=True,
            settings=kwargs.get('settings', {}),
            **{k: v for k, v in kwargs.items() if k not in ['settings', 'owner_id']}
        )
        
        self.session.add(workspace)
        self.session.flush()
        
        logger.info(f"Created workspace: {client_name} (owner: {owner_id})")
        return workspace
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get workspace by ID"""
        return self.session.query(Workspace).filter_by(
            id=workspace_id,
            is_active=True
        ).first()
    
    def list_workspaces(self, contact_email: Optional[str] = None) -> List[Workspace]:
        """List all active workspaces"""
        query = self.session.query(Workspace).filter_by(is_active=True)
        if contact_email:
            query = query.filter_by(contact_email=contact_email)
        return query.all()
    
    def update_workspace(self, workspace_id: str, **kwargs) -> Workspace:
        """Update workspace"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        for key, value in kwargs.items():
            if hasattr(workspace, key):
                setattr(workspace, key, value)
        
        self.session.flush()
        logger.info(f"Updated workspace: {workspace.client_name}")
        return workspace
    
    def delete_workspace(self, workspace_id: str, hard_delete: bool = False):
        """Delete workspace (soft or hard)"""
        workspace = self.session.query(Workspace).filter_by(id=workspace_id).first()
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        if hard_delete:
            self.session.delete(workspace)
            logger.info(f"Hard deleted workspace: {workspace.client_name}")
        else:
            workspace.is_active = False
            logger.info(f"Soft deleted workspace: {workspace.client_name}")
        
        self.session.flush()
    
    # =================================================================
    # ISO Standard Assignment
    # =================================================================
    
    def assign_standard(self, workspace_id: str, standard_id: str):
        """Assign ISO standard to workspace"""
        workspace = self.get_workspace(workspace_id)
        standard = self.session.query(ISOStandard).filter_by(id=standard_id).first()
        
        if not workspace or not standard:
            raise ValueError("Workspace or standard not found")
        
        if standard not in workspace.standards:
            workspace.standards.append(standard)
            self.session.flush()
            logger.info(f"Assigned {standard.name} to {workspace.client_name}")
    
    def unassign_standard(self, workspace_id: str, standard_id: str):
        """Unassign ISO standard from workspace"""
        workspace = self.get_workspace(workspace_id)
        standard = self.session.query(ISOStandard).filter_by(id=standard_id).first()
        
        if workspace and standard and standard in workspace.standards:
            workspace.standards.remove(standard)
            self.session.flush()
            logger.info(f"Unassigned {standard.name} from {workspace.client_name}")
    
    def get_workspace_standards(self, workspace_id: str) -> List[ISOStandard]:
        """Get all ISO standards assigned to workspace"""
        workspace = self.get_workspace(workspace_id)
        return workspace.standards if workspace else []
    
    # =================================================================
    # Statistics & Helpers
    # =================================================================
    
    def get_workspace_stats(self, workspace_id: str) -> Dict[str, Any]:
        """Get workspace statistics"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        doc_count = self.session.query(GeneratedDocument).filter_by(
            workspace_id=workspace_id
        ).count()
        
        return {
            'workspace_name': workspace.client_name,
            'contact_email': workspace.contact_email,
            'standard_count': len(workspace.standards),
            'document_count': doc_count,
            'is_active': workspace.is_active,
            'plan': workspace.plan,
            'created_at': workspace.created_at
        }


# =================================================================
# Utility Functions
# =================================================================

def create_default_workspace(session: Session, contact_email: str) -> Workspace:
    """Create a default workspace for a new user"""
    service = WorkspaceService(session)
    return service.create_workspace(
        client_name=f"{contact_email.split('@')[0]}'s Workspace",
        contact_email=contact_email,
        description="Default workspace",
        settings={'default': True}
    )


def get_user_workspaces(session: Session, contact_email: str) -> List[Workspace]:
    """Get all workspaces for a user"""
    service = WorkspaceService(session)
    return service.list_workspaces(contact_email=contact_email)
