"""
Test Trajectory Score Calculation Service

This script tests the trajectory score calculation with various student profiles.

Tests:
1. Academic score calculation
2. Behavioral score calculation
3. Skill score calculation with market weighting
4. Trajectory score calculation with similar alumni
5. Interaction adjustments
6. Major-specific weights
"""

import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app.services.trajectory_service import (
    calculate_academic_score,
    calculate_behavioral_score,
    calculate_skill_score,
    calculate_trajectory_score,
    map_alumni_outcome_to_score,
    get_major_weights,
    interpret_score,
    apply_interaction_adjustments
)
from app.services.similarity_service import find_similar_alumni
from app.services.qdrant_service import QdrantService
from app.services.vector_generation import generate_student_vector


def test_academic_score():
    """Test academic score calculation."""
    print("\n" + "="*60)
    print("TEST 1: Academic Score Calculation")
    print("="*60)
    
    # Test 1: High performer
    profile = {'gpa': 9.0, 'attendance': 95.0}
    score = calculate_academic_score(profile)
    print(f"✓ High performer (GPA 9.0, 95% attendance): {score:.3f}")
    assert score > 0.85, f"High performer should have score > 0.85, got {score:.3f}"
    
    # Test 2: Average performer
    profile = {'gpa': 7.0, 'attendance': 75.0}
    score = calculate_academic_score(profile)
    print(f"✓ Average performer (GPA 7.0, 75% attendance): {score:.3f}")
    assert 0.60 < score < 0.80, f"Average performer should have score 0.60-0.80, got {score:.3f}"
    
    # Test 3: Low performer
    profile = {'gpa': 5.0, 'attendance': 60.0}
    score = calculate_academic_score(profile)
    print(f"✓ Low performer (GPA 5.0, 60% attendance): {score:.3f}")
    assert score < 0.60, f"Low performer should have score < 0.60, got {score:.3f}"
    
    print("\n✅ All academic score tests passed!")


def test_behavioral_score():
    """Test behavioral score calculation."""
    print("\n" + "="*60)
    print("TEST 2: Behavioral Score Calculation")
    print("="*60)
    
    # Test 1: High effort student
    profile = {
        'study_hours_per_week': 30,
        'project_count': 5,
        'consistency': 4,
        'problem_solving': 4
    }
    wellbeing = [{
        'screen_time_hours': 4.0,
        'social_media_hours': 1.0,
        'distraction_level': 2,
        'sleep_duration_hours': 7.5
    }]
    score = calculate_behavioral_score(profile, wellbeing)
    print(f"✓ High effort (30h study, 5 projects, good habits): {score:.3f}")
    assert score > 0.55, f"High effort should have score > 0.55, got {score:.3f}"
    
    # Test 2: Average student
    profile = {
        'study_hours_per_week': 15,
        'project_count': 2,
        'consistency': 3,
        'problem_solving': 3
    }
    score = calculate_behavioral_score(profile, None)
    print(f"✓ Average (15h study, 2 projects, no wellbeing data): {score:.3f}")
    assert 0.35 < score < 0.65, f"Average should have score 0.35-0.65, got {score:.3f}"
    
    # Test 3: Low effort student
    profile = {
        'study_hours_per_week': 5,
        'project_count': 0,
        'consistency': 2,
        'problem_solving': 2
    }
    wellbeing = [{
        'screen_time_hours': 10.0,
        'social_media_hours': 5.0,
        'distraction_level': 5,
        'sleep_duration_hours': 5.0
    }]
    score = calculate_behavioral_score(profile, wellbeing)
    print(f"✓ Low effort (5h study, 0 projects, poor habits): {score:.3f}")
    assert score < 0.45, f"Low effort should have score < 0.45, got {score:.3f}"
    
    print("\n✅ All behavioral score tests passed!")


