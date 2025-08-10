#!/usr/bin/env python3
"""
Permission Testing Script
------------------------
This script tests the two-tier user permission system:
- Admin (user_type_id=1): Full privileges
- Regular User (user_type_id=2): Limited privileges (list, search, login, logout only)

Run this script to verify the permission system works correctly.
"""

import requests
import json
import sys

BASE_URL = "http://127.0.0.1:5000"

def test_login(username, password):
    """Test login and return token"""
    url = f"{BASE_URL}/db/v1/api/auth/login"
    data = {"username": username, "password": password}
    
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            result = response.json()
            if result['status'] == 'success':
                token = result['data']['token']
                user_info = result['data']['user']
                print(f"✅ Login successful for {username}")
                print(f"   User Type: {user_info['role']} (ID: {user_info['user_type_id']})")
                return token
        print(f"❌ Login failed for {username}: {response.text}")
        return None
    except Exception as e:
        print(f"❌ Login error for {username}: {e}")
        return None

def test_endpoint(endpoint, method="GET", token=None, data=None, should_succeed=True):
    """Test an API endpoint with expected outcome"""
    url = f"{BASE_URL}{endpoint}"
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers)
        elif method == "POST":
            response = requests.post(url, json=data, headers=headers)
        elif method == "PUT":
            response = requests.put(url, json=data, headers=headers)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers)
        
        success = response.status_code < 400
        
        if should_succeed and success:
            print(f"✅ {method} {endpoint} - SUCCESS (as expected)")
            return True
        elif not should_succeed and not success:
            print(f"✅ {method} {endpoint} - BLOCKED (as expected) - Status: {response.status_code}")
            return True
        elif should_succeed and not success:
            print(f"❌ {method} {endpoint} - FAILED (should have worked) - Status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
        else:  # not should_succeed and success
            print(f"❌ {method} {endpoint} - ALLOWED (should have been blocked!) - Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ {method} {endpoint} - ERROR: {e}")
        return False

def main():
    print("🧪 Testing Two-Tier User Permission System")
    print("=" * 50)
    
    # Test admin login
    print("\n1. Testing Admin Login...")
    admin_token = test_login("acmeadmin", "password123")
    if not admin_token:
        print("Cannot proceed without admin token")
        sys.exit(1)
    
    # Test regular user login
    print("\n2. Testing Regular User Login...")
    user_token = test_login("test", "test123")
    if not user_token:
        print("Cannot proceed without user token")
        sys.exit(1)
    
    print("\n3. Testing Admin Privileges (All should work)...")
    admin_tests = [
        ("/db/v1/api/user/list", "GET", None, True),
        ("/db/v1/api/user/search?q=test", "GET", None, True),
        ("/db/v1/api/user/create", "POST", {"username": "testuser", "password": "test123", "user_type_id": 2}, True),
        ("/db/v1/api/user/update", "PUT", {"username": "updated"}, True),
        ("/db/v1/api/user/delete", "DELETE", None, True),
    ]
    
    admin_success = 0
    for endpoint, method, data, should_succeed in admin_tests:
        if test_endpoint(endpoint, method, admin_token, data, should_succeed):
            admin_success += 1
    
    print(f"\n   Admin Tests: {admin_success}/{len(admin_tests)} passed")
    
    print("\n4. Testing Regular User Privileges...")
    print("   ✅ Should work: list, search")
    print("   ❌ Should be blocked: create, update, delete")
    
    user_tests = [
        ("/db/v1/api/user/list", "GET", None, True),  # Should work
        ("/db/v1/api/user/search?q=test", "GET", None, True),  # Should work
        ("/db/v1/api/user/create", "POST", {"username": "blocked", "password": "test123"}, False),  # Should be blocked
        ("/db/v1/api/user/update", "PUT", {"username": "blocked"}, False),  # Should be blocked
        ("/db/v1/api/user/delete", "DELETE", None, False),  # Should be blocked
    ]
    
    user_success = 0
    for endpoint, method, data, should_succeed in user_tests:
        if test_endpoint(endpoint, method, user_token, data, should_succeed):
            user_success += 1
    
    print(f"\n   Regular User Tests: {user_success}/{len(user_tests)} passed")
    
    # Summary
    total_tests = len(admin_tests) + len(user_tests)
    total_success = admin_success + user_success
    
    print("\n" + "=" * 50)
    print(f"🏆 TEST SUMMARY: {total_success}/{total_tests} tests passed")
    
    if total_success == total_tests:
        print("✅ All permission tests PASSED! Two-tier system working correctly.")
    else:
        print("❌ Some tests FAILED! Please check the permission system.")
        sys.exit(1)

if __name__ == "__main__":
    print("Make sure the server is running on http://127.0.0.1:5000")
    input("Press Enter to start testing...")
    main()
