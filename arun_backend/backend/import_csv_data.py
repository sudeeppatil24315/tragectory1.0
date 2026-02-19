import csv
import os
import sys
# Add backend directory to path to import app modules
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from sqlalchemy import text
from app.db import SessionLocal, engine
from app.models import Base, User, Student, StudentSubjectScore, BehavioralMetric, DigitalWellbeingDaily
from app.services.vector_gen_service import generate_and_store_student_vector
from datetime import datetime

CSV_PATH = r"C:\Users\arunp\OneDrive\Desktop\trajectory-x-main\data.csv"

def sync_schema():
    print("Syncing database schema (updating columns)...")
    Base.metadata.create_all(bind=engine)

def cleanup_old_import():
    """Wipe most tables to start clean with new schema."""
    db = SessionLocal()
    try:
        db.execute(text("TRUNCATE TABLE student_subject_scores, behavioral_metrics, digital_wellbeing_daily, vector_profiles, students RESTART IDENTITY CASCADE"))
        db.commit()
        print("Database wiped for fresh import.")
    except Exception as e:
        print(f"Cleanup Error: {e}")
        db.rollback()
    finally:
        db.close()

def parse_bool(val):
    if not val: return False
    return val.strip().lower() in ['yes', 'true', '1', 'always']

def import_data():
    sync_schema()
    cleanup_old_import()
    
    db = SessionLocal()
    try:
        with open(CSV_PATH, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                try:
                    email = row.get('Email Address') or row.get('Email address')
                    if not email: continue
                    email = email.strip()

                    # 1. User Logic
                    user = db.query(User).filter(User.email == email).first()
                    if not user:
                        user = User(email=email, password_hash="placeholder", role="student")
                        db.add(user)
                        db.commit()
                        user = db.query(User).filter(User.email == email).first()

                    # 2. Student Logic
                    is_alumni = (row.get('Are you a Student or Alumni?', '').lower() == 'alumni')
                    
                    student = Student(
                        user_id=user.id,
                        name=row.get('Full Name', 'Unknown'),
                        age=int(row.get('Age', 0) or 0),
                        gender=row.get('Gender', 'Unspecified'),
                        major=row.get('Major / Branch', 'Unspecified'),
                        semester=int(row.get('Current Semester', 0) or 0),
                        college_name=row.get('College Name', ''),
                        is_alumni=is_alumni,
                        gpa=float(row.get('Current GPA (0–10)', 0) or 0),
                        gpa_trend=row.get('GPA Trend Over Last Semesters', 'Stable'),
                        attendance=float(row.get('Average Attendance Percentage', 0) or 0),
                        backlogs=int(row.get('Number of Backlogs', 0) or 0),
                        programming_languages=row.get('Programming Languages Select all that apply)', ''),
                        strongest_skill=row.get('Strongest Technical Skill', ''),
                        placement_status=row.get('Placement status ', 'Not Placed'),
                        usn=f"USN_{user.id}_{int(datetime.now().timestamp())}",
                        
                        # New Career Fields
                        biggest_strength=row.get('Biggest strength', ''),
                        biggest_weakness=row.get('Biggest weakness', ''),
                        habit_to_improve=row.get('One habit you want to improve', ''),
                        what_holds_back=row.get('What holds you back the most', ''),
                        career_clarity=float(row.get('Career clarity level (1–5)', 0) or 0),
                        chosen_career_path=row.get('Have you chosen a career path?', ''),
                        daily_placement_prep=parse_bool(row.get('Daily placement preparation?')),
                        interview_fear=float(row.get('Interview fear level (1–5)', 0) or 0),
                        confidence_level=float(row.get('Confidence level (1–5)', 0) or 0),
                        
                        # New Placement Success Metrics
                        role_relevance=float(row.get('Role relevance to major (0–100%)', 0) or 0),
                        placement_attempts=int(row.get('Number of placement attempts', 0) or 0),
                        months_to_get_placed=int(row.get('Months taken to get placed', 0) or 0)
                    )
                    db.add(student)
                    db.commit()
                    db.refresh(student)

                    # 3. Subjects - Fixed Mapping for inconsistent headers
                    subject_mappings = [
                        ('Subject 1 Name(current semester)', 'Subject 1 Marks (0–100)'),
                        ('Subject 2 Name (current semester)', 'Subject 2 Marks (0–100)'),
                        ('Subject 3 Name (current semester)', 'Subject 3 Marks (0–100)'),
                        ('Subject 4 Name', 'Subject 4 Marks (0–100)'),
                        ('Subject 5 Name (current semester)', 'Subject 5 Marks (0–100)')
                    ]

                    for name_key, marks_key in subject_mappings:
                        sub_name = row.get(name_key)
                        sub_marks = row.get(marks_key)
                        if sub_name and sub_marks:
                            db.add(StudentSubjectScore(
                                student_id=student.id, 
                                student_name=student.name,
                                semester=student.semester, 
                                subject_name=sub_name.strip(), 
                                marks=float(sub_marks)
                            ))

                    # 4. Behavioral Metrics
                    db.add(BehavioralMetric(
                        student_id=student.id,
                        study_hours_per_week=float(row.get('Study hours per day', 0) or 0) * 7,
                        practice_hours_per_day=float(row.get('Technical Knowledge practice hours per day', 0) or 0),
                        project_count=int(row.get('Number of Projects Completed', 0) or 0),
                        project_types=row.get('Project Types (Select all that apply)', ''),
                        deployed_project=parse_bool(row.get('Have you deployed a project?')),
                        internship_exp=parse_bool(row.get('Internship experience?')),
                        internship_duration=int(row.get('Internship duration in months', 0) or 0),
                        problem_solving=float(row.get('Problem Solving Ability (1–5)', 0) or 0),
                        communication=float(row.get('Communication Skill (1–5)', 0) or 0),
                        teamwork=float(row.get('Teamwork Ability (1–5)', 0) or 0),
                        consistency=float(row.get('Consistency Level (1–5)', 0) or 0),
                        
                        # New Habits
                        attend_lab_regularly=parse_bool(row.get('Do you attend lab sessions regularly?')),
                        submit_assignments_on_time=parse_bool(row.get('Do you submit assignments on time?')),
                        avg_internal_marks=float(row.get('Average Internal Marks (0–100)', 0) or 0),
                        follow_study_schedule=parse_bool(row.get('Do you follow a study schedule?')),
                        concept_revision_frequency=row.get('Concept revision frequency', ''),
                        online_courses_count=row.get('Online courses completed (list/count)', ''),
                        
                        skill_score=float(row.get('Confidence level (1–5)', 3) or 3) * 2
                    ))

                    # 5. Digital Wellbeing (Daily snapshot)
                    db.add(DigitalWellbeingDaily(
                        student_id=student.id,
                        date=datetime.utcnow().date(),
                        total_screen_time=float(row.get('Average daily screen time (hours)', 0) or 0),
                        social_time=float(row.get('Daily social media time (hours)', 0) or 0),
                        educational_time=float(row.get('Daily learning app/video time (hours)', 0) or 0),
                        entertainment_time=float(row.get('Daily entertainment time (hours)', 0) or 0),
                        sleep_hours=float(row.get('Average sleep hours', 8) or 8),
                        
                        # New Wellbeing
                        sleep_schedule=row.get('Sleep schedule', ''),
                        use_phone_while_studying=parse_bool(row.get('Do you use phone while studying?')),
                        distraction_level=float(row.get('Distraction level while studying (1–5)', 0) or 0),
                        mental_exhaustion=parse_bool(row.get('Mental exhaustion often?')),
                        
                        focus_score=float(row.get('Career clarity level (1–5)', 3) or 3) * 2
                    ))

                    db.commit()
                    print(f"Imported Full Profile: {student.name}")
                    
                    # 6. Generate Vector (this will now use much more data!)
                    try:
                        generate_and_store_student_vector(db, student.id)
                    except: pass
                    
                    count += 1
                except Exception as e:
                    print(f"Row Error for {row.get('Full Name')}: {e}")
                    db.rollback()

        print(f"Migration Complete: {count} detailed student profiles created.")
    finally:
        db.close()

if __name__ == "__main__":
    import_data()
