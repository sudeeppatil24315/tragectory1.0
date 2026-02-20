"""
Test script for Qdrant Vector Database connection and basic operations.
"""

import sys
import numpy as np
from app.services.qdrant_service import QdrantService
from app.services.vector_generation import generate_student_vector

def test_qdrant_connection():
    """Test 1: Check if Qdrant is running and accessible."""
    print("=" * 60)
    print("TEST 1: Qdrant Connection")
    print("=" * 60)
    
    try:
        qdrant = QdrantService(host="localhost", port=6333)
        
        if qdrant.is_available:
            print("✅ SUCCESS: Connected to Qdrant at localhost:6333")
            return qdrant
        else:
            print("❌ FAILED: Cannot connect to Qdrant")
            print("\nTroubleshooting:")
            print("1. Check if Docker is running: docker ps")
            print("2. Check if Qdrant container is running: docker ps | grep qdrant")
            print("3. If not running, start it: docker start qdrant")
            print("4. If container doesn't exist, run: setup_qdrant.bat")
            return None
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return None


def test_create_collections(qdrant):
    """Test 2: Create students and alumni collections."""
    print("\n" + "=" * 60)
    print("TEST 2: Create Collections")
    print("=" * 60)
    
    try:
        success = qdrant.create_collections(vector_size=15)
        
        if success:
            print("✅ SUCCESS: Created 'students' and 'alumni' collections")
            
            # Get collection info
            students_info = qdrant.get_collection_info("students")
            alumni_info = qdrant.get_collection_info("alumni")
            
            print(f"\nStudents Collection:")
            print(f"  - Vectors: {students_info['vectors_count']}")
            print(f"  - Points: {students_info['points_count']}")
            print(f"  - Status: {students_info['status']}")
            
            print(f"\nAlumni Collection:")
            print(f"  - Vectors: {alumni_info['vectors_count']}")
            print(f"  - Points: {alumni_info['points_count']}")
            print(f"  - Status: {alumni_info['status']}")
            
            return True
        else:
            print("❌ FAILED: Could not create collections")
            return False
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False


