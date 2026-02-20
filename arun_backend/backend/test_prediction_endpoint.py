"""
Test script for the prediction endpoint

This script tests the /api/predict endpoint to ensure it works correctly.
Run this after starting the backend server.
"""

import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
TEST_EMAIL = "test_student@example.com"
TEST_PASSWORD = "testpass123"

def test_prediction_endpoint():
    """Test the prediction endpoint with a test student"""
    
    print("=" * 60)
    print("TESTING PREDICTION ENDPOINT")
    print("=" * 60)
    
    # Step 1: Register a test user (or login if already exists)
    print("\n1. Registering/Logging in test user...")
    
    # Try to register
    register_response = requests.post(
        f"{BASE_URL}/api/auth/register",
        json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "role": "student"
        }
    )
    
    if register_response.status_code == 201:
        print("✓ User registered successfully")
        token = register_response.json()["access_token"]
    elif register_response.status_code == 400:
        # User already exists, try to login
        print("  User already exists, logging in...")
        login_response = requests.post(
            f"{BASE_URL}/api/auth/login",
            json={
                "email": TEST_EMAIL,
                "password": TEST_PASSWORD
            }
        )
        
        if login_response.status_code == 200:
            print("✓ User logged in successfully")
            token = login_response.json()["access_token"]
        else:
            print(f"✗ Login failed: {login_response.status_code}")
            print(f"  Response: {login_response.text}")
            return
    else:
        print(f"✗ Registration failed: {register_response.status_code}")
        print(f"  Response: {register_response.text}")
        return
    
    # Step 2: Call prediction endpoint
    print("\n2. Calling prediction endpoint...")
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    prediction_response = requests.post(
        f"{BASE_URL}/api/predict",
        headers=headers,
        json={}  # Empty body means predict for current user
    )
    
    print(f"   Status Code: {prediction_response.status_code}")
    
    if prediction_response.status_code == 200:
        print("✓ Prediction successful!")
        result = prediction_response.json()
        
        print("\n" + "=" * 60)
        print("PREDICTION RESULTS")
        print("=" * 60)
        print(f"\nTrajectory Score: {result['trajectory_score']:.1f}/100")
        print(f"Predicted Tier: {result['predicted_tier']}")
        print(f"Confidence: {result['confidence']:.2f} (±{result['margin_of_error']:.1f})")
        print(f"Trend: {result['trend']} (velocity: {result['velocity']:.2f})")
        
        print(f"\nComponent Scores:")
        print(f"  Academic:    {result['component_scores']['academic']:.1f}")
        print(f"  Behavioral:  {result['component_scores']['behavioral']:.1f}")
        print(f"  Skills:      {result['component_scores']['skills']:.1f}")
        
        print(f"\nComponent Weights:")
        print(f"  Academic:    {result['component_weights']['academic']:.0%}")
        print(f"  Behavioral:  {result['component_weights']['behavioral']:.0%}")
        print(f"  Skills:      {result['component_weights']['skills']:.0%}")
        
        print(f"\nInterpretation: {result['interpretation']}")
        print(f"Similar Alumni: {result['similar_alumni_count']}")
        
        if result['similar_alumni']:
            print("\nTop Similar Alumni:")
            for i, alumni in enumerate(result['similar_alumni'][:3], 1):
                print(f"  {i}. Similarity: {alumni['similarity_score']:.2f}, "
                      f"Tier: {alumni['company_tier']}, "
                      f"Score: {alumni['outcome_score']:.1f}")
        
        print("\n" + "=" * 60)
        print("✓ TEST PASSED")
        print("=" * 60)
        
    elif prediction_response.status_code == 404:
        print("✗ Student profile not found")
        print("  This is expected if no student profile exists for this user")
        print("  You need to create a student profile first")
        print(f"  Response: {prediction_response.text}")
    elif prediction_response.status_code == 503:
        print("✗ Service unavailable (Qdrant not running?)")
        print(f"  Response: {prediction_response.text}")
    else:
        print(f"✗ Prediction failed: {prediction_response.status_code}")
        print(f"  Response: {prediction_response.text}")
    
    # Step 3: Test health check endpoint
    print("\n3. Testing health check endpoint...")
    
    health_response = requests.get(f"{BASE_URL}/api/predict/health")
    
    if health_response.status_code == 200:
        health = health_response.json()
        print(f"✓ Health check successful")
        print(f"  Status: {health['status']}")
        print(f"  Qdrant Available: {health['qdrant_available']}")
        print(f"  Message: {health['message']}")
    else:
        print(f"✗ Health check failed: {health_response.status_code}")


if __name__ == "__main__":
    try:
        test_prediction_endpoint()
    except requests.exceptions.ConnectionError:
        print("\n✗ ERROR: Could not connect to backend server")
        print("  Make sure the backend is running on http://localhost:8000")
        print("  Run: cd arun_backend/backend && python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
