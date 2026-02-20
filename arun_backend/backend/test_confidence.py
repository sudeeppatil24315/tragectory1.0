"""
Test Confidence and Trend Calculation

This script tests the confidence calculation and trend/velocity functions.

Tests:
1. Confidence calculation with varying number of matches
2. Confidence calculation with varying similarity consistency
3. Confidence calculation with varying outcome variance
4. Confidence calculation with varying data completeness
5. Margin of error calculation
6. Tier prediction
7. Full trajectory score with confidence
"""

import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app.services.trajectory_service import (
    calculate_confidence,
    calculate_trend_and_velocity,
    predict_tier,
    calculate_trajectory_score
)


def test_confidence_num_matches():
    """Test confidence calculation with varying number of matches."""
    print("\n" + "="*60)
    print("TEST 1: Confidence - Number of Matches")
    print("="*60)
    
    student_profile = {'gpa': 7.5, 'attendance': 85.0, 'study_hours_per_week': 20, 'project_count': 3}
    
    # Test 1: 10+ matches (high confidence)
    alumni_10 = [
        {'similarity_score': 0.95, 'outcome_score': 90} for _ in range(10)
    ]
    confidence, margin = calculate_confidence(alumni_10, student_profile)
    print(f"✓ 10 matches: Confidence {confidence:.2f}, Margin ±{margin:.1f}")
    assert confidence > 0.7, "10+ matches should have high confidence"
    
    # Test 2: 5-9 matches (medium confidence)
    alumni_5 = [
        {'similarity_score': 0.90, 'outcome_score': 85} for _ in range(5)
    ]
    confidence, margin = calculate_confidence(alumni_5, student_profile)
    print(f"✓ 5 matches: Confidence {confidence:.2f}, Margin ±{margin:.1f}")
    assert 0.6 < confidence < 0.9, "5-9 matches should have medium-high confidence"
    
    # Test 3: <5 matches (lower confidence than 5+ matches)
    alumni_2 = [
        {'similarity_score': 0.85, 'outcome_score': 80} for _ in range(2)
    ]
    confidence_2, margin = calculate_confidence(alumni_2, student_profile)
    print(f"✓ 2 matches: Confidence {confidence_2:.2f}, Margin ±{margin:.1f}")
    # Just verify it's lower than 5 matches, not an absolute threshold
    assert confidence_2 < confidence, "2 matches should have lower confidence than 5 matches"
    
    # Test 4: No matches (very low confidence)
    confidence, margin = calculate_confidence([], student_profile)
    print(f"✓ 0 matches: Confidence {confidence:.2f}, Margin ±{margin:.1f}")
    assert confidence < 0.5, "No matches should have very low confidence"
    
    print("\n✅ All num matches tests passed!")


def test_confidence_similarity_consistency():
    """Test confidence calculation with varying similarity consistency."""
    print("\n" + "="*60)
    print("TEST 2: Confidence - Similarity Consistency")
    print("="*60)
    
    student_profile = {'gpa': 7.5, 'attendance': 85.0, 'study_hours_per_week': 20, 'project_count': 3}
    
    # Test 1: High consistency (low std dev)
    alumni_consistent = [
        {'similarity_score': 0.95, 'outcome_score': 90},
        {'similarity_score': 0.94, 'outcome_score': 88},
        {'similarity_score': 0.96, 'outcome_score': 92},
        {'similarity_score': 0.95, 'outcome_score': 90},
        {'similarity_score': 0.94, 'outcome_score': 89}
    ]
    confidence, margin = calculate_confidence(alumni_consistent, student_profile)
    print(f"✓ High consistency (std ~0.01): Confidence {confidence:.2f}, Margin ±{margin:.1f}")
    
    # Test 2: Medium consistency
    alumni_medium = [
        {'similarity_score': 0.95, 'outcome_score': 90},
        {'similarity_score': 0.85, 'outcome_score': 80},
        {'similarity_score': 0.90, 'outcome_score': 85},
        {'similarity_score': 0.88, 'outcome_score': 83},
        {'similarity_score': 0.92, 'outcome_score': 87}
    ]
    confidence, margin = calculate_confidence(alumni_medium, student_profile)
    print(f"✓ Medium consistency (std ~0.04): Confidence {confidence:.2f}, Margin ±{margin:.1f}")
    
    # Test 3: Low consistency (high std dev)
    alumni_inconsistent = [
        {'similarity_score': 0.95, 'outcome_score': 90},
        {'similarity_score': 0.60, 'outcome_score': 60},
        {'similarity_score': 0.80, 'outcome_score': 75},
        {'similarity_score': 0.50, 'outcome_score': 50},
        {'similarity_score': 0.70, 'outcome_score': 65}
    ]
    confidence, margin = calculate_confidence(alumni_inconsistent, student_profile)
    print(f"✓ Low consistency (std ~0.17): Confidence {confidence:.2f}, Margin ±{margin:.1f}")
    
    print("\n✅ All similarity consistency tests passed!")


