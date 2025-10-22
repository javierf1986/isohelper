"""
Test script for ISO 9001 API
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_health():
    """Test the health endpoint"""
    print("🔍 Testing /health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_root():
    """Test the root endpoint"""
    print("🔍 Testing / (root) endpoint...")
    response = requests.get(BASE_URL)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_list_templates():
    """Test listing available templates"""
    print("🔍 Testing /api/v1/templates endpoint...")
    response = requests.get(f"{BASE_URL}/api/v1/templates/")
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

def test_generate_document():
    """Test document generation"""
    print("🔍 Testing /api/v1/documents/generate endpoint...")
    
    payload = {
        "company_name": "ABC Manufacturing Ltd",
        "industry": "automotive",
        "company_size": "medium",
        "clauses": ["4.1", "4.2"],
        "language": "en",
        "custom_context": "We specialize in electric vehicle components"
    }
    
    response = requests.post(
        f"{BASE_URL}/api/v1/documents/generate",
        json=payload
    )
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    print()

if __name__ == "__main__":
    print("=" * 60)
    print("ISO 9001 AI Documentation Generator - API Tests")
    print("=" * 60)
    print()
    
    try:
        test_health()
        test_root()
        test_list_templates()
        test_generate_document()
        
        print("✅ All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API.")
        print("   Make sure the server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
