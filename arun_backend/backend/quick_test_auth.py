import requests
import json

BASE_URL = "http://localhost:8000"

print("Testing Authentication System...")
print()

# Test 1: Register
print("1. Testing Registration...")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": "quicktest@example.com",
            "password": "test123456",
            "role": "student"
        }
    )
    if response.status_code == 200:
        print("✅ Registration successful!")
        token = response.json()["access_token"]
    else:
        print(f"❌ Registration failed: {response.status_code}")
        print(response.text)
        token = None
except Exception as e:
    print(f"❌ Error: {e}")
    token = None

print()

# Test 2: Login
print("2. Testing Login...")
try:
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data={
            "username": "quicktest@example.com",
            "password": "test123456"
        }
    )
    if response.status_code == 200:
        print("✅ Login successful!")
        token = response.json()["access_token"]
    else:
        print(f"❌ Login failed: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"❌ Error: {e}")

print()

# Test 3: Get current user
if token:
    print("3. Testing Get Current User...")
    try:
        response = requests.get(
            f"{BASE_URL}/api/auth/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        if response.status_code == 200:
            user = response.json()
            print(f"✅ Got user info: {user['email']} (role: {user['role']})")
        else:
            print(f"❌ Get user failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {e}")

print()
print("=" * 60)
print("Authentication tests complete!")
print("=" * 60)
