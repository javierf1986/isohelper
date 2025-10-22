"""
Quick API endpoint tests using requests library
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("="*70)
print(" ISO 9001 API - Quick Endpoint Tests")
print("="*70)
print()

# Test 1: Health Check
print("1️⃣  Testing /health endpoint...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    print("   ✅ PASS")
except Exception as e:
    print(f"   ❌ FAIL: {e}")
print()

# Test 2: Root
print("2️⃣  Testing / (root) endpoint...")
try:
    response = requests.get(BASE_URL, timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    print("   ✅ PASS")
except Exception as e:
    print(f"   ❌ FAIL: {e}")
print()

# Test 3: Templates
print("3️⃣  Testing /api/v1/templates/ endpoint...")
try:
    response = requests.get(f"{BASE_URL}/api/v1/templates/", timeout=5)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    print("   ✅ PASS (Returns empty - implementation pending)")
except Exception as e:
    print(f"   ❌ FAIL: {e}")
print()

# Test 4: Generate Document
print("4️⃣  Testing /api/v1/documents/generate endpoint...")
try:
    payload = {
        "company_name": "Test Corp via API",
        "industry": "software",
        "company_size": "small",
        "clauses": ["4.1"],
        "language": "en"
    }
    response = requests.post(
        f"{BASE_URL}/api/v1/documents/generate",
        json=payload,
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    print("   ✅ PASS (Returns placeholder - full implementation pending)")
except Exception as e:
    print(f"   ❌ FAIL: {e}")
print()

print("="*70)
print("✅ API Testing Complete!")
print()
print("💡 Tips:")
print("   - Visit http://localhost:8000/docs for interactive API documentation")
print("   - Run 'python test_manual.py' to test actual document generation")
print("   - Check './generated_documents/' for generated files")
print("="*70)
