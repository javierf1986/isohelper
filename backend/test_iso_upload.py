"""
Test script for ISO Standards Upload API
Tests the complete upload and parsing flow
"""
import requests
import json
from pathlib import Path

# Configuration
API_BASE = "http://localhost:8000/api/v1"
TEST_FILE = Path("../test_data/iso_14001_2015_mock.txt")

def get_auth_token():
    """Get authentication token (mock for testing)"""
    # For testing, we'll skip auth or use a test token
    # In production, you'd login first
    return None

def test_list_standards():
    """Test listing all ISO standards"""
    print("\n" + "="*60)
    print("TEST: List ISO Standards")
    print("="*60)
    
    response = requests.get(f"{API_BASE}/iso-standards/")
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} standards:")
        for std in data:
            print(f"  - {std['name']} (ISO {std['iso_number']}:{std['year']}): {std['clause_count']} clauses")
    else:
        print(f"Error: {response.text}")
    
    return response.status_code == 200

def test_upload_standard():
    """Test uploading an ISO standard document"""
    print("\n" + "="*60)
    print("TEST: Upload ISO Standard")
    print("="*60)
    
    if not TEST_FILE.exists():
        print(f"❌ Test file not found: {TEST_FILE}")
        return False
    
    print(f"Uploading: {TEST_FILE}")
    
    with open(TEST_FILE, 'rb') as f:
        files = {'file': (TEST_FILE.name, f, 'text/plain')}
        response = requests.post(
            f"{API_BASE}/iso-standards/upload",
            files=files
        )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("✅ Upload successful!")
        print(f"Standard: {data['standard']['name']} (ISO {data['standard']['iso_number']}:{data['standard']['year']})")
        print(f"ID: {data['standard']['id']}")
        print(f"Category: {data['standard']['category']}")
        print(f"Clauses: {data['standard']['clause_count']}")
        
        if 'statistics' in data:
            stats = data['statistics']
            print("\nStatistics:")
            print(f"  - Total clauses: {stats.get('total_clauses', 0)}")
            print(f"  - Requirements: {stats.get('requirements', 0)}")
            print(f"  - Guidance: {stats.get('guidance', 0)}")
            print(f"  - Pages: {stats.get('pages', 0)}")
        
        return data['standard']['id']
    else:
        print(f"❌ Upload failed: {response.text}")
        return None

def test_get_standard_detail(standard_id):
    """Test getting detailed information about a standard"""
    print("\n" + "="*60)
    print("TEST: Get Standard Detail")
    print("="*60)
    
    response = requests.get(f"{API_BASE}/iso-standards/{standard_id}")
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Standard: {data['name']} (ISO {data['iso_number']}:{data['year']})")
        print(f"Description: {data['description'][:100]}...")
        print(f"Clauses: {len(data['clauses'])}")
        
        # Show first few clauses
        print("\nFirst 5 clauses:")
        for clause in data['clauses'][:5]:
            print(f"  {clause['clause_number']} - {clause['title']}")
        
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def test_delete_standard(standard_id):
    """Test deleting a standard"""
    print("\n" + "="*60)
    print("TEST: Delete Standard")
    print("="*60)
    
    response = requests.delete(f"{API_BASE}/iso-standards/{standard_id}")
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ {data['message']}")
        return True
    else:
        print(f"❌ Failed: {response.text}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("ISO STANDARDS API TEST SUITE")
    print("="*60)
    
    # Test 1: List standards (should be empty or show existing)
    test_list_standards()
    
    # Test 2: Upload a standard
    standard_id = test_upload_standard()
    
    if standard_id:
        # Test 3: Get detail
        test_get_standard_detail(standard_id)
        
        # Test 4: List again (should show the uploaded standard)
        test_list_standards()
        
        # Test 5: Delete the standard
        # test_delete_standard(standard_id)
        print("\n⚠️  Skipping delete test - keeping standard for frontend testing")
    
    print("\n" + "="*60)
    print("TEST SUITE COMPLETE")
    print("="*60)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Could not connect to backend server")
        print("Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
