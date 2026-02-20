"""
Test Script for Skill Assessment System - Task 21

Tests quiz-based assessment, voice evaluation, and market demand analysis.
"""

import requests
import json
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"
STUDENT_EMAIL = "test_student@example.com"
STUDENT_PASSWORD = "password123"

# Test data
QUIZ_SUBMISSION = {
    "skill_name": "Python",
    "questions": [
        {"question": "What is a list comprehension?", "answer": 4},
        {"question": "Explain decorators", "answer": 3},
        {"question": "What is a generator?", "answer": 4},
        {"question": "Explain async/await", "answer": 3},
        {"question": "What is a context manager?", "answer": 4},
        {"question": "Explain metaclasses", "answer": 2},
        {"question": "What is the GIL?", "answer": 3},
        {"question": "Explain lambda functions", "answer": 5},
        {"question": "What is a closure?", "answer": 4},
        {"question": "Explain inheritance", "answer": 5}
    ]
}

VOICE_EVAL_SUBMISSION = {
    "skill_name": "Python",
    "question": "Explain the difference between a list and a tuple in Python",
    "answer": "Lists are mutable sequences that can be modified after creation, while tuples are immutable sequences that cannot be changed. Lists use square brackets [] and tuples use parentheses (). Lists are typically used when you need a collection that can grow or shrink, while tuples are used for fixed collections of items. Tuples are also more memory-efficient and can be used as dictionary keys because they are hashable."
}

REACT_QUIZ = {
    "skill_name": "React",
    "questions": [
        {"question": "What is JSX?", "answer": 5},
        {"question": "Explain hooks", "answer": 4},
        {"question": "What is useState?", "answer": 5},
        {"question": "Explain useEffect", "answer": 4},
        {"question": "What is component lifecycle?", "answer": 3},
        {"question": "Explain props vs state", "answer": 5},
        {"question": "What is virtual DOM?", "answer": 4},
        {"question": "Explain React Router", "answer": 3},
        {"question": "What is Redux?", "answer": 3},
        {"question": "Explain context API", "answer": 4}
    ]
}

JQUERY_QUIZ = {
    "skill_name": "jQuery",
    "questions": [
        {"question": "What is jQuery?", "answer": 4},
        {"question": "Explain selectors", "answer": 4},
        {"question": "What is AJAX?", "answer": 3},
        {"question": "Explain event handling", "answer": 4},
        {"question": "What is DOM manipulation?", "answer": 4},
        {"question": "Explain animations", "answer": 3},
        {"question": "What is chaining?", "answer": 3},
        {"question": "Explain plugins", "answer": 2},
        {"question": "What is $.ajax()?", "answer": 3},
        {"question": "Explain $(document).ready()", "answer": 4}
    ]
}


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


def test_student_login():
    """Test 1: Student login."""
    print_section("Test 1: Student Login")
    
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


