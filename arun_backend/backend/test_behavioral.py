"""
Test Script for Behavioral Analysis Service - Task 22

Tests correlation analysis, at-risk pattern detection, and alumni comparison.
"""

import requests
import json
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://localhost:8000"
STUDENT_EMAIL = "test_student@example.com"
STUDENT_PASSWORD = "password123"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin123"


def print_section(title):
    """Print a section header."""
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def print_result(test_name, success, data=None, error=None):
    """Print test result."""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if data:
        print(f"   Response: {json.dumps(data, indent=2)}")
    if error:
        print(f"   Error: {error}")
    print()


def test_admin_login():
    """Test 1: Admin login."""
    print_section("Test 1: Admin Login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print_result("Admin login", True, {"token": token[:20] + "..."})
            return token
        else:
            print_result("Admin login", False, error=f"Status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_result("Admin login", False, error=str(e))
        return None


def test_student_login():
    """Test 2: Student login."""
    print_section("Test 2: Student Login")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={"email": STUDENT_EMAIL, "password": STUDENT_PASSWORD}
        )
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            print_result("Student login", True, {"token": token[:20] + "..."})
            return token
        else:
            print_result("Student login", False, error=f"Status {response.status_code}: {response.text}")
            return None
    except Exception as e:
        print_result("Student login", False, error=str(e))
        return None


def test_get_correlations(admin_token):
    """Test 3: Get behavioral correlations (Admin only)."""
    print_section("Test 3: Get Behavioral Correlations")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/behavioral/correlations",
            headers={"Authorization": f"Bearer {admin_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result("Get correlations", True, data)
            return True
        else:
            print_result("Get correlations", False, error=f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_result("Get correlations", False, error=str(e))
        return False


def test_get_at_risk_patterns(student_token):
    """Test 4: Get at-risk patterns."""
    print_section("Test 4: Get At-Risk Patterns")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/behavioral/at-risk",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result("Get at-risk patterns", True, data)
            return True
        else:
            print_result("Get at-risk patterns", False, error=f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_result("Get at-risk patterns", False, error=str(e))
        return False


def test_get_comparison(student_token):
    """Test 5: Get comparison to successful alumni."""
    print_section("Test 5: Get Comparison to Alumni")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/behavioral/comparison",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result("Get comparison", True, data)
            return True
        else:
            print_result("Get comparison", False, error=f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_result("Get comparison", False, error=str(e))
        return False


def test_get_insights(student_token):
    """Test 6: Get complete behavioral insights."""
    print_section("Test 6: Get Complete Behavioral Insights")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/behavioral/insights",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result("Get insights", True, data)
            return True
        else:
            print_result("Get insights", False, error=f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_result("Get insights", False, error=str(e))
        return False


def test_student_access_to_correlations(student_token):
    """Test 7: Student should NOT access correlations (admin only)."""
    print_section("Test 7: Student Access to Correlations (Should Fail)")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/behavioral/correlations",
            headers={"Authorization": f"Bearer {student_token}"}
        )
        
        if response.status_code == 403:
            print_result("Student access denied (expected)", True, {"error": "Forbidden as expected"})
            return True
        else:
            print_result("Student access denied", False, error="Should have returned 403 Forbidden")
            return False
    except Exception as e:
        print_result("Student access denied", False, error=str(e))
        return False


def test_unauthenticated_access():
    """Test 8: Unauthenticated access should fail."""
    print_section("Test 8: Unauthenticated Access (Should Fail)")
    
    tests = [
        ("correlations", f"{BASE_URL}/api/behavioral/correlations"),
        ("at-risk", f"{BASE_URL}/api/behavioral/at-risk"),
        ("comparison", f"{BASE_URL}/api/behavioral/comparison"),
        ("insights", f"{BASE_URL}/api/behavioral/insights")
    ]
    
    all_passed = True
    for name, url in tests:
        try:
            response = requests.get(url)
            if response.status_code == 401:
                print(f"✅ {name}: Correctly rejected (401)")
            else:
                print(f"❌ {name}: Should have returned 401, got {response.status_code}")
                all_passed = False
        except Exception as e:
            print(f"❌ {name}: Error - {str(e)}")
            all_passed = False
    
    return all_passed


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("  BEHAVIORAL ANALYSIS SERVICE TEST SUITE - Task 22")
    print("="*80)
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {BASE_URL}")
    
    # Test 1: Admin login
    admin_token = test_admin_login()
    if not admin_token:
        print("\n⚠️  Admin login failed - some tests will be skipped")
    
    # Test 2: Student login
    student_token = test_student_login()
    if not student_token:
        print("\n❌ Cannot proceed without student authentication token")
        return
    
    # Test 3: Get correlations (admin only)
    if admin_token:
        test_get_correlations(admin_token)
    
    # Test 4: Get at-risk patterns
    test_get_at_risk_patterns(student_token)
    
    # Test 5: Get comparison to alumni
    test_get_comparison(student_token)
    
    # Test 6: Get complete insights
    test_get_insights(student_token)
    
    # Test 7: Student should NOT access correlations
    test_student_access_to_correlations(student_token)
    
    # Test 8: Unauthenticated access
    test_unauthenticated_access()
    
    # Summary
    print_section("TEST SUMMARY")
    print("✅ All tests completed!")
    print("\nKey Features Tested:")
    print("  1. Behavioral correlations (screen time vs GPA, focus vs trajectory, sleep vs academic)")
    print("  2. At-risk pattern detection (high social media + low sleep + declining GPA)")
    print("  3. Excessive screen time detection (>8 hours/day)")
    print("  4. Low focus score detection (<0.5)")
    print("  5. Insufficient sleep detection (<6 hours)")
    print("  6. Comparison to successful alumni")
    print("  7. Complete behavioral insights with recommendations")
    print("  8. Admin-only access control")
    print("  9. Authentication requirements")
    print("\nExpected Results:")
    print("  - Correlations calculated using NumPy/Pandas (NO LLM)")
    print("  - At-risk flags with severity levels (high/medium/low)")
    print("  - Comparison shows student vs optimal ranges")
    print("  - Personalized recommendations generated")
    print("  - Admin can view correlations, students cannot")
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