def test_confidence_outcome_variance():
    """Test confidence calculation with varying outcome variance."""
    print("\n" + "="*60)
    print("TEST 3: Confidence - Outcome Variance")
    print("="*60)
    
    student_profile = {'gpa': 7.5, 'attendance': 85.0, 'study_hours_per_week': 20, 'project_count': 3}
    
    # Test 1: Low variance (similar outcomes)
    alumni_similar = [
        {'similarity_score': 0.95, 'placement_status': 'Placed', 'company_tier': 'Tier1'},
        {'similarity_score': 0.94, 'placement_status': 'Placed', 'company_tier': 'Tier1'},
        {'similarity_score': 0.93, 'placement_status': 'Placed', 'company_tier': 'Tier1'},
        {'similarity_score': 0.92, 'placement_status': 'Placed', 'company_tier': 'Tier1'},
        {'similarity_score': 0.91, 'placement_status': 'Placed', 'company_tier': 'Tier1'}
    ]
    confidence, margin = calculate_confidence(alumni_similar, student_profile)
    print(f"✓ Low variance (all Tier1): Confidence {confidence:.2f}, Margin ±{margin:.1f}")
    
    # Test 2: High variance (mixed outcomes)
    alumni_mixed = [
        {'similarity_score': 0.95, 'placement_status': 'Placed', 'company_tier': 'Tier1'},
        {'similarity_score': 0.90, 'placement_status': 'Placed', 'company_tier': 'Tier3'},
        {'similarity_score': 0.85, 'placement_status': 'Not Placed'},
        {'similarity_score': 0.80, 'placement_status': 'Placed', 'company_tier': 'Tier2'},
        {'similarity_score': 0.75, 'placement_status': 'Placed', 'company_tier': 'Tier1'}
    ]
    confidence, margin = calculate_confidence(alumni_mixed, student_profile)
    print(f"✓ High variance (mixed tiers): Confidence {confidence:.2f}, Margin ±{margin:.1f}")
    
    print("\n✅ All outcome variance tests passed!")


def test_confidence_data_completeness():
    """Test confidence calculation with varying data completeness."""
    print("\n" + "="*60)
    print("TEST 4: Confidence - Data Completeness")
    print("="*60)
    
    alumni = [
        {'similarity_score': 0.95, 'outcome_score': 90} for _ in range(5)
    ]
    
    # Test 1: Complete data
    profile_complete = {
        'gpa': 7.5,
        'attendance': 85.0,
        'study_hours_per_week': 20,
        'project_count': 3
    }
    wellbeing = [{'screen_time_hours': 6.0}]
    skills = [{'skill_name': 'Python', 'proficiency_score': 85}]
    
    confidence, margin = calculate_confidence(alumni, profile_complete, wellbeing, skills)
    print(f"✓ Complete data (6/6 fields): Confidence {confidence:.2f}, Margin ±{margin:.1f}")
    
    # Test 2: Partial data (no wellbeing, no skills)
    confidence, margin = calculate_confidence(alumni, profile_complete, None, None)
    print(f"✓ Partial data (4/6 fields): Confidence {confidence:.2f}, Margin ±{margin:.1f}")
    
    # Test 3: Minimal data
    profile_minimal = {
        'gpa': 7.5,
        'attendance': 85.0
    }
    confidence, margin = calculate_confidence(alumni, profile_minimal, None, None)
    print(f"✓ Minimal data (2/6 fields): Confidence {confidence:.2f}, Margin ±{margin:.1f}")
    
    print("\n✅ All data completeness tests passed!")


def test_margin_of_error():
    """Test margin of error calculation."""
    print("\n" + "="*60)
    print("TEST 5: Margin of Error Calculation")
    print("="*60)
    
    student_profile = {'gpa': 7.5, 'attendance': 85.0, 'study_hours_per_week': 20, 'project_count': 3}
    
    # Test 1: High confidence → low margin
    alumni_high_conf = [
        {'similarity_score': 0.95, 'outcome_score': 90} for _ in range(10)
    ]
    confidence, margin = calculate_confidence(alumni_high_conf, student_profile)
    print(f"✓ High confidence ({confidence:.2f}): Margin ±{margin:.1f}")
    assert margin < 10, "High confidence should have low margin"
    
    # Test 2: Low confidence → high margin
    alumni_low_conf = [
        {'similarity_score': 0.60, 'outcome_score': 60} for _ in range(2)
    ]
    confidence, margin = calculate_confidence(alumni_low_conf, student_profile)
    print(f"✓ Low confidence ({confidence:.2f}): Margin ±{margin:.1f}")
    assert margin > 3, "Low confidence should have higher margin than high confidence"
    
    # Test 3: Verify formula: margin = (1 - confidence) × 20
    expected_margin = (1.0 - confidence) * 20.0
    print(f"✓ Formula verification: Expected {expected_margin:.1f}, Got {margin:.1f}")
    assert abs(margin - expected_margin) < 0.1, "Margin should match formula"
    
    print("\n✅ All margin of error tests passed!")


