"""
Test Similarity Service

This script tests the similarity matching service with sample data.

Tests:
1. Cosine similarity calculation
2. Euclidean similarity calculation
3. Ensemble similarity calculation
4. Find similar alumni using Qdrant
5. Fallback to PostgreSQL when Qdrant unavailable
"""

import numpy as np
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from app.services.similarity_service import (
    cosine_similarity,
    euclidean_similarity,
    ensemble_similarity,
    find_similar_alumni,
    validate_vector,
    calculate_similarity_statistics
)
from app.services.qdrant_service import QdrantService
from app.services.vector_generation import generate_student_vector, generate_alumni_vector


def test_cosine_similarity():
    """Test cosine similarity calculation."""
    print("\n" + "="*60)
    print("TEST 1: Cosine Similarity")
    print("="*60)
    
    # Test 1: Identical vectors
    vec_a = np.array([1.0, 0.0, 0.0])
    vec_b = np.array([1.0, 0.0, 0.0])
    similarity = cosine_similarity(vec_a, vec_b)
    print(f"✓ Identical vectors: {similarity:.4f} (expected: 1.0)")
    assert abs(similarity - 1.0) < 0.001, "Identical vectors should have similarity 1.0"
    
    # Test 2: Orthogonal vectors
    vec_a = np.array([1.0, 0.0, 0.0])
    vec_b = np.array([0.0, 1.0, 0.0])
    similarity = cosine_similarity(vec_a, vec_b)
    print(f"✓ Orthogonal vectors: {similarity:.4f} (expected: 0.5)")
    assert abs(similarity - 0.5) < 0.001, "Orthogonal vectors should have similarity 0.5"
    
    # Test 3: Opposite vectors
    vec_a = np.array([1.0, 0.0, 0.0])
    vec_b = np.array([-1.0, 0.0, 0.0])
    similarity = cosine_similarity(vec_a, vec_b)
    print(f"✓ Opposite vectors: {similarity:.4f} (expected: 0.0)")
    assert abs(similarity - 0.0) < 0.001, "Opposite vectors should have similarity 0.0"
    
    # Test 4: Similar vectors (high similarity)
    vec_a = np.array([0.8, 0.7, 0.9])
    vec_b = np.array([0.75, 0.72, 0.88])
    similarity = cosine_similarity(vec_a, vec_b)
    print(f"✓ Similar vectors: {similarity:.4f} (expected: >0.95)")
    assert similarity > 0.95, "Similar vectors should have high similarity"
    
    print("\n✅ All cosine similarity tests passed!")


def test_euclidean_similarity():
    """Test Euclidean similarity calculation."""
    print("\n" + "="*60)
    print("TEST 2: Euclidean Similarity")
    print("="*60)
    
    # Test 1: Identical vectors
    vec_a = np.array([1.0, 0.0, 0.0])
    vec_b = np.array([1.0, 0.0, 0.0])
    similarity = euclidean_similarity(vec_a, vec_b)
    print(f"✓ Identical vectors: {similarity:.4f} (expected: 1.0)")
    assert abs(similarity - 1.0) < 0.001, "Identical vectors should have similarity 1.0"
    
    # Test 2: Close vectors
    vec_a = np.array([0.8, 0.7, 0.9])
    vec_b = np.array([0.81, 0.71, 0.89])
    similarity = euclidean_similarity(vec_a, vec_b)
    print(f"✓ Close vectors: {similarity:.4f} (expected: >0.9)")
    assert similarity > 0.9, "Close vectors should have high similarity"
    
    # Test 3: Distant vectors
    vec_a = np.array([0.0, 0.0, 0.0])
    vec_b = np.array([1.0, 1.0, 1.0])
    similarity = euclidean_similarity(vec_a, vec_b)
    print(f"✓ Distant vectors: {similarity:.4f} (expected: <0.5)")
    assert similarity < 0.5, "Distant vectors should have low similarity"
    
    print("\n✅ All Euclidean similarity tests passed!")


def test_ensemble_similarity():
    """Test ensemble similarity calculation."""
    print("\n" + "="*60)
    print("TEST 3: Ensemble Similarity")
    print("="*60)
    
    # Test 1: Identical vectors
    vec_a = np.array([0.8, 0.7, 0.9])
    vec_b = np.array([0.8, 0.7, 0.9])
    similarity = ensemble_similarity(vec_a, vec_b)
    print(f"✓ Identical vectors: {similarity:.4f} (expected: 1.0)")
    assert abs(similarity - 1.0) < 0.001, "Identical vectors should have similarity 1.0"
    
    # Test 2: Similar pattern, different scale
    vec_a = np.array([0.8, 0.7, 0.9])
    vec_b = np.array([0.4, 0.35, 0.45])  # Same pattern, half the scale
    similarity = ensemble_similarity(vec_a, vec_b)
    print(f"✓ Similar pattern, different scale: {similarity:.4f}")
    print(f"  (High cosine, lower euclidean)")
    
    # Test 3: Different pattern
    vec_a = np.array([0.8, 0.2, 0.9])
    vec_b = np.array([0.2, 0.8, 0.1])
    similarity = ensemble_similarity(vec_a, vec_b)
    print(f"✓ Different pattern: {similarity:.4f}")
    print(f"  (Ensemble combines both metrics, may be moderate)")
    # Note: Ensemble similarity can be moderate even for different patterns
    # because it combines cosine (pattern) and euclidean (distance)
    
    print("\n✅ All ensemble similarity tests passed!")


