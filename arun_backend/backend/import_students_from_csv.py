"""
Import student data from froms.csv into PostgreSQL and Qdrant

This script:
1. Reads student data from froms.csv
2. Creates user accounts for each student
3. Creates student profiles with all data
4. Generates vectors and stores them in Qdrant
"""

import csv
import sys
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.orm import Session
from app.db import SessionLocal, engine
from app.models import User, Student, DigitalWellbeingData, Skill, SleepQualityEnum
from app.services.vector_generation import generate_student_vector
from app.services.qdrant_service import QdrantService
from passlib.context import CryptContext

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def parse_yes_no(value: str) -> bool:
    """Convert Yes/No to boolean"""
    if not value:
        return False
    return value.strip().lower() in ['yes', 'y', 'true']


def parse_float(value: str, default: float = 0.0) -> float:
    """Safely parse float value"""
    if not value or value.strip() == '':
        return default
    try:
        return float(value.strip())
    except ValueError:
        return default


def parse_int(value: str, default: int = 0) -> int:
    """Safely parse int value"""
    if not value or value.strip() == '':
        return default
    try:
        return int(value.strip())
    except ValueError:
        return default


def calculate_focus_score(social_media: float, learning: float, entertainment: float) -> float:
    """Calculate focus score from app usage"""
    productive = learning
    distracting = social_media + entertainment
    
    if distracting == 0:
        return 1.0 if productive > 0 else 0.5
    
    focus = productive / distracting
    return min(focus / 2.0, 1.0)