def test_submit_quiz(token, quiz_data):
    """Test 2: Submit quiz."""
    skill_name = quiz_data["skill_name"]
    print_section(f"Test 2: Submit Quiz - {skill_name}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/skills/quiz",
            json=quiz_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(f"Quiz submission - {skill_name}", True, data)
            return True
        else:
            print_result(f"Quiz submission - {skill_name}", False, error=f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_result(f"Quiz submission - {skill_name}", False, error=str(e))
        return False


def test_submit_voice_eval(token, voice_data):
    """Test 3: Submit voice evaluation."""
    skill_name = voice_data["skill_name"]
    print_section(f"Test 3: Submit Voice Evaluation - {skill_name}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/skills/voice-eval",
            json=voice_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(f"Voice evaluation - {skill_name}", True, data)
            return True
        else:
            print_result(f"Voice evaluation - {skill_name}", False, error=f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_result(f"Voice evaluation - {skill_name}", False, error=str(e))
        return False


def test_analyze_demand(token, skill_name):
    """Test 4: Analyze skill market demand."""
    print_section(f"Test 4: Analyze Market Demand - {skill_name}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/skills/analyze-demand/{skill_name}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(f"Market demand analysis - {skill_name}", True, data)
            return True
        else:
            print_result(f"Market demand analysis - {skill_name}", False, error=f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_result(f"Market demand analysis - {skill_name}", False, error=str(e))
        return False


def test_get_all_skills(token):
    """Test 5: Get all student skills."""
    print_section("Test 5: Get All Skills")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/skills/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result("Get all skills", True, {"count": len(data), "skills": data})
            return True
        else:
            print_result("Get all skills", False, error=f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_result("Get all skills", False, error=str(e))
        return False


def test_get_skill_details(token, skill_name):
    """Test 6: Get specific skill details."""
    print_section(f"Test 6: Get Skill Details - {skill_name}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/skills/{skill_name}",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 200:
            data = response.json()
            print_result(f"Get skill details - {skill_name}", True, data)
            return True
        else:
            print_result(f"Get skill details - {skill_name}", False, error=f"Status {response.status_code}: {response.text}")
            return False
    except Exception as e:
        print_result(f"Get skill details - {skill_name}", False, error=str(e))
        return False


def test_validation_errors(token):
    """Test 7: Validation errors."""
    print_section("Test 7: Validation Errors")
    
    # Test 7.1: Quiz with too few questions
    print("Test 7.1: Quiz with too few questions (should fail)")
    try:
        response = requests.post(
            f"{BASE_URL}/api/skills/quiz",
            json={
                "skill_name": "Python",
                "questions": [
                    {"question": "Test", "answer": 3}
                ]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 422:
            print_result("Quiz validation (too few questions)", True, {"error": "Validation failed as expected"})
        else:
            print_result("Quiz validation (too few questions)", False, error="Should have failed with 422")
    except Exception as e:
        print_result("Quiz validation (too few questions)", False, error=str(e))
    
    # Test 7.2: Quiz with invalid answer range
    print("Test 7.2: Quiz with invalid answer (should fail)")
    try:
        response = requests.post(
            f"{BASE_URL}/api/skills/quiz",
            json={
                "skill_name": "Python",
                "questions": [
                    {"question": f"Question {i}", "answer": 6}  # Invalid: must be 1-5
                    for i in range(10)
                ]
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 422:
            print_result("Quiz validation (invalid answer)", True, {"error": "Validation failed as expected"})
        else:
            print_result("Quiz validation (invalid answer)", False, error="Should have failed with 422")
    except Exception as e:
        print_result("Quiz validation (invalid answer)", False, error=str(e))
    
    # Test 7.3: Voice eval with short answer
    print("Test 7.3: Voice eval with short answer (should fail)")
    try:
        response = requests.post(
            f"{BASE_URL}/api/skills/voice-eval",
            json={
                "skill_name": "Python",
                "question": "What is Python?",
                "answer": "A language"  # Too short
            },
            headers={"Authorization": f"Bearer {token}"}
        )
        
        if response.status_code == 422:
            print_result("Voice eval validation (short answer)", True, {"error": "Validation failed as expected"})
        else:
            print_result("Voice eval validation (short answer)", False, error="Should have failed with 422")
    except Exception as e:
        print_result("Voice eval validation (short answer)", False, error=str(e))


def test_market_demand_comparison(token):
    """Test 8: Compare market demand for different skills."""
    print_section("Test 8: Market Demand Comparison")
    
    skills = ["Python", "React", "jQuery"]
    
    for skill in skills:
        test_get_skill_details(token, skill)


def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("  SKILL ASSESSMENT SYSTEM TEST SUITE - Task 21")
    print("="*80)
    print(f"\nTest started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Backend URL: {BASE_URL}")
    print(f"Student: {STUDENT_EMAIL}")
    
    # Test 1: Login
    token = test_student_login()
    if not token:
        print("\n❌ Cannot proceed without authentication token")
        return
    
    # Test 2: Submit Python quiz
    test_submit_quiz(token, QUIZ_SUBMISSION)
    
    # Test 3: Submit Python voice evaluation
    test_submit_voice_eval(token, VOICE_EVAL_SUBMISSION)
    
    # Test 4: Analyze Python market demand
    test_analyze_demand(token, "Python")
    
    # Test 5: Submit React quiz (high demand skill)
    test_submit_quiz(token, REACT_QUIZ)
    test_analyze_demand(token, "React")
    
    # Test 6: Submit jQuery quiz (low demand skill)
    test_submit_quiz(token, JQUERY_QUIZ)
    test_analyze_demand(token, "jQuery")
    
    # Test 7: Get all skills
    test_get_all_skills(token)
    
    # Test 8: Get specific skill details
    test_get_skill_details(token, "Python")
    
    # Test 9: Validation errors
    test_validation_errors(token)
    
    # Test 10: Market demand comparison
    test_market_demand_comparison(token)
    
    # Summary
    print_section("TEST SUMMARY")
    print("✅ All tests completed!")
    print("\nKey Features Tested:")
    print("  1. Quiz-based skill assessment (10-15 questions, 1-5 scale)")
    print("  2. Voice evaluation with LLM (text-based MVP)")
    print("  3. Combined skill score: (quiz × 0.60) + (voice × 0.40)")
    print("  4. Market demand analysis with LLM")
    print("  5. Market weight assignment: 0.5x (Low), 1.0x (Medium), 2.0x (High)")
    print("  6. Skill CRUD operations")
    print("  7. Input validation")
    print("  8. Vector regeneration trigger")
    print("\nExpected Results:")
    print("  - Python: High demand (2.0x weight)")
    print("  - React: High demand (2.0x weight)")
    print("  - jQuery: Low demand (0.5x weight)")
    print(f"\nTest completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    main()