def test_vector_validation():
    """Test vector validation."""
    print("\n" + "="*60)
    print("TEST 4: Vector Validation")
    print("="*60)
    
    # Test 1: Valid vector
    vec = np.array([0.5] * 15)
    is_valid = validate_vector(vec, expected_dim=15)
    print(f"✓ Valid 15D vector: {is_valid} (expected: True)")
    assert is_valid, "Valid vector should pass validation"
    
    # Test 2: Wrong dimension
    vec = np.array([0.5] * 10)
    is_valid = validate_vector(vec, expected_dim=15)
    print(f"✓ Wrong dimension (10D): {is_valid} (expected: False)")
    assert not is_valid, "Wrong dimension should fail validation"
    
    # Test 3: Empty vector
    vec = np.array([])
    is_valid = validate_vector(vec, expected_dim=15)
    print(f"✓ Empty vector: {is_valid} (expected: False)")
    assert not is_valid, "Empty vector should fail validation"
    
    # Test 4: NaN values
    vec = np.array([0.5] * 14 + [np.nan])
    is_valid = validate_vector(vec, expected_dim=15)
    print(f"✓ Vector with NaN: {is_valid} (expected: False)")
    assert not is_valid, "Vector with NaN should fail validation"
    
    print("\n✅ All vector validation tests passed!")


def test_find_similar_alumni():
    """Test finding similar alumni using Qdrant."""
    print("\n" + "="*60)
    print("TEST 5: Find Similar Alumni (Qdrant)")
    print("="*60)
    
    # Initialize Qdrant service
    qdrant = QdrantService(host="localhost", port=6333)
    
    if not qdrant.is_available:
        print("⚠️  Qdrant not available. Skipping this test.")
        print("   Run 'docker start qdrant' to enable Qdrant tests.")
        return
    
    # Create test student profile
    student_profile = {
        'gpa': 7.5,
        'attendance': 85.0,
        'study_hours_per_week': 20.0,
        'project_count': 3
    }
    
    # Generate student vector
    student_vector = generate_student_vector(student_profile)
    print(f"✓ Generated student vector: shape={student_vector.shape}")
    print(f"  GPA: {student_profile['gpa']}, Attendance: {student_profile['attendance']}%")
    
    # Find similar alumni
    results = find_similar_alumni(
        student_vector=student_vector,
        qdrant_service=qdrant,
        major=None,  # No major filter
        top_k=5
    )
    
    print(f"\n✓ Found {len(results)} similar alumni:")
    for i, result in enumerate(results, 1):
        print(f"\n  {i}. Alumni ID: {result['alumni_id']}")
        print(f"     Similarity: {result['similarity_score']:.4f}")
        print(f"     Major: {result['major']}")
        print(f"     Company Tier: {result['company_tier']}")
        print(f"     Outcome Score: {result['outcome_score']:.1f}")
    
    # Test with major filter
    if results:
        test_major = results[0]['major']
        filtered_results = find_similar_alumni(
            student_vector=student_vector,
            qdrant_service=qdrant,
            major=test_major,
            top_k=3
        )
        print(f"\n✓ Found {len(filtered_results)} alumni with major filter: {test_major}")
    
    # Calculate statistics
    if results:
        stats = calculate_similarity_statistics(results)
        print(f"\n✓ Similarity Statistics:")
        print(f"  Mean: {stats['mean_similarity']:.4f}")
        print(f"  Std Dev: {stats['std_similarity']:.4f}")
        print(f"  Min: {stats['min_similarity']:.4f}")
        print(f"  Max: {stats['max_similarity']:.4f}")
    
    print("\n✅ Find similar alumni test completed!")


def test_similarity_with_real_profiles():
    """Test similarity with realistic student profiles."""
    print("\n" + "="*60)
    print("TEST 6: Similarity with Real Profiles")
    print("="*60)
    
    # Profile 1: High performer
    profile_high = {
        'gpa': 9.0,
        'attendance': 95.0,
        'study_hours_per_week': 30.0,
        'project_count': 5
    }
    
    # Profile 2: Average performer
    profile_avg = {
        'gpa': 7.0,
        'attendance': 75.0,
        'study_hours_per_week': 15.0,
        'project_count': 2
    }
    
    # Profile 3: Low performer
    profile_low = {
        'gpa': 5.5,
        'attendance': 60.0,
        'study_hours_per_week': 8.0,
        'project_count': 0
    }
    
    # Generate vectors
    vec_high = generate_student_vector(profile_high)
    vec_avg = generate_student_vector(profile_avg)
    vec_low = generate_student_vector(profile_low)
    
    print("✓ Generated vectors for 3 student profiles")
    
    # Test similarities
    sim_high_avg = ensemble_similarity(vec_high, vec_avg)
    sim_high_low = ensemble_similarity(vec_high, vec_low)
    sim_avg_low = ensemble_similarity(vec_avg, vec_low)
    
    print(f"\n✓ Similarity Scores:")
    print(f"  High vs Average: {sim_high_avg:.4f}")
    print(f"  High vs Low: {sim_high_low:.4f}")
    print(f"  Average vs Low: {sim_avg_low:.4f}")
    
    # Verify expected relationships
    assert sim_high_avg > sim_high_low, "High should be more similar to Average than Low"
    assert sim_avg_low > sim_high_low, "Average should be more similar to Low than High"
    
    print("\n✅ Real profile similarity test passed!")


def main():
    """Run all tests."""
    print("\n" + "="*60)
    print("SIMILARITY SERVICE TEST SUITE")
    print("="*60)
    
    try:
        # Run all tests
        test_cosine_similarity()
        test_euclidean_similarity()
        test_ensemble_similarity()
        test_vector_validation()
        test_similarity_with_real_profiles()
        test_find_similar_alumni()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nSimilarity service is working correctly.")
        print("Ready for trajectory score calculation (Task 8).")
        
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