def import_students_from_csv(csv_path: str):
    """Import students from CSV file"""
    db = SessionLocal()
    qdrant = QdrantService(host="localhost", port=6333)
    
    try:
        print(f"📂 Reading CSV file: {csv_path}")
        
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            students_imported = 0
            
            for row in reader:
                try:
                    email = row['Email Address'].strip().lower()
                    full_name = row['Full Name'].strip()
                    
                    print(f"\n👤 Processing: {full_name} ({email})")
                    
                    # Check if user already exists
                    existing_user = db.query(User).filter(User.email == email).first()
                    if existing_user:
                        print(f"   ⚠️  User already exists, skipping...")
                        continue
                    
                    # Create user account
                    user = User(
                        email=email,
                        password_hash=hash_password("password123"),  # Default password
                        role="student",
                        created_at=datetime.utcnow()
                    )
                    db.add(user)
                    db.flush()
                    print(f"   ✅ Created user account (ID: {user.id})")
                    
                    # Parse student data
                    major = row['Major / Branch'].strip()
                    semester = parse_int(row['Current Semester'], 7)
                    gpa = parse_float(row['Current GPA (0–10)'], 7.0)
                    attendance = parse_float(row['Average Attendance Percentage'].replace('%', ''), 75.0)
                    internal_marks = parse_float(row['Average Internal Marks (0–100)'], 75.0)
                    backlogs = parse_int(row['Number of Backlogs'], 0)
                    
                    # Study habits
                    study_hours_per_day = parse_float(row['Study hours per day'], 3.0)
                    study_hours_per_week = study_hours_per_day * 7
                    practice_hours = parse_float(row['Technical Knowledge practice hours per day'], 1.0)
                    
                    # Skills and projects
                    project_count = parse_int(row['Number of Projects Completed'], 0)
                    problem_solving = parse_int(row['Problem Solving Ability (1–5)'], 3)
                    communication = parse_int(row['Communication Skill (1–5)'], 3)
                    teamwork = parse_int(row['Teamwork Ability (1–5)'], 3)
                    consistency = parse_int(row['Consistency Level (1–5)'], 3)
                    career_clarity = parse_int(row['Career clarity level (1–5)'], 3)
                    
                    # Boolean fields
                    deployed = parse_yes_no(row['Have you deployed a project?'])
                    internship = parse_yes_no(row['Internship experience?'])
                    
                    # Programming languages
                    languages = row['Programming Languages Select all that apply)'].strip()
                    
                    # Create student profile
                    student = Student(
                        user_id=user.id,
                        name=full_name,
                        major=major,
                        semester=semester,
                        gpa=Decimal(str(gpa)),
                        attendance=Decimal(str(attendance)),
                        study_hours_per_week=Decimal(str(study_hours_per_week)),
                        project_count=project_count,
                        created_at=datetime.utcnow(),
                        updated_at=datetime.utcnow()
                    )
                    db.add(student)
                    db.flush()
                    print(f"   ✅ Created student profile (ID: {student.id})")
                    
                    # Add digital wellbeing data
                    screen_time = parse_float(row['Average daily screen time (hours)'], 6.0)
                    social_media = parse_float(row['Daily social media time (hours)'], 2.0)
                    learning_time = parse_float(row['Daily learning app/video time (hours)'], 2.0)
                    entertainment = parse_float(row['Daily entertainment time (hours)'], 2.0)
                    sleep_hours = parse_float(row['Average sleep hours'], 7.0)
                    distraction_level = parse_int(row['Distraction level while studying (1–5)'], 3)
                    
                    focus_score = calculate_focus_score(social_media, learning_time, entertainment)
                    
                    # Add behavioral data for last 7 days
                    for days_ago in range(7):
                        behavioral_date = date.today() - __import__('datetime').timedelta(days=days_ago)
                        
                        # Determine sleep quality based on hours
                        if sleep_hours >= 7:
                            sleep_quality = SleepQualityEnum.GOOD
                        elif sleep_hours >= 5:
                            sleep_quality = SleepQualityEnum.FAIR
                        else:
                            sleep_quality = SleepQualityEnum.POOR
                        
                        wellbeing = DigitalWellbeingData(
                            student_id=student.id,
                            date=behavioral_date,
                            screen_time_hours=Decimal(str(screen_time)),
                            educational_app_hours=Decimal(str(learning_time)),
                            social_media_hours=Decimal(str(social_media)),
                            entertainment_hours=Decimal(str(entertainment)),
                            productivity_hours=Decimal(str(practice_hours)),
                            communication_hours=Decimal("0.5"),
                            focus_score=Decimal(str(focus_score)),
                            sleep_duration_hours=Decimal(str(sleep_hours)),
                            sleep_quality=sleep_quality,
                            synced_at=datetime.utcnow()
                        )
                        db.add(wellbeing)
                    
                    print(f"   ✅ Added 7 days of behavioral data")
                    
                    # Add skills
                    skills_list = languages.split(',')
                    for skill_name in skills_list[:5]:  # Limit to 5 skills
                        skill_name = skill_name.strip()
                        if skill_name:
                            skill = Skill(
                                student_id=student.id,
                                skill_name=skill_name,
                                proficiency_score=Decimal(str(problem_solving * 20)),  # Convert 1-5 to 0-100
                                quiz_score=None,
                                voice_score=None,
                                market_weight=Decimal("1.0"),
                                last_assessed_at=datetime.utcnow(),
                                created_at=datetime.utcnow(),
                                updated_at=datetime.utcnow()
                            )
                            db.add(skill)
                    
                    print(f"   ✅ Added {len(skills_list[:5])} skills")
                    
                    # Commit to database
                    db.commit()
                    db.refresh(student)
                    
                    # Generate vector and store in Qdrant
                    print(f"   🔄 Generating vector...")
                    student_profile = {
                        'gpa': float(gpa),
                        'attendance': float(attendance),
                        'internal_marks': float(internal_marks),
                        'backlogs': backlogs,
                        'study_hours_per_week': float(study_hours_per_week),
                        'practice_hours': float(practice_hours),
                        'project_count': project_count,
                        'consistency': consistency,
                        'problem_solving': problem_solving,
                        'languages': languages,
                        'communication': communication,
                        'teamwork': teamwork,
                        'deployed': deployed,
                        'internship': internship,
                        'career_clarity': career_clarity,
                        'major': major
                    }
                    
                    wellbeing_data = [{
                        'screen_time_hours': screen_time,
                        'social_media_hours': social_media,
                        'distraction_level': distraction_level,
                        'sleep_duration_hours': sleep_hours
                    }]
                    
                    vector = generate_student_vector(student_profile, wellbeing_data)
                    
                    # Store in Qdrant
                    success = qdrant.store_student_vector(
                        student_id=student.id,
                        vector=vector,
                        metadata={
                            'student_id': student.id,
                            'major': major,
                            'gpa': float(gpa),
                            'name': full_name
                        }
                    )
                    
                    if success:
                        print(f"   ✅ Vector stored in Qdrant")
                        students_imported += 1
                    else:
                        print(f"   ⚠️  Failed to store vector in Qdrant")
                    
                    print(f"   ✨ Successfully imported {full_name}!")
                    
                except Exception as e:
                    print(f"   ❌ Error importing student: {str(e)}")
                    db.rollback()
                    continue
        
        print(f"\n{'='*60}")
        print(f"✅ Import complete!")
        print(f"📊 Total students imported: {students_imported}")
        print(f"{'='*60}")
        
    except Exception as e:
        print(f"\n❌ Fatal error: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    csv_path = Path(__file__).parent.parent / "froms.csv"
    
    if not csv_path.exists():
        print(f"❌ CSV file not found: {csv_path}")
        sys.exit(1)
    
    print("="*60)
    print("🚀 Student Data Import Script")
    print("="*60)
    print(f"📁 CSV File: {csv_path}")
    print(f"🗄️  Database: PostgreSQL")
    print(f"🔍 Vector DB: Qdrant")
    print("="*60)
    
    import_students_from_csv(str(csv_path))