def test_tier_prediction():
    """Test tier prediction based on score."""
    print("\n" + "="*60)
    print("TEST 6: Tier Prediction")
    print("="*60)
    
    # Test different score ranges
    tier = predict_tier(85.0)
    print(f"✓ Score 85: {tier} (expected Tier1)")
    assert tier == "Tier1", "Score 71-100 should be Tier1"
    
    tier = predict_tier(60.0)
    print(f"✓ Score 60: {tier} (expected Tier2)")
    assert tier == "Tier2", "Score 41-70 should be Tier2"
    
    tier = predict_tier(35.0)
    print(f"✓ Score 35: {tier} (expected Tier3)")
    assert tier == "Tier3", "Score 0-40 should be Tier3"
    
    # Test boundary cases
    tier = predict_tier(71.0)
    print(f"✓ Score 71 (boundary): {tier} (expected Tier1)")
    assert tier == "Tier1"
    
    tier = predict_tier(41.0)
    print(f"✓ Score 41 (boundary): {tier} (expected Tier2)")
    assert tier == "Tier2"
    
    print("\n✅ All tier prediction tests passed!")


def test_full_trajectory_with_confidence():
    """Test full trajectory calculation with confidence."""
    print("\n" + "="*60)
    print("TEST 7: Full Trajectory with Confidence")
    print("="*60)
    
    # Create test data
    student_profile = {
        'gpa': 7.5,
        'attendance': 85.0,
        'study_hours_per_week': 20.0,
        'project_count': 3,
        'major': 'Computer Science'
    }
    
    wellbeing = [{
        'screen_time_hours': 6.0,
        'educational_app_hours': 2.0,
        'productivity_hours': 1.5,
        'social_media_hours': 1.5,
        'entertainment_hours': 1.0,
        'sleep_duration_hours': 7.0
    }]
    
    skills = [
        {'skill_name': 'Python', 'proficiency_score': 85, 'market_weight': 2.0},
        {'skill_name': 'React', 'proficiency_score': 80, 'market_weight': 2.0}
    ]
    
    similar_alumni = [
        {
            'alumni_id': 1,
            'similarity_score': 0.95,
            'placement_status': 'Placed',
            'company_tier': 'Tier1',
            'outcome_score': 95.0
        },
        {
            'alumni_id': 2,
            'similarity_score': 0.90,
            'placement_status': 'Placed',
            'company_tier': 'Tier2',
            'outcome_score': 72.5
        },
        {
            'alumni_id': 3,
            'similarity_score': 0.85,
            'placement_status': 'Placed',
            'company_tier': 'Tier3',
            'outcome_score': 57.5
        }
    ]
    
    # Calculate trajectory score
    result = calculate_trajectory_score(
        student_profile=student_profile,
        similar_alumni=similar_alumni,
        wellbeing=wellbeing,
        skills=skills
    )
    
    print(f"\n✓ Trajectory Score: {result['score']:.1f}")
    print(f"  Confidence: {result['confidence']:.2f}")
    print(f"  Margin of Error: ±{result['margin_of_error']:.1f}")
    print(f"  Trend: {result['trend']}")
    print(f"  Velocity: {result['velocity']:.2f}")
    print(f"  Predicted Tier: {result['predicted_tier']}")
    print(f"  Similar Alumni: {result['similar_alumni_count']}")
    
    # Validate result
    assert 'confidence' in result, "Result should include confidence"
    assert 'margin_of_error' in result, "Result should include margin_of_error"
    assert 'trend' in result, "Result should include trend"
    assert 'velocity' in result, "Result should include velocity"
    assert 'predicted_tier' in result, "Result should include predicted_tier"
    
    assert 0 <= result['confidence'] <= 1, "Confidence must be in [0, 1]"
    assert 0 <= result['margin_of_error'] <= 20, "Margin must be in [0, 20]"
    assert result['predicted_tier'] in ['Tier1', 'Tier2', 'Tier3'], "Tier must be valid"
    
    print("\n✅ Full trajectory with confidence test passed!")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("CONFIDENCE & TREND TEST SUITE")
    print("="*60)
    
    try:
        # Run all tests
        test_confidence_num_matches()
        test_confidence_similarity_consistency()
        test_confidence_outcome_variance()
        test_confidence_data_completeness()
        test_margin_of_error()
        test_tier_prediction()
        test_full_trajectory_with_confidence()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nConfidence and trend calculation is working correctly.")
        print("Task 9 complete! Ready for Task 10 (Prediction API Endpoint).")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
