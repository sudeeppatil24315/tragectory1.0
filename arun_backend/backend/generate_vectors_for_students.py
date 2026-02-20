"""
Generate vectors for existing students and store in Qdrant

This script:
1. Fetches all students from PostgreSQL
2. Generates vectors for each student
3. Stores vectors in Qdrant
"""

import sys
from pathlib import Path
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models import Student, DigitalWellbeingData, Skill
from app.services.vector_generation import generate_student_vector
from app.services.qdrant_service import QdrantService


def generate_vectors_for_all_students():
    """Generate and store vectors for all students"""
    db = SessionLocal()
    qdrant = QdrantService(host="localhost", port=6333)
    
    try:
        print("="*60)
        print("🔄 Vector Generation for Existing Students")
        print("="*60)
        
        # Get all students
        students = db.query(Student).all()
        print(f"\n📊 Found {len(students)} students in database")
        
        if len(students) == 0:
            print("⚠️  No students found in database!")
            return
        
        vectors_generated = 0
        
        for student in students:
            try:
                print(f"\n👤 Processing: {student.name} (ID: {student.id})")
                
                # Get behavioral data (last 7 days)
                behavioral_data = db.query(DigitalWellbeingData)\
                    .filter(DigitalWellbeingData.student_id == student.id)\
                    .order_by(DigitalWellbeingData.date.desc())\
                    .limit(7)\
                    .all()
                
                if not behavioral_data:
                    print(f"   ⚠️  No behavioral data found, skipping...")
                    continue
                
                # Calculate averages from behavioral data
                avg_screen_time = sum(float(d.screen_time_hours) for d in behavioral_data) / len(behavioral_data)
                avg_social_media = sum(float(d.social_media_hours) for d in behavioral_data) / len(behavioral_data)
                avg_sleep = sum(float(d.sleep_duration_hours) for d in behavioral_data) / len(behavioral_data)
                
                # Get skills
                skills = db.query(Skill)\
                    .filter(Skill.student_id == student.id)\
                    .all()
                
                languages = ", ".join([s.skill_name for s in skills]) if skills else "Python"
                
                # Prepare student profile for vector generation
                student_profile = {
                    'gpa': float(student.gpa) if student.gpa else 7.0,
                    'attendance': float(student.attendance) if student.attendance else 75.0,
                    'internal_marks': 75.0,  # Default
                    'backlogs': student.backlogs if student.backlogs else 0,
                    'study_hours_per_week': float(student.study_hours_per_week) if student.study_hours_per_week else 20.0,
                    'practice_hours': 2.0,  # Default
                    'project_count': student.project_count if student.project_count else 0,
                    'consistency': 3,  # Default
                    'problem_solving': 3,  # Default
                    'languages': languages,
                    'communication': 3,  # Default
                    'teamwork': 3,  # Default
                    'deployed': False,  # Default
                    'internship': False,  # Default
                    'career_clarity': 3,  # Default
                    'major': student.major
                }
                
                wellbeing_data = [{
                    'screen_time_hours': avg_screen_time,
                    'social_media_hours': avg_social_media,
                    'distraction_level': 3,  # Default
                    'sleep_duration_hours': avg_sleep
                }]
                
                print(f"   🔄 Generating vector...")
                vector = generate_student_vector(student_profile, wellbeing_data)
                
                # Store in Qdrant
                metadata = {
                    'student_id': student.id,
                    'major': student.major,
                    'gpa': float(student.gpa) if student.gpa else 7.0,
                    'name': student.name
                }
                
                success = qdrant.store_student_vector(
                    student_id=student.id,
                    vector=vector,
                    metadata=metadata
                )
                
                if success:
                    print(f"   ✅ Vector stored in Qdrant")
                    vectors_generated += 1
                else:
                    print(f"   ❌ Failed to store vector in Qdrant")
                
            except Exception as e:
                print(f"   ❌ Error processing student: {str(e)}")
                continue
        
        print(f"\n{'='*60}")
        print(f"✅ Vector generation complete!")
        print(f"📊 Vectors generated: {vectors_generated}/{len(students)}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    print("="*60)
    print("🚀 Vector Generation Script")
    print("="*60)
    print(f"🗄️  Database: PostgreSQL")
    print(f"🔍 Vector DB: Qdrant (localhost:6333)")
    print("="*60)
    
    generate_vectors_for_all_students()
