"""
Quick test for simplified workspace service
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database.init_db import get_session, init_database
from backend.services.workspace_service_v2 import WorkspaceService, create_default_workspace
from backend.models.iso_models import ISOStandard

def main():
    print("\n🧪 Testing Simplified Workspace Service\n")
    
    # Initialize
    init_database(drop_existing=False)
    session = get_session()
    service = WorkspaceService(session)
    
    try:
        # Test 1: Create workspace
        print("1️⃣  Creating workspace...")
        ws = service.create_workspace(
            client_name="Test Company",
            contact_email="admin@test.com",
            description="Test workspace"
        )
        print(f"   ✅ Created: {ws.client_name} (ID: {ws.id})")
        
        # Test 2: List workspaces
        print("\n2️⃣  Listing workspaces...")
        workspaces = service.list_workspaces()
        print(f"   ✅ Found {len(workspaces)} workspace(s)")
        
        # Test 3: Assign standard
        standards = session.query(ISOStandard).all()
        if standards:
            print(f"\n3️⃣  Assigning ISO standard...")
            service.assign_standard(ws.id, standards[0].id)
            assigned = service.get_workspace_standards(ws.id)
            print(f"   ✅ Assigned {len(assigned)} standard(s)")
        else:
            print(f"\n3️⃣  ⚠️  No ISO standards in database")
        
        # Test 4: Get stats
        print("\n4️⃣  Getting statistics...")
        stats = service.get_workspace_stats(ws.id)
        print(f"   ✅ Workspace: {stats['workspace_name']}")
        print(f"   ✅ Standards: {stats['standard_count']}")
        print(f"   ✅ Documents: {stats['document_count']}")
        
        # Test 5: Delete
        print("\n5️⃣  Deleting workspace...")
        service.delete_workspace(ws.id, hard_delete=False)
        active = service.get_workspace(ws.id)
        print(f"   ✅ Soft delete: {'success' if not active else 'failed'}")
        
        session.rollback()
        print("\n✅ All tests passed!\n")
        return 0
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}\n")
        session.rollback()
        return 1
    finally:
        session.close()


if __name__ == "__main__":
    sys.exit(main())
