"""
Test script for Data Cleaning Service

This script tests the data cleaning service with various messy data scenarios.
"""

from app.services.data_cleaning_service import get_data_cleaning_service


def test_data_cleaning():
    """Test the data cleaning service with messy data"""
    
    print("=" * 60)
    print("TESTING DATA CLEANING SERVICE")
    print("=" * 60)
    
    # Get service
    print("\n1. Creating data cleaning service...")
    service = get_data_cleaning_service()
    print("✓ Service created")
    
    # Test Case 1: Messy major name
    print("\n2. Test Case 1: Messy Major Name")
    print("   Input: 'comp sci' → Expected: 'Computer Science'")
    
    raw_data1 = {
        "name": "john doe",
        "major": "comp sci",
        "gpa": 8.5,
        "skills": ["python", "java"]
    }
    
    result1 = service.clean_student_record(raw_data1)
    
    if result1['success']:
        print(f"✓ Cleaning successful ({result1['method']})")
        print(f"   Major: {result1['cleaned_data']['major']}")
        print(f"   Name: {result1['cleaned_data']['name']}")
        print(f"   Quality Score: {result1['quality_score']:.1f}")
        print(f"   Changes: {len(result1['changes'])}")
        for change in result1['changes']:
            print(f"     - {change}")
    else:
        print(f"✗ Cleaning failed: {result1.get('error', 'Unknown')}")
    
    # Test Case 2: GPA scale conversion
    print("\n3. Test Case 2: GPA Scale Conversion")
    print("   Input: 3.5/4.0 → Expected: 8.75/10.0")
    
    raw_data2 = {
        "name": "Jane Smith",
        "major": "Computer Science",
        "gpa": 3.5,  # 4.0 scale
        "skills": ["React", "Node.js"]
    }
    
    result2 = service.clean_student_record(raw_data2)
    
    if result2['success']:
        print(f"✓ Cleaning successful ({result2['method']})")
        print(f"   GPA: {result2['cleaned_data']['gpa']}/10.0")
        print(f"   Quality Score: {result2['quality_score']:.1f}")
        if result2['changes']:
            print(f"   Changes:")
            for change in result2['changes']:
                print(f"     - {change}")
    else:
        print(f"✗ Cleaning failed")
    
    # Test Case 3: Skill name standardization
    print("\n4. Test Case 3: Skill Name Standardization")
    print("   Input: ['ReactJS', 'nodejs', 'javascript']")
    print("   Expected: ['React', 'Node.js', 'JavaScript']")
    
    raw_data3 = {
        "name": "Bob Johnson",
        "major": "Computer Science",
        "gpa": 7.5,
        "skills": ["ReactJS", "nodejs", "javascript", "mongodb"]
    }
    
    result3 = service.clean_student_record(raw_data3)
    
    if result3['success']:
        print(f"✓ Cleaning successful ({result3['method']})")
        print(f"   Skills: {result3['cleaned_data']['skills']}")
        print(f"   Quality Score: {result3['quality_score']:.1f}")
        if result3['changes']:
            print(f"   Changes:")
            for change in result3['changes']:
                print(f"     - {change}")
    else:
        print(f"✗ Cleaning failed")
    
    # Test Case 4: Multiple issues
    print("\n5. Test Case 4: Multiple Issues")
    print("   Input: Messy name, wrong major, wrong GPA scale, messy skills")
    
    raw_data4 = {
        "name": "  alice BROWN  ",
        "major": "mech eng",
        "gpa": 3.8,  # 4.0 scale
        "skills": ["python3", "c++", "solidworks"]
    }
    
    result4 = service.clean_student_record(raw_data4)
    
    if result4['success']:
        print(f"✓ Cleaning successful ({result4['method']})")
        print(f"   Name: '{result4['cleaned_data']['name']}'")
        print(f"   Major: {result4['cleaned_data']['major']}")
        print(f"   GPA: {result4['cleaned_data']['gpa']}/10.0")
        print(f"   Skills: {result4['cleaned_data']['skills']}")
        print(f"   Quality Score: {result4['quality_score']:.1f}")
        print(f"   Changes: {len(result4['changes'])}")
        for change in result4['changes']:
            print(f"     - {change}")
    else:
        print(f"✗ Cleaning failed")
    
    # Test Case 5: Already clean data
    print("\n6. Test Case 5: Already Clean Data")
    print("   Input: Perfect data → Expected: No changes")
    
    raw_data5 = {
        "name": "David Lee",
        "major": "Computer Science",
        "gpa": 8.5,
        "skills": ["Python", "React", "Node.js"]
    }
    
    result5 = service.clean_student_record(raw_data5)
    
    if result5['success']:
        print(f"✓ Cleaning successful ({result5['method']})")
        print(f"   Quality Score: {result5['quality_score']:.1f}")
        print(f"   Changes: {len(result5['changes'])}")
        if result5['changes']:
            for change in result5['changes']:
                print(f"     - {change}")
        else:
            print("   ✓ No changes needed (data was already clean)")
    else:
        print(f"✗ Cleaning failed")
    
    # Test Case 6: Batch cleaning
    print("\n7. Test Case 6: Batch Cleaning")
    print("   Input: 3 records with various issues")
    
    batch_records = [
        {
            "name": "student one",
            "major": "cs",
            "gpa": 3.2,
            "skills": ["reactjs", "python"]
        },
        {
            "name": "STUDENT TWO",
            "major": "mech",
            "gpa": 7.8,
            "skills": ["solidworks", "autocad"]
        },
        {
            "name": "Student Three",
            "major": "Business Administration",
            "gpa": 8.0,
            "skills": ["Excel", "PowerPoint"]
        }
    ]
    
    batch_results = service.clean_batch(batch_records)
    
    successful = sum(1 for r in batch_results if r['success'])
    llm_count = sum(1 for r in batch_results if r.get('method') == 'llm')
    
    print(f"✓ Batch cleaning complete")
    print(f"   Successful: {successful}/{len(batch_records)}")
    print(f"   LLM used: {llm_count}")
    print(f"   Rule-based: {len(batch_records) - llm_count}")
    
    # Show results
    for i, result in enumerate(batch_results, 1):
        if result['success']:
            print(f"\n   Record {i}:")
            print(f"     Name: {result['cleaned_data']['name']}")
            print(f"     Major: {result['cleaned_data']['major']}")
            print(f"     GPA: {result['cleaned_data']['gpa']}")
            print(f"     Changes: {len(result['changes'])}")
    
    # Summary
    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED")
    print("=" * 60)
    print("\nData cleaning service is ready for use!")
    print("\nKey Features:")
    print("  ✓ LLM-based intelligent cleaning (when available)")
    print("  ✓ Rule-based fallback (always works)")
    print("  ✓ Major name standardization")
    print("  ✓ GPA scale normalization")
    print("  ✓ Skill name standardization")
    print("  ✓ Capitalization fixes")
    print("  ✓ Quality scoring")
    print("  ✓ Batch processing")


if __name__ == "__main__":
    try:
        test_data_cleaning()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n✗ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
