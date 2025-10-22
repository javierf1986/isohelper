"""
Authentication System Test Suite
Phase 3: Enterprise & Security Features

Tests for JWT authentication, user registration, login, and RBAC.
"""
import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000/api/v1"


class AuthTester:
    """Test authentication endpoints"""
    
    def __init__(self):
        self.access_token: Optional[str] = None
        self.refresh_token: Optional[str] = None
        self.user_id: Optional[str] = None
    
    def print_section(self, title: str):
        """Print section header"""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print('='*60)
    
    def print_result(self, name: str, success: bool, data: dict = None):
        """Print test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"\n{status} - {name}")
        if data:
            print(f"Response: {json.dumps(data, indent=2)}")
    
    def test_health(self):
        """Test health endpoint"""
        self.print_section("Health Check")
        
        try:
            response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
            success = response.status_code == 200
            self.print_result("Health Check", success, response.json())
            return success
        except Exception as e:
            self.print_result("Health Check", False, {"error": str(e)})
            return False
    
    def test_register(self, email: str, password: str, full_name: str = None):
        """Test user registration"""
        self.print_section(f"User Registration: {email}")
        
        payload = {
            "email": email,
            "password": password
        }
        if full_name:
            payload["full_name"] = full_name
        
        try:
            response = requests.post(f"{BASE_URL}/auth/register", json=payload)
            success = response.status_code == 201
            data = response.json()
            
            if success:
                self.user_id = data.get("id")
            
            self.print_result(f"Register {email}", success, data)
            return success
        except Exception as e:
            self.print_result(f"Register {email}", False, {"error": str(e)})
            return False
    
    def test_login(self, email: str, password: str):
        """Test user login"""
        self.print_section(f"User Login: {email}")
        
        payload = {
            "email": email,
            "password": password
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=payload)
            success = response.status_code == 200
            data = response.json()
            
            if success:
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
            
            # Mask tokens in output for security
            if "access_token" in data:
                data["access_token"] = data["access_token"][:50] + "..."
            if "refresh_token" in data:
                data["refresh_token"] = data["refresh_token"][:30] + "..."
            
            self.print_result(f"Login {email}", success, data)
            return success
        except Exception as e:
            self.print_result(f"Login {email}", False, {"error": str(e)})
            return False
    
    def test_get_profile(self):
        """Test getting current user profile"""
        self.print_section("Get Current User Profile")
        
        if not self.access_token:
            self.print_result("Get Profile", False, {"error": "No access token"})
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            success = response.status_code == 200
            data = response.json()
            
            self.print_result("Get Profile", success, data)
            return success
        except Exception as e:
            self.print_result("Get Profile", False, {"error": str(e)})
            return False
    
    def test_update_profile(self, full_name: str):
        """Test updating user profile"""
        self.print_section(f"Update Profile: {full_name}")
        
        if not self.access_token:
            self.print_result("Update Profile", False, {"error": "No access token"})
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        params = {"full_name": full_name}
        
        try:
            response = requests.put(f"{BASE_URL}/auth/me", headers=headers, params=params)
            success = response.status_code == 200
            data = response.json()
            
            self.print_result("Update Profile", success, data)
            return success
        except Exception as e:
            self.print_result("Update Profile", False, {"error": str(e)})
            return False
    
    def test_change_password(self, old_password: str, new_password: str):
        """Test changing password"""
        self.print_section("Change Password")
        
        if not self.access_token:
            self.print_result("Change Password", False, {"error": "No access token"})
            return False
        
        headers = {"Authorization": f"Bearer {self.access_token}"}
        payload = {
            "old_password": old_password,
            "new_password": new_password
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/change-password", headers=headers, json=payload)
            success = response.status_code == 200
            data = response.json()
            
            self.print_result("Change Password", success, data)
            return success
        except Exception as e:
            self.print_result("Change Password", False, {"error": str(e)})
            return False
    
    def test_unauthorized_access(self):
        """Test accessing protected route without token"""
        self.print_section("Unauthorized Access Test")
        
        try:
            response = requests.get(f"{BASE_URL}/auth/me")
            success = response.status_code == 403  # Should be forbidden
            data = response.json()
            
            self.print_result("Unauthorized Access (should fail)", success, data)
            return success
        except Exception as e:
            self.print_result("Unauthorized Access", False, {"error": str(e)})
            return False
    
    def test_invalid_credentials(self):
        """Test login with invalid credentials"""
        self.print_section("Invalid Credentials Test")
        
        payload = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/auth/login", json=payload)
            success = response.status_code == 401  # Should be unauthorized
            data = response.json()
            
            self.print_result("Invalid Credentials (should fail)", success, data)
            return success
        except Exception as e:
            self.print_result("Invalid Credentials", False, {"error": str(e)})
            return False


def main():
    """Run comprehensive authentication tests"""
    tester = AuthTester()
    
    print("🔐 ISO Helper - Authentication System Test Suite")
    print("Phase 3: Enterprise & Security Features")
    print("\nMake sure the server is running: python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000")
    
    # Test credentials
    test_email = "testuser@example.com"
    test_password = "SecurePass1!"
    test_name = "Test User"
    new_password = "NewPass456!"
    
    results = []
    
    # Run tests
    results.append(("Health Check", tester.test_health()))
    results.append(("Register User", tester.test_register(test_email, test_password, test_name)))
    results.append(("Login User", tester.test_login(test_email, test_password)))
    results.append(("Get Profile", tester.test_get_profile()))
    results.append(("Update Profile", tester.test_update_profile("Updated Test User")))
    results.append(("Change Password", tester.test_change_password(test_password, new_password)))
    results.append(("Login with New Password", tester.test_login(test_email, new_password)))
    results.append(("Unauthorized Access", tester.test_unauthorized_access()))
    results.append(("Invalid Credentials", tester.test_invalid_credentials()))
    
    # Summary
    print("\n" + "="*60)
    print("  TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n📊 Results: {passed}/{total} tests passed ({passed*100//total}%)")
    
    if passed == total:
        print("\n🎉 All tests passed! Authentication system is working correctly.")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check the output above for details.")


if __name__ == "__main__":
    main()