def test_skill_score():
    """Test skill score calculation with market weighting."""
    print("\n" + "="*60)
    print("TEST 3: Skill Score with Market Weighting")
    print("="*60)
    
    # Test 1: Using new FINAL-FORMULAS approach
    profile = {
        'languages': 'Python,Java,C++,JavaScript,SQL',
        'problem_solving': 4,
        'communication': 4,
        'teamwork': 4,
        'project_count': 5,
        'deployed': True,
        'internship': True,
        'career_clarity': 3
    }
    score = calculate_skill_score(profile, None)
    print(f"✓ Complete profile (5 languages, deployed, internship): {score:.3f}")
    assert score > 0.70, f"Complete profile should have high score, got {score:.3f}"
    
    # Test 2: Trending skills (backward compatibility with market weights)
    skills = [
        {'skill_name': 'Python', 'proficiency_score': 85, 'market_weight': 2.0},
        {'skill_name': 'React', 'proficiency_score': 80, 'market_weight': 2.0},
        {'skill_name': 'AWS', 'proficiency_score': 75, 'market_weight': 2.0}
    ]
    score = calculate_skill_score(None, skills)
    print(f"✓ Trending skills (Python, React, AWS): {score:.3f}")
    assert score > 0.75, f"Trending skills should have high score, got {score:.3f}"
    
    # Test 3: Outdated skills (low demand)
    skills = [
        {'skill_name': 'PHP', 'proficiency_score': 90, 'market_weight': 0.5},
        {'skill_name': 'jQuery', 'proficiency_score': 85, 'market_weight': 0.5},
        {'skill_name': 'Flash', 'proficiency_score': 80, 'market_weight': 0.5}
    ]
    score = calculate_skill_score(None, skills)
    print(f"✓ Outdated skills (PHP, jQuery, Flash): {score:.3f}")
    print(f"  (High proficiency but low market demand)")
    assert score < 0.90, f"Outdated skills should have lower score despite high proficiency, got {score:.3f}"
    
    # Test 4: Minimal profile
    profile = {
        'languages': 'Python',
        'problem_solving': 3,
        'project_count': 2,
        'deployed': False,
        'internship': False
    }
    score = calculate_skill_score(profile, None)
    print(f"✓ Minimal profile (1 language, no deployment/internship): {score:.3f}")
    assert 0.20 < score < 0.50, f"Minimal profile should have moderate-low score, got {score:.3f}"
    
    print("\n✅ All skill score tests passed!")


def test_alumni_outcome_mapping():
    """Test alumni outcome to score mapping."""
    print("\n" + "="*60)
    print("TEST 4: Alumni Outcome Mapping")
    print("="*60)
    
    # Test different tiers
    alumni_tier1 = {'placement_status': 'Placed', 'company_tier': 'Tier1'}
    score = map_alumni_outcome_to_score(alumni_tier1)
    print(f"✓ Tier1 (FAANG): {score:.1f} (expected: 90-100)")
    assert 90 <= score <= 100, "Tier1 should be 90-100"
    
    alumni_tier2 = {'placement_status': 'Placed', 'company_tier': 'Tier2'}
    score = map_alumni_outcome_to_score(alumni_tier2)
    print(f"✓ Tier2 (Mid-size): {score:.1f} (expected: 65-80)")
    assert 65 <= score <= 80, "Tier2 should be 65-80"
    
    alumni_tier3 = {'placement_status': 'Placed', 'company_tier': 'Tier3'}
    score = map_alumni_outcome_to_score(alumni_tier3)
    print(f"✓ Tier3 (Startup): {score:.1f} (expected: 50-65)")
    assert 50 <= score <= 65, "Tier3 should be 50-65"
    
    alumni_not_placed = {'placement_status': 'Not Placed'}
    score = map_alumni_outcome_to_score(alumni_not_placed)
    print(f"✓ Not Placed: {score:.1f} (expected: 10-30)")
    assert 10 <= score <= 30, "Not Placed should be 10-30"
    
    print("\n✅ All outcome mapping tests passed!")