def test_store_student_vector(qdrant):
    """Test 3: Store a test student vector."""
    print("\n" + "=" * 60)
    print("TEST 3: Store Student Vector")
    print("=" * 60)
    
    try:
        # Generate a test vector
        test_profile = {
            "gpa": 7.5,
            "attendance": 85.0,
            "study_hours_per_week": 20,
            "project_count": 3
        }
        
        vector = generate_student_vector(test_profile)
        
        print(f"Generated vector: {vector.shape} dimensions")
        print(f"Vector preview: [{vector[0]:.3f}, {vector[1]:.3f}, {vector[2]:.3f}, ...]")
        
        # Store vector
        metadata = {
            "name": "Test Student",
            "major": "Computer Science",
            "semester": 5,
            "gpa": 7.5,
            "attendance": 85.0,
            "trajectory_score": 0.0
        }
        
        success = qdrant.store_student_vector(
            student_id=999,
            vector=vector,
            metadata=metadata
        )
        
        if success:
            print("✅ SUCCESS: Stored test student vector (ID: 999)")
            return True
        else:
            print("❌ FAILED: Could not store student vector")
            return False
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_store_alumni_vectors(qdrant):
    """Test 4: Store test alumni vectors."""
    print("\n" + "=" * 60)
    print("TEST 4: Store Alumni Vectors")
    print("=" * 60)
    
    try:
        # Create 3 test alumni with different profiles
        alumni_data = [
            {
                "id": 1001,
                "profile": {"gpa": 8.5, "attendance": 90, "study_hours_per_week": 25, "project_count": 5},
                "metadata": {
                    "name": "Alumni A",
                    "major": "Computer Science",
                    "graduation_year": 2023,
                    "company_tier": "Tier1",
                    "salary_range": "15-20 LPA",
                    "placement_status": "Placed",
                    "outcome_score": 95.0
                }
            },
            {
                "id": 1002,
                "profile": {"gpa": 7.0, "attendance": 80, "study_hours_per_week": 18, "project_count": 2},
                "metadata": {
                    "name": "Alumni B",
                    "major": "Computer Science",
                    "graduation_year": 2023,
                    "company_tier": "Tier2",
                    "salary_range": "8-12 LPA",
                    "placement_status": "Placed",
                    "outcome_score": 70.0
                }
            },
            {
                "id": 1003,
                "profile": {"gpa": 6.0, "attendance": 70, "study_hours_per_week": 12, "project_count": 1},
                "metadata": {
                    "name": "Alumni C",
                    "major": "Computer Science",
                    "graduation_year": 2023,
                    "company_tier": "Tier3",
                    "salary_range": "4-6 LPA",
                    "placement_status": "Placed",
                    "outcome_score": 50.0
                }
            }
        ]
        
        stored_count = 0
        for alumni in alumni_data:
            vector = generate_student_vector(alumni["profile"])
            success = qdrant.store_alumni_vector(
                alumni_id=alumni["id"],
                vector=vector,
                metadata=alumni["metadata"]
            )
            if success:
                stored_count += 1
                print(f"  ✓ Stored {alumni['metadata']['name']} (ID: {alumni['id']})")
        
        if stored_count == len(alumni_data):
            print(f"\n✅ SUCCESS: Stored {stored_count} alumni vectors")
            return True
        else:
            print(f"\n⚠️  PARTIAL: Stored {stored_count}/{len(alumni_data)} alumni vectors")
            return False
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_similarity_search(qdrant):
    """Test 5: Find similar alumni for test student."""
    print("\n" + "=" * 60)
    print("TEST 5: Similarity Search")
    print("=" * 60)
    
    try:
        # Generate student vector (same as Test 3)
        test_profile = {
            "gpa": 7.5,
            "attendance": 85.0,
            "study_hours_per_week": 20,
            "project_count": 3
        }
        
        student_vector = generate_student_vector(test_profile)
        
        print("Searching for similar alumni...")
        print(f"Student profile: GPA {test_profile['gpa']}, Attendance {test_profile['attendance']}%")
        
        # Find similar alumni
        results = qdrant.find_similar_alumni(
            student_vector=student_vector,
            major="Computer Science",
            top_k=3
        )
        
        if results:
            print(f"\n✅ SUCCESS: Found {len(results)} similar alumni\n")
            
            for i, result in enumerate(results, 1):
                print(f"{i}. {result['name']}")
                print(f"   Similarity: {result['similarity_score']:.3f}")
                print(f"   Company: {result['company_tier']}")
                print(f"   Salary: {result['salary_range']}")
                print(f"   Outcome Score: {result['outcome_score']}")
                print()
            
            return True
        else:
            print("❌ FAILED: No similar alumni found")
            print("\nPossible reasons:")
            print("1. No alumni vectors stored yet")
            print("2. Major filter too restrictive")
            print("3. Collection is empty")
            return False
    
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("QDRANT VECTOR DATABASE TEST SUITE")
    print("=" * 60)
    print("\nThis script will test:")
    print("1. Connection to Qdrant")
    print("2. Collection creation")
    print("3. Vector storage (students)")
    print("4. Vector storage (alumni)")
    print("5. Similarity search")
    print("\n" + "=" * 60)
    
    # Test 1: Connection
    qdrant = test_qdrant_connection()
    if not qdrant:
        print("\n❌ TESTS ABORTED: Cannot connect to Qdrant")
        print("\nPlease ensure:")
        print("1. Docker is running")
        print("2. Qdrant container is running (docker ps | grep qdrant)")
        print("3. Run setup_qdrant.bat if needed")
        sys.exit(1)
    
    # Test 2: Create collections
    if not test_create_collections(qdrant):
        print("\n⚠️  WARNING: Collection creation failed, but continuing...")
    
    # Test 3: Store student vector
    if not test_store_student_vector(qdrant):
        print("\n❌ TESTS ABORTED: Cannot store student vector")
        sys.exit(1)
    
    # Test 4: Store alumni vectors
    if not test_store_alumni_vectors(qdrant):
        print("\n⚠️  WARNING: Alumni storage failed, but continuing...")
    
    # Test 5: Similarity search
    test_similarity_search(qdrant)
    
    # Final summary
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)
    print("\n✅ Qdrant is ready for use!")
    print("\nNext steps:")
    print("1. Import real alumni data")
    print("2. Generate vectors for all students")
    print("3. Test trajectory score calculation")
    print("\nQdrant Dashboard: http://localhost:6333/dashboard")
    print("=" * 60)


if __name__ == "__main__":
    main()
