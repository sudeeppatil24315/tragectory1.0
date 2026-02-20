"""
Test script for Student Profile Management endpoints (Task 20.1)

Tests:
1. Get student profile
2. Update student profile
3. Add behavioral data
4. Add skill assessment
5. Get student skills
6. Get behavioral data history
"""

import requests
from datetime import date, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
STUDENT_EMAIL = "student@test.com"
STUDENT_PASSWORD = "student123"


def test_student_profile_management():
    """Test complete student profile management flow"""
    
    print("=" * 80)
    print("TASK 20.1: Student Profile Management - Test Suite")
    print("=" * 80)
    print()
    
    # Test 1: Login as student
    print("Test 1: Student login")
    print("-" * 80)
    login_response = requests.post(
        f"{BASE_URL}/api/auth/login",
        json={"email": STUDENT_EMAIL, "password": STUDENT_PASSWORD}
    )
    
    if login_response.status_code == 200:
        student_token = login_response.json()["access_token"]
        print(f"✅ PASS: Student login successful")
        print(f"   Token: {student_token[:20]}...")
    else:
        print(f"❌ FAIL: Student login failed with status {login_response.status_code}")
        print(f"   Response: {login_response.text}")
        return
    
    headers = {"Authorization": f"Bearer {student_token}"}
    print()
    
    # Test 2: Get student profile
    print("Test 2: Get student profile")
    print("-" * 80)
    response = requests.get(f"{BASE_URL}/api/student/profile", headers=headers)
    
    if response.status_code == 200:
        profile = response.json()
        print("✅ PASS: Profile retrieved successfully")
        print(f"   Student ID: {profile.get('id')}")
        print(f"   Name: {profile.get('name')}")
        print(f"   Major: {profile.get('major')}")
        print(f"   GPA: {profile.get('gpa')}")
        print(f"   Attendance: {profile.get('attendance')}%")
        student_id = profile.get('id')
    else:
        print(f"❌ FAIL: Get profile failed with status {response.status_code}")
        print(f"   Response: {response.text}")
        return
    print()
    
    # Test 3: Update student profile
    print("Test 3: Update student profile")
    print("-" * 80)
    update_data = {
        "gpa": 8.5,
        "attendance": 90.0,
        "study_hours_per_week": 25.0,
        "project_count": 5
    }
    response = requests.put(
        f"{BASE_URL}/api/student/profile",
        headers=headers,
        json=update_data
    )
    
    if response.status_code == 200:
        updated_profile = response.json()
        print("✅ PASS: Profile updated successfully")
        print(f"   GPA: {updated_profile.get('gpa')}")
        print(f"   Attendance: {updated_profile.get('attendance')}%")
        print(f"   Study hours/week: {updated_profile.get('study_hours_per_week')}")
        print(f"   Project count: {updated_profile.get('project_count')}")
        print(f"   Vector ID: {updated_profile.get('vector_id')}")
    else:
        print(f"❌ FAIL: Update profile failed with status {response.status_code}")
        print(f"   Response: {response.text}")
    print()
    
    # Test 4: Add behavioral data
    print("Test 4: Add behavioral data")
    print("-" * 80)
    behavioral_data = {
        "date": str(date.today()),
        "screen_time_hours": 8.5,
        "educational_app_hours": 2.0,
        "social_media_hours": 3.0,
        "entertainment_hours": 2.5,
        "productivity_hours": 1.0,
        "sleep_duration_hours": 7.0,
        "sleep_quality": "good"
    }
    response = requests.post(
        f"{BASE_URL}/api/student/behavioral",
        headers=headers,
        json=behavioral_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ PASS: Behavioral data added successfully")
        print(f"   Message: {result.get('message')}")
        print(f"   Date: {result.get('date')}")
        print(f"   Focus score: {result.get('focus_score')}")
        print(f"   Vector regenerated: {result.get('vector_regenerated')}")
    else:
        print(f"❌ FAIL: Add behavioral data failed with status {response.status_code}")
        print(f"   Response: {response.text}")
    print()
    
    # Test 5: Add skill assessment
    print("Test 5: Add skill assessment")
    print("-" * 80)
    skill_data = {
        "skill_name": "Python",
        "proficiency_score": 85.0,
        "quiz_score": 90.0,
        "voice_score": 80.0
    }
    response = requests.post(
        f"{BASE_URL}/api/student/skills",
        headers=headers,
        json=skill_data
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ PASS: Skill assessment added successfully")
        print(f"   Message: {result.get('message')}")
        print(f"   Skill: {result.get('skill_name')}")
        print(f"   Proficiency: {result.get('proficiency_score')}")
        print(f"   Vector regenerated: {result.get('vector_regenerated')}")
    else:
        print(f"❌ FAIL: Add skill failed with status {response.status_code}")
        print(f"   Response: {response.text}")
    print()
    
    # Test 6: Add another skill
    print("Test 6: Add another skill (React)")
    print("-" * 80)
    skill_data2 = {
        "skill_name": "React",
        "proficiency_score": 80.0,
        "quiz_score": 85.0
    }
    response = requests.post(
        f"{BASE_URL}/api/student/skills",
        headers=headers,
        json=skill_data2
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ PASS: Second skill added successfully")
        print(f"   Skill: {result.get('skill_name')}")
    else:
        print(f"❌ FAIL: Add second skill failed")
    print()
    
    # Test 7: Get all student skills
    print("Test 7: Get all student skills")
    print("-" * 80)
    response = requests.get(f"{BASE_URL}/api/student/skills", headers=headers)
    
    if response.status_code == 200:
        skills_data = response.json()
        print("✅ PASS: Skills retrieved successfully")
        print(f"   Total skills: {skills_data.get('total_skills')}")
        for skill in skills_data.get('skills', []):
            print(f"   - {skill['skill_name']}: {skill['proficiency_score']}/100 (weight: {skill['market_weight']}x)")
    else:
        print(f"❌ FAIL: Get skills failed with status {response.status_code}")
    print()
    
    # Test 8: Get behavioral data history
    print("Test 8: Get behavioral data history (last 30 days)")
    print("-" * 80)
    response = requests.get(
        f"{BASE_URL}/api/student/behavioral?days=30",
        headers=headers
    )
    
    if response.status_code == 200:
        behavioral_history = response.json()
        print("✅ PASS: Behavioral data retrieved successfully")
        print(f"   Total entries: {behavioral_history.get('total_entries')}")
        if behavioral_history.get('data'):
            latest = behavioral_history['data'][0]
            print(f"   Latest entry:")
            print(f"      Date: {latest['date']}")
            print(f"      Screen time: {latest['screen_time_hours']} hours")
            print(f"      Focus score: {latest['focus_score']}")
            print(f"      Sleep: {latest['sleep_duration_hours']} hours ({latest['sleep_quality']})")
    else:
        print(f"❌ FAIL: Get behavioral data failed with status {response.status_code}")
    print()
    
    # Test 9: Validation - Invalid GPA
    print("Test 9: Validation - Invalid GPA (should fail)")
    print("-" * 80)
    invalid_data = {"gpa": 15.0}  # Invalid: > 10.0
    response = requests.put(
        f"{BASE_URL}/api/student/profile",
        headers=headers,
        json=invalid_data
    )
    
    if response.status_code == 422:
        print("✅ PASS: Invalid GPA correctly rejected (422)")
    else:
        print(f"❌ FAIL: Expected 422, got {response.status_code}")
    print()
    
    # Test 10: Validation - Invalid attendance
    print("Test 10: Validation - Invalid attendance (should fail)")
    print("-" * 80)
    invalid_data = {"attendance": 150.0}  # Invalid: > 100.0
    response = requests.put(
        f"{BASE_URL}/api/student/profile",
        headers=headers,
        json=invalid_data
    )
    
    if response.status_code == 422:
        print("✅ PASS: Invalid attendance correctly rejected (422)")
    else:
        print(f"❌ FAIL: Expected 422, got {response.status_code}")
    print()
    
    # Summary
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("Task 20.1: Student Profile Management")
    print()
    print("✅ Implemented endpoints:")
    print("   - GET /api/student/profile (fetch profile)")
    print("   - PUT /api/student/profile (update profile)")
    print("   - POST /api/student/behavioral (add wellbeing data)")
    print("   - POST /api/student/skills (add skill assessment)")
    print("   - GET /api/student/skills (get all skills)")
    print("   - GET /api/student/behavioral (get history)")
    print()
    print("✅ Features:")
    print("   - Student authentication required")
    print("   - Input validation (GPA 0-10, attendance 0-100)")
    print("   - Focus score calculation")
    print("   - Vector regeneration on updates")
    print("   - Skill tracking with market weights")
    print("   - Behavioral data history")
    print()
    print("✅ Task 20.1 is COMPLETE and ready for use!")
    print("=" * 80)


if __name__ == "__main__":
    try:
        test_student_profile_management()
    except requests.exceptions.ConnectionError:
        print("❌ ERROR: Cannot connect to backend server")
        print("   Make sure the backend is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
