"""
Test script for Workspace API endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_workspace_api():
    print("\n🧪 Testing Workspace API Endpoints\n")
    
    # Test 1: Create workspace
    print("1️⃣  Creating workspace...")
    response = requests.post(
        f"{BASE_URL}/workspaces",
        json={
            "client_name": "Test Company",
            "contact_email": "admin@test.com",
            "description": "Test workspace",
            "industry": "Technology",
            "company_size": "medium"
        }
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 201:
        workspace = response.json()
        workspace_id = workspace['id']
        print(f"   ✅ Created workspace: {workspace['client_name']}")
        print(f"   ID: {workspace_id}")
    else:
        print(f"   ❌ Failed: {response.text}")
        return
    
    # Test 2: Get workspace
    print(f"\n2️⃣  Getting workspace {workspace_id}...")
    response = requests.get(f"{BASE_URL}/workspaces/{workspace_id}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        ws = response.json()
        print(f"   ✅ Retrieved: {ws['client_name']}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test 3: List workspaces
    print("\n3️⃣  Listing all workspaces...")
    response = requests.get(f"{BASE_URL}/workspaces")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        workspaces = response.json()
        print(f"   ✅ Found {len(workspaces)} workspace(s)")
        for ws in workspaces:
            print(f"      • {ws['client_name']}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test 4: Update workspace
    print(f"\n4️⃣  Updating workspace {workspace_id}...")
    response = requests.put(
        f"{BASE_URL}/workspaces/{workspace_id}",
        json={
            "description": "Updated test workspace",
            "industry": "Software Development"
        }
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        ws = response.json()
        print(f"   ✅ Updated: {ws['description']}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test 5: Get workspace stats
    print(f"\n5️⃣  Getting workspace stats...")
    response = requests.get(f"{BASE_URL}/workspaces/{workspace_id}/stats")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()
        print(f"   ✅ Stats:")
        print(f"      • Standards: {stats['standard_count']}")
        print(f"      • Documents: {stats['document_count']}")
        print(f"      • Plan: {stats['plan']}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    # Test 6: Assign ISO standard (if available)
    print(f"\n6️⃣  Checking for ISO standards...")
    response = requests.get(f"{BASE_URL}/workspaces/{workspace_id}/standards")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        standards = response.json()
        print(f"   ✅ Currently {len(standards)} standard(s) assigned")
    
    # Test 7: Delete workspace
    print(f"\n7️⃣  Deleting workspace {workspace_id}...")
    response = requests.delete(f"{BASE_URL}/workspaces/{workspace_id}")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"   ✅ Deleted: {result['message']}")
    else:
        print(f"   ❌ Failed: {response.text}")
    
    print("\n✅ All API tests completed!\n")


if __name__ == "__main__":
    try:
        test_workspace_api()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to server. Make sure it's running on port 8000\n")
    except Exception as e:
        print(f"\n❌ Error: {e}\n")
