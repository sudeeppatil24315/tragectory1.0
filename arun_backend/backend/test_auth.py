"""
Test script for authentication endpoints.
Run this after starting the server to test registration and login.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_register():
    """Test user registration"""
    print("\n=== Testing User Registration ===")
    
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "student"
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("✅ Registration successful!")
        return response.json()["access_token"]
    else:
        print("❌ Registration failed!")
        return None


def test_login():
    """Test user login"""
    print("\n=== Testing User Login ===")
    
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": "test@example.com",  # OAuth2 spec uses 'username' field
        "password": "testpassword123"
    }
    
    response = requests.post(url, data=data)  # Note: data, not json for OAuth2
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
        return response.json()["access_token"]
    else:
        print("❌ Login failed!")
        return None


def test_get_current_user(token):
    """Test getting current user info with token"""
    print("\n=== Testing Get Current User ===")
    
    url = f"{BASE_URL}/api/auth/me"
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(url, headers=headers)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 200:
        print("✅ Get current user successful!")
    else:
        print("❌ Get current user failed!")


def test_invalid_credentials():
    """Test login with invalid credentials"""
    print("\n=== Testing Invalid Credentials ===")
    
    url = f"{BASE_URL}/api/auth/login"
    data = {
        "username": "wrong@example.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(url, data=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 401:
        print("✅ Invalid credentials correctly rejected!")
    else:
        print("❌ Invalid credentials test failed!")


def test_duplicate_registration():
    """Test registering with existing email"""
    print("\n=== Testing Duplicate Registration ===")
    
    url = f"{BASE_URL}/api/auth/register"
    data = {
        "email": "test@example.com",
        "password": "testpassword123",
        "role": "student"
    }
    
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 400:
        print("✅ Duplicate registration correctly rejected!")
    else:
        print("❌ Duplicate registration test failed!")


if __name__ == "__main__":
    print("=" * 60)
    print("AUTHENTICATION SYSTEM TEST")
    print("=" * 60)
    print("\nMake sure the server is running: python -m uvicorn app.main:app --reload")
    print("\nStarting tests...")
    print()
    
    # Test 1: Register new user
    token = test_register()
    
    # Test 2: Login with registered user
    if token:
        token = test_login()
    
    # Test 3: Get current user info
    if token:
        test_get_current_user(token)
    
    # Test 4: Invalid credentials
    test_invalid_credentials()
    
    # Test 5: Duplicate registration
    test_duplicate_registration()
    
    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)