def test_major_weights():
    """Test major-specific weights."""
    print("\n" + "="*60)
    print("TEST 5: Major-Specific Weights")
    print("="*60)
    
    # Test different majors
    cs_weights = get_major_weights('Computer Science')
    print(f"✓ Computer Science: Academic {cs_weights['academic']:.0%}, "
          f"Behavioral {cs_weights['behavioral']:.0%}, Skills {cs_weights['skills']:.0%}")
    assert cs_weights['skills'] == 0.40, "CS should prioritize skills (40%)"
    
    mech_weights = get_major_weights('Mechanical Engineering')
    print(f"✓ Mechanical Engineering: Academic {mech_weights['academic']:.0%}, "
          f"Behavioral {mech_weights['behavioral']:.0%}, Skills {mech_weights['skills']:.0%}")
    assert mech_weights['academic'] == 0.40, "Mech should prioritize academics (40%)"
    
    business_weights = get_major_weights('Business Administration')
    print(f"✓ Business Administration: Academic {business_weights['academic']:.0%}, "
          f"Behavioral {business_weights['behavioral']:.0%}, Skills {business_weights['skills']:.0%}")
    assert business_weights['behavioral'] == 0.50, "Business should prioritize behavioral (50%)"
    
    default_weights = get_major_weights('Unknown Major')
    print(f"✓ Unknown Major (default): Academic {default_weights['academic']:.0%}, "
          f"Behavioral {default_weights['behavioral']:.0%}, Skills {default_weights['skills']:.0%}")
    
    print("\n✅ All major weight tests passed!")


def test_trajectory_calculation():
    """Test full trajectory score calculation."""
    print("\n" + "="*60)
    print("TEST 6: Full Trajectory Score Calculation")
    print("="*60)
    
    # Create test student profile with all new fields
    student_profile = {
        'gpa': 7.5,
        'attendance': 85.0,
        'internal_marks': 75.0,
        'backlogs': 0,
        'study_hours_per_week': 20.0,
        'practice_hours': 1.0,
        'project_count': 3,
        'consistency': 3,
        'problem_solving': 3,
        'languages': 'Python,Java,JavaScript',
        'communication': 3,
        'teamwork': 3,
        'deployed': True,
        'internship': False,
        'career_clarity': 3,
        'major': 'Computer Science'
    }
    
    # Create test wellbeing data
    wellbeing = [{
        'screen_time_hours': 6.0,
        'social_media_hours': 2.0,
        'distraction_level': 3,
        'sleep_duration_hours': 7.0
    }]
    
    # Create mock similar alumni
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
        skills=None  # Use profile-based approach
    )
    
    print(f"\n✓ Student Profile:")
    print(f"  GPA: {student_profile['gpa']}, Attendance: {student_profile['attendance']}%")
    print(f"  Study: {student_profile['study_hours_per_week']}h/week, Projects: {student_profile['project_count']}")
    print(f"  Major: {student_profile['major']}")
    
    print(f"\n✓ Component Scores:")
    print(f"  Academic: {result['academic_score']:.1f}")
    print(f"  Behavioral: {result['behavioral_score']:.1f}")
    print(f"  Skills: {result['skill_score']:.1f}")
    
    print(f"\n✓ Component Weights (CS major):")
    weights = result['component_weights']
    print(f"  Academic: {weights['academic']:.0%}")
    print(f"  Behavioral: {weights['behavioral']:.0%}")
    print(f"  Skills: {weights['skills']:.0%}")
    
    print(f"\n✓ Trajectory Score: {result['score']:.1f}")
    print(f"  Based on {result['similar_alumni_count']} similar alumni")
    print(f"  Interpretation: {result['interpretation']}")
    
    # Validate result
    assert 0 <= result['score'] <= 100, "Score must be in [0, 100] range"
    assert 0 <= result['academic_score'] <= 100, "Academic score must be in [0, 100] range"
    assert 0 <= result['behavioral_score'] <= 100, "Behavioral score must be in [0, 100] range"
    assert 0 <= result['skill_score'] <= 100, "Skill score must be in [0, 100] range"
    assert result['similar_alumni_count'] == 3, "Should have 3 similar alumni"
    
    print("\n✅ Trajectory calculation test passed!")


