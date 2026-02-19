"""
Test the new POST endpoints to verify they work correctly
"""
import requests
import json

BASE_URL = "http://localhost:8000"

print("=" * 60)
print("TESTING POST ENDPOINTS")
print("=" * 60)

# Test 1: Fetch Activities
print("\n[TEST 1] POST /activities/fetch")
print("-" * 40)

url = f"{BASE_URL}/activities/fetch"
headers = {"Content-Type": "application/json"}
data = {
    "student_id": 1,
    "activity_date": "2026-02-17"
}

print(f"URL: {url}")
print(f"Headers: {headers}")
print(f"Body: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        activities = response.json()
        print(f"✓ Success! Found {len(activities)} activities")
        for act in activities:
            print(f"  - {act['title']} ({act['activity_type']})")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"✗ Exception: {e}")

# Test 2: Today's Schedule
print("\n[TEST 2] POST /activities/schedule/today")
print("-" * 40)

url = f"{BASE_URL}/activities/schedule/today"
data = {"student_id": 1}

print(f"URL: {url}")
print(f"Body: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        schedule = response.json()
        print(f"✓ Success! Found {len(schedule)} schedule items")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"✗ Exception: {e}")

# Test 3: Pending Todos
print("\n[TEST 3] POST /activities/todos/pending")
print("-" * 40)

url = f"{BASE_URL}/activities/todos/pending"
data = {"student_id": 1}

print(f"URL: {url}")
print(f"Body: {json.dumps(data, indent=2)}")

try:
    response = requests.post(url, json=data, headers=headers)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        todos = response.json()
        print(f"✓ Success! Found {len(todos)} pending todos")
    else:
        print(f"✗ Error: {response.status_code}")
        print(f"Response: {response.text}")
except Exception as e:
    print(f"✗ Exception: {e}")

print("\n" + "=" * 60)
print("TESTING COMPLETE")
print("=" * 60)
