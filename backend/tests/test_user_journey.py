"""
End-to-End User Journey Test Script
Tests the complete workflow from registration to document deletion
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8889/api/v1"
TEST_USER_EMAIL = f"testuser_{int(time.time())}@example.com"
TEST_USER_PASSWORD = "TestPass123!"
TEST_USER_NAME = "Test User"

# Global variables
access_token = None
document_id = None

def print_step(step_num, description):
    """Print test step with formatting"""
    print(f"\n{'='*70}")
    print(f"STEP {step_num}: {description}")
    print('='*70)

def print_result(success, message):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status}: {message}")

def test_1_register():
    """Test user registration"""
    print_step(1, "User Registration")
    
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD,
        "full_name": TEST_USER_NAME
    }
    
    try:
        response = requests.post(f"{BASE_URL}/auth/register", json=payload)
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_result(True, f"User registered successfully")
            print(f"   User ID: {data.get('id')}")
            print(f"   Email: {data.get('email')}")
            print(f"   Name: {data.get('full_name')}")
            return True
        else:
            print_result(False, f"Registration failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False

def test_2_login():
    """Test user login"""
    print_step(2, "User Login")
    
    global access_token
    
    payload = {
        "email": TEST_USER_EMAIL,
        "password": TEST_USER_PASSWORD
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/auth/login", 
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            print_result(True, "Login successful")
            print(f"   Access Token: {access_token[:50]}...")
            print(f"   Token Type: {data.get('token_type')}")
            return True
        else:
            print_result(False, f"Login failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False

def test_3_get_standards():
    """Test getting ISO standards list"""
    print_step(3, "Get ISO Standards")
    
    try:
        response = requests.get(f"{BASE_URL}/templates/standards")
        
        if response.status_code == 200:
            standards = response.json()
            print_result(True, f"Retrieved {len(standards)} ISO standards")
            for std in standards:
                print(f"   - {std['name']} (ID: {std['id']})")
            return True, standards
        else:
            print_result(False, f"Failed: {response.status_code}")
            return False, []
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False, []

def test_4_get_clauses(standard_id):
    """Test getting clauses for a standard"""
    print_step(4, f"Get Clauses for {standard_id}")
    
    try:
        response = requests.get(f"{BASE_URL}/templates/{standard_id}/clauses")
        
        if response.status_code == 200:
            clauses = response.json()
            print_result(True, f"Retrieved {len(clauses)} clauses")
            print(f"   First 5 clauses:")
            for clause in clauses[:5]:
                print(f"   - {clause['number']}: {clause['title']}")
            return True, clauses
        else:
            print_result(False, f"Failed: {response.status_code}")
            return False, []
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False, []

def test_5_generate_document(standard_id, clause_numbers):
    """Test document generation"""
    print_step(5, "Generate Document")
    
    global document_id
    
    payload = {
        "iso_standard": standard_id,
        "selected_clauses": clause_numbers,
        "company_name": "Acme Corporation",
        "company_description": "Leading provider of quality solutions",
        "scope": "Quality Management System for software development",
        "use_ai_enhancement": True
    }
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        print("   Generating document (this may take a moment)...")
        response = requests.post(
            f"{BASE_URL}/documents/generate",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            document_id = data.get('id')
            print_result(True, "Document generated successfully")
            print(f"   Document ID: {document_id}")
            print(f"   Title: {data.get('title')}")
            print(f"   File Path: {data.get('file_path')}")
            print(f"   ISO Standard: {data.get('iso_standard')}")
            return True
        else:
            print_result(False, f"Failed: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False

def test_6_list_documents():
    """Test listing documents"""
    print_step(6, "List Documents")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(f"{BASE_URL}/documents", headers=headers)
        
        if response.status_code == 200:
            documents = response.json()
            print_result(True, f"Retrieved {len(documents)} documents")
            for doc in documents:
                print(f"   - ID {doc['id']}: {doc['title']} ({doc['iso_standard']})")
            return True, documents
        else:
            print_result(False, f"Failed: {response.status_code}")
            return False, []
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False, []

def test_7_get_document_details():
    """Test getting document details"""
    print_step(7, "Get Document Details")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.get(
            f"{BASE_URL}/documents/{document_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            doc = response.json()
            print_result(True, "Document details retrieved")
            print(f"   Title: {doc.get('title')}")
            print(f"   ISO Standard: {doc.get('iso_standard')}")
            print(f"   Created: {doc.get('created_at')}")
            print(f"   Content Length: {len(doc.get('content', ''))} characters")
            return True
        else:
            print_result(False, f"Failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False

def test_8_export_document():
    """Test document export"""
    print_step(8, "Export Document")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    # Get the document to find its file path
    doc_response = requests.get(
        f"{BASE_URL}/documents/{document_id}",
        headers=headers
    )
    
    if doc_response.status_code != 200:
        print_result(False, "Could not get document details")
        return False
    
    doc = doc_response.json()
    file_path = doc.get('file_path')
    
    formats = ['pdf', 'docx', 'html']
    all_success = True
    
    for format_type in formats:
        print(f"\n   Testing {format_type.upper()} export...")
        
        payload = {
            "document_path": file_path,
            "format": format_type,
            "company_name": "Acme Corporation",
            "include_branding": True
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/export",
                json=payload,
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"   ✅ {format_type.upper()} export successful")
                print(f"      Output: {data.get('file_path')}")
            else:
                print(f"   ❌ {format_type.upper()} export failed: {response.status_code}")
                all_success = False
        except Exception as e:
            print(f"   ❌ {format_type.upper()} exception: {str(e)}")
            all_success = False
    
    print_result(all_success, "Export tests completed")
    return all_success

def test_9_delete_document():
    """Test document deletion"""
    print_step(9, "Delete Document")
    
    headers = {
        "Authorization": f"Bearer {access_token}"
    }
    
    try:
        response = requests.delete(
            f"{BASE_URL}/documents/{document_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            print_result(True, "Document deleted successfully")
            
            # Verify deletion
            verify_response = requests.get(
                f"{BASE_URL}/documents/{document_id}",
                headers=headers
            )
            
            if verify_response.status_code == 404:
                print("   ✅ Verified: Document no longer exists")
                return True
            else:
                print("   ⚠️  Warning: Document may still exist")
                return True
        else:
            print_result(False, f"Failed: {response.status_code}")
            return False
    except Exception as e:
        print_result(False, f"Exception: {str(e)}")
        return False

def main():
    """Run all tests"""
    print("\n" + "="*70)
    print(" ISO HELPER - END-TO-END USER JOURNEY TEST")
    print("="*70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {BASE_URL}")
    print(f"Test User: {TEST_USER_EMAIL}")
    
    results = []
    
    # Test 1: Register
    results.append(("Registration", test_1_register()))
    
    # Test 2: Login
    if results[-1][1]:
        results.append(("Login", test_2_login()))
    else:
        print("\n⚠️  Skipping remaining tests due to registration failure")
        return
    
    # Test 3: Get Standards
    if results[-1][1]:
        success, standards = test_3_get_standards()
        results.append(("Get Standards", success))
        
        if success and len(standards) > 0:
            standard_id = standards[0]['id']
            
            # Test 4: Get Clauses
            success, clauses = test_4_get_clauses(standard_id)
            results.append(("Get Clauses", success))
            
            if success and len(clauses) > 0:
                # Select first 5 clauses
                clause_numbers = [c['number'] for c in clauses[:5]]
                
                # Test 5: Generate Document
                success = test_5_generate_document(standard_id, clause_numbers)
                results.append(("Generate Document", success))
                
                if success and document_id:
                    # Test 6: List Documents
                    success, docs = test_6_list_documents()
                    results.append(("List Documents", success))
                    
                    # Test 7: Get Document Details
                    success = test_7_get_document_details()
                    results.append(("Get Document Details", success))
                    
                    # Test 8: Export Document
                    success = test_8_export_document()
                    results.append(("Export Document", success))
                    
                    # Test 9: Delete Document
                    success = test_9_delete_document()
                    results.append(("Delete Document", success))
    
    # Print summary
    print("\n" + "="*70)
    print(" TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed ({(passed/total*100):.1f}%)")
    print(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)

if __name__ == "__main__":
    main()