def test_interaction_adjustments():
    """Test interaction adjustments."""
    print("\n" + "="*60)
    print("TEST 7: Interaction Adjustments")
    print("="*60)
    
    base_score = 75.0
    
    # Test 1: Burnout penalty
    wellbeing_burnout = [{
        'sleep_duration_hours': 5.0,
        'screen_time_hours': 6.0,
        'educational_app_hours': 2.0,
        'productivity_hours': 1.0,
        'social_media_hours': 1.5,
        'entertainment_hours': 1.5
    }]
    adjusted = apply_interaction_adjustments(
        base_score, 85.0, 70.0, 75.0, wellbeing_burnout
    )
    print(f"✓ Burnout penalty (high academic + low sleep): {base_score:.1f} → {adjusted:.1f}")
    assert adjusted < base_score, "Should apply burnout penalty"
    
    # Test 2: Grit bonus
    adjusted = apply_interaction_adjustments(
        base_score, 70.0, 80.0, 75.0, None
    )
    print(f"✓ Grit bonus (high behavioral): {base_score:.1f} → {adjusted:.1f}")
    assert adjusted > base_score, "Should apply grit bonus"
    
    # Test 3: Balance bonus
    adjusted = apply_interaction_adjustments(
        base_score, 75.0, 75.0, 75.0, None
    )
    print(f"✓ Balance bonus (all components > 70): {base_score:.1f} → {adjusted:.1f}")
    assert adjusted > base_score, "Should apply balance bonus"
    
    print("\n✅ All interaction adjustment tests passed!")


def test_score_interpretation():
    """Test score interpretation."""
    print("\n" + "="*60)
    print("TEST 8: Score Interpretation")
    print("="*60)
    
    # Test different score ranges
    interpretation = interpret_score(85.0)
    print(f"✓ Score 85: {interpretation}")
    assert "High employability" in interpretation
    
    interpretation = interpret_score(60.0)
    print(f"✓ Score 60: {interpretation}")
    assert "Moderate employability" in interpretation
    
    interpretation = interpret_score(35.0)
    print(f"✓ Score 35: {interpretation}")
    assert "Low employability" in interpretation
    
    print("\n✅ All interpretation tests passed!")


def test_with_real_qdrant_data():
    """Test trajectory calculation with real Qdrant data."""
    print("\n" + "="*60)
    print("TEST 9: Trajectory with Real Qdrant Data")
    print("="*60)
    
    # Initialize Qdrant
    qdrant = QdrantService(host="localhost", port=6333)
    
    if not qdrant.is_available:
        print("⚠️  Qdrant not available. Skipping this test.")
        return
    
    # Create student profile with all new fields
    student_profile = {
        'gpa': 7.5,
        'attendance': 85.0,
        'internal_marks': 75.0,
        'backlogs': 0,
        'study_hours_per_week': 20.0,
        'practice_hours': 1.0,
        'project_count': 3,
        'consistency': 3,
        'problem_solving': 3,
        'languages': 'Python,Java,JavaScript',
        'communication': 3,
        'teamwork': 3,
        'deployed': True,
        'internship': False,
        'career_clarity': 3,
        'major': 'Computer Science'
    }
    
    # Generate vector
    student_vector = generate_student_vector(student_profile)
    
    # Find similar alumni
    similar_alumni = find_similar_alumni(
        student_vector=student_vector,
        qdrant_service=qdrant,
        major='Computer Science',
        top_k=5
    )
    
    if not similar_alumni:
        print("⚠️  No alumni data in Qdrant. Skipping this test.")
        return
    
    # Calculate trajectory score
    result = calculate_trajectory_score(
        student_profile=student_profile,
        similar_alumni=similar_alumni,
        wellbeing=None,
        skills=None  # Use profile-based approach
    )
    
    print(f"\n✓ Trajectory Score: {result['score']:.1f}")
    print(f"  Based on {result['similar_alumni_count']} real alumni from Qdrant")
    print(f"  Interpretation: {result['interpretation']}")
    
    print(f"\n✓ Similar Alumni:")
    for i, alumni in enumerate(similar_alumni[:3], 1):
        print(f"  {i}. Similarity: {alumni['similarity_score']:.3f}, "
              f"Tier: {alumni['company_tier']}, "
              f"Outcome: {alumni['outcome_score']:.1f}")
    
    print("\n✅ Real Qdrant data test completed!")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("TRAJECTORY SERVICE TEST SUITE")
    print("="*60)
    
    try:
        # Run all tests
        test_academic_score()
        test_behavioral_score()
        test_skill_score()
        test_alumni_outcome_mapping()
        test_major_weights()
        test_trajectory_calculation()
        test_interaction_adjustments()
        test_score_interpretation()
        test_with_real_qdrant_data()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nTrajectory service is working correctly.")
        print("Ready for confidence & trend calculation (Task 9).")
        
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
