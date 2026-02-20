"""
Test script for Alumni Vector Generation Service

This script tests the complete alumni vector generation pipeline:
1. Create test alumni records
2. Generate vectors
3. Calculate outcome scores
4. Store in Qdrant
5. Update PostgreSQL references

Run with: python test_alumni_vector_generation.py
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.db import SessionLocal
from app.models import Alumni, PlacementStatusEnum, CompanyTierEnum
from app.services.alumni_vector_service import get_alumni_vector_service
from app.services.qdrant_service import QdrantService
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_test_alumni(db):
    """
    Create test alumni records for testing.
    
    Returns:
        list: List of created Alumni instances
    """
    logger.info("Creating test alumni records...")
    
    test_alumni = [
        {
            'name': 'Test Alumni 1 - Tier1',
            'major': 'Computer Science',
            'graduation_year': 2023,
            'gpa': 8.5,
            'attendance': 90.0,
            'study_hours_per_week': 25.0,
            'project_count': 5,
            'placement_status': PlacementStatusEnum.PLACED,
            'company_tier': CompanyTierEnum.TIER1,
            'role_title': 'Software Engineer',
            'salary_range': '15-20 LPA',
            'role_to_major_match_score': 95.0
        },
        {
            'name': 'Test Alumni 2 - Tier2',
            'major': 'Computer Science',
            'graduation_year': 2023,
            'gpa': 7.8,
            'attendance': 85.0,
            'study_hours_per_week': 20.0,
            'project_count': 3,
            'placement_status': PlacementStatusEnum.PLACED,
            'company_tier': CompanyTierEnum.TIER2,
            'role_title': 'Developer',
            'salary_range': '8-12 LPA',
            'role_to_major_match_score': 85.0
        },
        {
            'name': 'Test Alumni 3 - Tier3',
            'major': 'Mechanical Engineering',
            'graduation_year': 2023,
            'gpa': 7.0,
            'attendance': 80.0,
            'study_hours_per_week': 18.0,
            'project_count': 2,
            'placement_status': PlacementStatusEnum.PLACED,
            'company_tier': CompanyTierEnum.TIER3,
            'role_title': 'Junior Engineer',
            'salary_range': '5-7 LPA',
            'role_to_major_match_score': 70.0
        },
        {
            'name': 'Test Alumni 4 - Not Placed',
            'major': 'Business Administration',
            'graduation_year': 2023,
            'gpa': 6.5,
            'attendance': 70.0,
            'study_hours_per_week': 15.0,
            'project_count': 1,
            'placement_status': PlacementStatusEnum.NOT_PLACED,
            'company_tier': None,
            'role_title': None,
            'salary_range': None,
            'role_to_major_match_score': None
        }
    ]
    
    created_alumni = []
    
    for data in test_alumni:
        alumni = Alumni(**data)
        db.add(alumni)
        db.flush()  # Get ID without committing
        created_alumni.append(alumni)
    
    db.commit()
    
    logger.info(f"Created {len(created_alumni)} test alumni records")
    return created_alumni


def test_outcome_score_calculation():
    """Test outcome score calculation for different placement scenarios."""
    logger.info("\n" + "="*80)
    logger.info("TEST 1: Outcome Score Calculation")
    logger.info("="*80)
    
    service = get_alumni_vector_service()
    
    # Test Tier1
    score_tier1 = service.calculate_outcome_score(
        PlacementStatusEnum.PLACED,
        CompanyTierEnum.TIER1
    )
    logger.info(f"Tier1 outcome score: {score_tier1} (expected: 95.0)")
    assert score_tier1 == 95.0, "Tier1 score should be 95.0"
    
    # Test Tier2
    score_tier2 = service.calculate_outcome_score(
        PlacementStatusEnum.PLACED,
        CompanyTierEnum.TIER2
    )
    logger.info(f"Tier2 outcome score: {score_tier2} (expected: 72.5)")
    assert score_tier2 == 72.5, "Tier2 score should be 72.5"
    
    # Test Tier3
    score_tier3 = service.calculate_outcome_score(
        PlacementStatusEnum.PLACED,
        CompanyTierEnum.TIER3
    )
    logger.info(f"Tier3 outcome score: {score_tier3} (expected: 57.5)")
    assert score_tier3 == 57.5, "Tier3 score should be 57.5"
    
    # Test Not Placed
    score_not_placed = service.calculate_outcome_score(
        PlacementStatusEnum.NOT_PLACED,
        None
    )
    logger.info(f"Not Placed outcome score: {score_not_placed} (expected: 20.0)")
    assert score_not_placed == 20.0, "Not Placed score should be 20.0"
    
    logger.info("✓ All outcome score calculations correct!")


def test_vector_generation(db):
    """Test vector generation for alumni records."""
    logger.info("\n" + "="*80)
    logger.info("TEST 2: Vector Generation")
    logger.info("="*80)
    
    service = get_alumni_vector_service()
    
    # Create test alumni
    alumni_list = create_test_alumni(db)
    
    for alumni in alumni_list:
        logger.info(f"\nGenerating vector for: {alumni.name}")
        
        # Generate vector
        vector = service.generate_vector_for_alumni(alumni, db)
        
        # Verify vector
        assert vector is not None, f"Vector generation failed for {alumni.name}"
        assert vector.shape == (15,), f"Vector should be 15-dimensional, got {vector.shape}"
        assert all(0 <= v <= 1 for v in vector), "All vector components should be in [0, 1]"
        
        logger.info(f"✓ Vector generated: shape={vector.shape}, "
                   f"min={vector.min():.3f}, max={vector.max():.3f}, "
                   f"mean={vector.mean():.3f}")
    
    logger.info("\n✓ All vectors generated successfully!")
    return alumni_list


def test_qdrant_storage(db, alumni_list):
    """Test storing alumni vectors in Qdrant."""
    logger.info("\n" + "="*80)
    logger.info("TEST 3: Qdrant Storage")
    logger.info("="*80)
    
    service = get_alumni_vector_service()
    qdrant = QdrantService()
    
    if not qdrant.is_available:
        logger.warning("⚠ Qdrant unavailable - skipping storage test")
        logger.warning("  (This is OK - system will use PostgreSQL fallback)")
        return
    
    for alumni in alumni_list:
        logger.info(f"\nStoring vector for: {alumni.name}")
        
        # Generate vector
        vector = service.generate_vector_for_alumni(alumni, db)
        
        # Calculate outcome score
        outcome_score = service.calculate_outcome_score(
            alumni.placement_status,
            alumni.company_tier
        )
        
        # Store in Qdrant
        success = service.store_alumni_vector_in_qdrant(
            alumni,
            vector,
            outcome_score
        )
        
        assert success, f"Failed to store vector for {alumni.name}"
        logger.info(f"✓ Vector stored in Qdrant (outcome_score={outcome_score})")
    
    # Verify collection info
    info = qdrant.get_collection_info("alumni")
    if info:
        logger.info(f"\nAlumni collection info:")
        logger.info(f"  Points count: {info['points_count']}")
        logger.info(f"  Vectors count: {info['vectors_count']}")
        logger.info(f"  Status: {info['status']}")
    
    logger.info("\n✓ All vectors stored in Qdrant successfully!")


def test_complete_pipeline(db):
    """Test the complete alumni vector generation pipeline."""
    logger.info("\n" + "="*80)
    logger.info("TEST 4: Complete Pipeline")
    logger.info("="*80)
    
    service = get_alumni_vector_service()
    
    # Create test alumni
    alumni_list = create_test_alumni(db)
    
    # Process batch
    logger.info(f"\nProcessing batch of {len(alumni_list)} alumni...")
    summary = service.process_alumni_batch(alumni_list, db)
    
    # Display summary
    logger.info(f"\nBatch Processing Summary:")
    logger.info(f"  Total: {summary['total']}")
    logger.info(f"  Successful: {summary['successful']}")
    logger.info(f"  Failed: {summary['failed']}")
    logger.info(f"  Qdrant stored: {summary['qdrant_stored']}")
    
    # Display individual results
    logger.info(f"\nIndividual Results:")
    for result in summary['results']:
        status = "✓" if result['success'] else "✗"
        qdrant_status = "✓" if result['vector_stored'] else "✗"
        logger.info(f"  {status} {result['alumni_name']}")
        logger.info(f"      Outcome Score: {result['outcome_score']}")
        logger.info(f"      Qdrant Stored: {qdrant_status}")
        if 'error' in result:
            logger.info(f"      Error: {result['error']}")
    
    # Verify all successful
    assert summary['successful'] == summary['total'], \
        f"Expected all {summary['total']} to succeed, got {summary['successful']}"
    
    logger.info("\n✓ Complete pipeline test passed!")


def cleanup_test_data(db):
    """Clean up test alumni records."""
    logger.info("\n" + "="*80)
    logger.info("CLEANUP: Removing test data")
    logger.info("="*80)
    
    # Delete test alumni
    deleted = db.query(Alumni).filter(Alumni.name.like('Test Alumni%')).delete()
    db.commit()
    
    logger.info(f"Deleted {deleted} test alumni records")
    
    # Clean up Qdrant (optional - test data won't interfere)
    qdrant = QdrantService()
    if qdrant.is_available:
        logger.info("Note: Test vectors remain in Qdrant (won't affect production)")


def main():
    """Run all tests."""
    logger.info("="*80)
    logger.info("ALUMNI VECTOR GENERATION SERVICE - TEST SUITE")
    logger.info("="*80)
    
    db = SessionLocal()
    
    try:
        # Test 1: Outcome score calculation
        test_outcome_score_calculation()
        
        # Test 2: Vector generation
        alumni_list = test_vector_generation(db)
        
        # Test 3: Qdrant storage
        test_qdrant_storage(db, alumni_list)
        
        # Clean up test data from tests 2 and 3
        cleanup_test_data(db)
        
        # Test 4: Complete pipeline (creates new test data)
        test_complete_pipeline(db)
        
        # Final cleanup
        cleanup_test_data(db)
        
        logger.info("\n" + "="*80)
        logger.info("✓ ALL TESTS PASSED!")
        logger.info("="*80)
        logger.info("\nAlumni vector generation service is working correctly.")
        logger.info("Ready for CSV import integration.")
        
    except Exception as e:
        logger.error(f"\n✗ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    main()
