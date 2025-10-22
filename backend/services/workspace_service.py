"""
Workspace Service - Multi-Tenant Management

This service provides:
- Workspace CRUD operations
- Client isolation
- User management
- Role-Based Access Control (RBAC)
- Standard assignment to workspaces
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from backend.models.iso_models import (
    Workspace,
    ISOStandard,
    GeneratedDocument,
    workspace_standards
)
from enum import Enum

logger = logging.getLogger(__name__)


class UserRole(str, Enum):
    """User roles for RBAC"""
    ADMIN = "admin"              # Full access, manage users
    MANAGER = "manager"          # Create/edit documents, view all
    CONTRIBUTOR = "contributor"  # Create/edit own documents
    VIEWER = "viewer"            # Read-only access


class WorkspaceService:
    """Service for managing workspaces and multi-tenancy"""
    
    def __init__(self, session: Session):
        self.session = session
    
    # ==================== Workspace CRUD ====================
    
    def create_workspace(
        self,
        client_name: str,
        contact_email: str,
        description: Optional[str] = None,
        settings: Optional[Dict] = None
    ) -> Workspace:
        """
        Create a new workspace
        
        Args:
            client_name: Workspace/client name
            contact_email: Email of workspace owner/contact
            description: Optional description
            settings: Optional workspace settings
            
        Returns:
            Created Workspace object
        """
        # Check if workspace name already exists
        existing = self.session.query(Workspace).filter_by(client_name=client_name).first()
        if existing:
            raise ValueError(f"Workspace '{client_name}' already exists")
        
        # Create workspace
        workspace = Workspace(
            client_name=client_name,
            description=description or f"Workspace for {client_name}",
            contact_email=contact_email,
            settings=settings or {},
            is_active=True
        )
        
        self.session.add(workspace)
        self.session.flush()
        
        logger.info(f"Created workspace: {workspace.client_name} (ID: {workspace.id})")
        return workspace
    
    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        """Get workspace by ID"""
        return self.session.query(Workspace).filter_by(
            id=workspace_id,
            is_active=True
        ).first()
    
    def get_workspace_by_name(self, name: str) -> Optional[Workspace]:
        """Get workspace by name"""
        return self.session.query(Workspace).filter_by(
            name=name,
            is_active=True
        ).first()
    
    def list_workspaces(
        self,
        owner_email: Optional[str] = None,
        include_inactive: bool = False
    ) -> List[Workspace]:
        """
        List all workspaces
        
        Args:
            owner_email: Filter by owner email
            include_inactive: Include inactive workspaces
            
        Returns:
            List of Workspace objects
        """
        query = self.session.query(Workspace)
        
        if not include_inactive:
            query = query.filter_by(is_active=True)
        
        if owner_email:
            query = query.filter_by(owner_email=owner_email)
        
        return query.order_by(Workspace.created_at.desc()).all()
    
    def update_workspace(
        self,
        workspace_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        settings: Optional[Dict] = None
    ) -> Workspace:
        """
        Update workspace details
        
        Args:
            workspace_id: Workspace ID
            name: New name (optional)
            description: New description (optional)
            settings: New settings (optional)
            
        Returns:
            Updated Workspace object
        """
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        if name and name != workspace.name:
            # Check for name collision
            existing = self.get_workspace_by_name(name)
            if existing and existing.id != workspace_id:
                raise ValueError(f"Workspace name '{name}' already exists")
            workspace.name = name
        
        if description is not None:
            workspace.description = description
        
        if settings is not None:
            workspace.settings = settings
        
        workspace.updated_at = datetime.utcnow()
        self.session.flush()
        
        logger.info(f"Updated workspace: {workspace.name}")
        return workspace
    
    def delete_workspace(self, workspace_id: str, hard_delete: bool = False):
        """
        Delete workspace (soft delete by default)
        
        Args:
            workspace_id: Workspace ID
            hard_delete: If True, permanently delete from database
        """
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        if hard_delete:
            self.session.delete(workspace)
            logger.info(f"Hard deleted workspace: {workspace.name}")
        else:
            workspace.is_active = False
            workspace.updated_at = datetime.utcnow()
            logger.info(f"Soft deleted workspace: {workspace.name}")
        
        self.session.flush()
    
    # ==================== ISO Standard Assignment ====================
    
    def assign_standard(self, workspace_id: str, standard_id: str):
        """
        Assign an ISO standard to a workspace
        
        Args:
            workspace_id: Workspace ID
            standard_id: ISO Standard ID
        """
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        standard = self.session.query(ISOStandard).filter_by(id=standard_id).first()
        if not standard:
            raise ValueError(f"Standard {standard_id} not found")
        
        # Check if already assigned
        if standard in workspace.standards:
            logger.info(f"Standard {standard.number} already assigned to {workspace.name}")
            return
        
        # Assign standard
        workspace.standards.append(standard)
        self.session.flush()
        
        logger.info(f"Assigned {standard.number}:{standard.year} to {workspace.name}")
    
    def unassign_standard(self, workspace_id: str, standard_id: str):
        """
        Remove an ISO standard from a workspace
        
        Args:
            workspace_id: Workspace ID
            standard_id: ISO Standard ID
        """
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        standard = self.session.query(ISOStandard).filter_by(id=standard_id).first()
        if not standard:
            raise ValueError(f"Standard {standard_id} not found")
        
        if standard in workspace.standards:
            workspace.standards.remove(standard)
            self.session.flush()
            logger.info(f"Unassigned {standard.number} from {workspace.name}")
        else:
            logger.info(f"Standard {standard.number} not assigned to {workspace.name}")
    
    def get_workspace_standards(self, workspace_id: str) -> List[ISOStandard]:
        """
        Get all ISO standards assigned to a workspace
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            List of ISOStandard objects
        """
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        return workspace.standards
    
    # ==================== Document Management ====================
    
    def get_workspace_documents(
        self,
        workspace_id: str,
        standard_number: Optional[str] = None
    ) -> List[GeneratedDocument]:
        """
        Get all documents in a workspace
        
        Args:
            workspace_id: Workspace ID
            standard_number: Filter by ISO standard number (optional)
            
        Returns:
            List of GeneratedDocument objects
        """
        query = self.session.query(GeneratedDocument).filter_by(
            workspace_id=workspace_id
        )
        
        if standard_number:
            query = query.filter_by(standard_number=standard_number)
        
        return query.order_by(GeneratedDocument.created_at.desc()).all()
    
    def get_document_count(self, workspace_id: str) -> int:
        """Get total document count for workspace"""
        return self.session.query(GeneratedDocument).filter_by(
            workspace_id=workspace_id
        ).count()
    
    # ==================== User Management ====================
    
    def add_user_to_workspace(
        self,
        workspace_id: str,
        user_email: str,
        role: UserRole
    ):
        """
        Add a user to workspace with specific role
        
        Args:
            workspace_id: Workspace ID
            user_email: User email
            role: User role (UserRole enum)
        """
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        # Get or create user list in settings
        users = workspace.settings.get('users', {})
        users[user_email] = {
            'role': role.value,
            'added_at': datetime.utcnow().isoformat()
        }
        workspace.settings['users'] = users
        workspace.updated_at = datetime.utcnow()
        
        self.session.flush()
        logger.info(f"Added {user_email} as {role.value} to {workspace.name}")
    
    def remove_user_from_workspace(self, workspace_id: str, user_email: str):
        """Remove a user from workspace"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        users = workspace.settings.get('users', {})
        if user_email in users:
            del users[user_email]
            workspace.settings['users'] = users
            workspace.updated_at = datetime.utcnow()
            self.session.flush()
            logger.info(f"Removed {user_email} from {workspace.name}")
    
    def get_user_role(self, workspace_id: str, user_email: str) -> Optional[UserRole]:
        """Get user's role in workspace"""
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            return None
        
        # Owner has admin role
        if workspace.owner_email == user_email:
            return UserRole.ADMIN
        
        users = workspace.settings.get('users', {})
        user_data = users.get(user_email)
        
        if user_data:
            return UserRole(user_data['role'])
        
        return None
    
    def check_permission(
        self,
        workspace_id: str,
        user_email: str,
        required_role: UserRole
    ) -> bool:
        """
        Check if user has required permission level
        
        Args:
            workspace_id: Workspace ID
            user_email: User email
            required_role: Minimum required role
            
        Returns:
            True if user has permission
        """
        user_role = self.get_user_role(workspace_id, user_email)
        if not user_role:
            return False
        
        # Role hierarchy
        role_hierarchy = {
            UserRole.VIEWER: 1,
            UserRole.CONTRIBUTOR: 2,
            UserRole.MANAGER: 3,
            UserRole.ADMIN: 4
        }
        
        return role_hierarchy[user_role] >= role_hierarchy[required_role]
    
    def list_workspace_users(self, workspace_id: str) -> Dict[str, Dict]:
        """
        List all users in workspace with their roles
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            Dictionary mapping email to user data
        """
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        users = workspace.settings.get('users', {}).copy()
        
        # Add owner
        users[workspace.owner_email] = {
            'role': UserRole.ADMIN.value,
            'added_at': workspace.created_at.isoformat(),
            'is_owner': True
        }
        
        return users
    
    # ==================== Statistics ====================
    
    def get_workspace_stats(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get workspace statistics
        
        Args:
            workspace_id: Workspace ID
            
        Returns:
            Dictionary with statistics
        """
        workspace = self.get_workspace(workspace_id)
        if not workspace:
            raise ValueError(f"Workspace {workspace_id} not found")
        
        document_count = self.get_document_count(workspace_id)
        standard_count = len(workspace.standards)
        user_count = len(workspace.settings.get('users', {})) + 1  # +1 for owner
        
        return {
            'workspace_id': workspace.id,
            'workspace_name': workspace.name,
            'owner_email': workspace.owner_email,
            'created_at': workspace.created_at.isoformat(),
            'document_count': document_count,
            'standard_count': standard_count,
            'user_count': user_count,
            'is_active': workspace.is_active
        }


# ==================== Helper Functions ====================

def create_default_workspace(session: Session, owner_email: str) -> Workspace:
    """
    Create a default workspace for a new user
    
    Args:
        session: SQLAlchemy session
        owner_email: Owner email
        
    Returns:
        Created Workspace object
    """
    service = WorkspaceService(session)
    
    workspace = service.create_workspace(
        client_name=f"{owner_email.split('@')[0]}'s Workspace",
        contact_email=owner_email,
        description="Default workspace",
        settings={'default': True}
    )
    
    session.commit()
    return workspace


def get_user_workspaces(session: Session, user_email: str) -> List[Workspace]:
    """
    Get all workspaces accessible by a user
    
    Args:
        session: SQLAlchemy session
        user_email: User email
        
    Returns:
        List of Workspace objects
    """
    service = WorkspaceService(session)
    
    # Get workspaces owned by user
    owned = service.list_workspaces(owner_email=user_email)
    
    # Get workspaces where user is a member
    all_workspaces = service.list_workspaces()
    member_of = [
        ws for ws in all_workspaces
        if user_email in ws.settings.get('users', {})
    ]
    
    # Combine and deduplicate
    all_user_workspaces = list({ws.id: ws for ws in owned + member_of}.values())
    
    return sorted(all_user_workspaces, key=lambda x: x.created_at, reverse=True)


if __name__ == "__main__":
    # Test the workspace service
    logging.basicConfig(level=logging.INFO)
    
    print("Workspace Service - Multi-Tenant Management")
    print("=" * 50)
    print("\nFeatures:")
    print("  • Workspace CRUD operations")
    print("  • Client isolation")
    print("  • Role-Based Access Control (RBAC)")
    print("  • ISO standard assignment")
    print("  • User management")
    print("  • Document tracking")
    print("\nRoles:")
    print(f"  • {UserRole.ADMIN.value}: Full access, manage users")
    print(f"  • {UserRole.MANAGER.value}: Create/edit documents, view all")
    print(f"  • {UserRole.CONTRIBUTOR.value}: Create/edit own documents")
    print(f"  • {UserRole.VIEWER.value}: Read-only access")
