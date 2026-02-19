from sqlalchemy.orm import Session
from app.models import Student, StudentSubjectScore
from fastapi import HTTPException

def create_student_profile(db: Session, student_data: dict):
    # Validation logic
    gpa = student_data.get("gpa")
    attendance = student_data.get("attendance")
    user_id = student_data.get("user_id")
    
    if gpa is not None and not (0 <= gpa <= 10):
        raise HTTPException(status_code=400, detail="GPA must be between 0 and 10")
    if attendance is not None and not (0 <= attendance <= 100):
        raise HTTPException(status_code=400, detail="Attendance must be between 0 and 100")

    # Handle Swagger default '0' for user_id which might not exist
    if user_id == 0:
        student_data["user_id"] = None

    try:
        new_student = Student(**student_data)
        db.add(new_student)
        db.commit()
        db.refresh(new_student)
        return new_student
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def get_all_students(db: Session):
    return db.query(Student).all()

def add_subject_scores(db: Session, student_id: int, scores: list):
    # Check if student exists
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    try:
        db_scores = []
        for score in scores:
            db_score = StudentSubjectScore(
                student_id=student_id,
                subject_name=score["subject_name"],
                marks=score["marks"],
                semester=score.get("semester", student.semester)
            )
            db.add(db_score)
            db_scores.append(db_score)
        
        db.commit()
        return db_scores
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")

def get_full_student_profile(db: Session, student_id: int):
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    scores = db.query(StudentSubjectScore).filter(StudentSubjectScore.student_id == student_id).all()
    
    return {
        "id": student.id,
        "name": student.name,
        "usn": student.usn,
        "major": student.major,
        "semester": student.semester,
        "gpa": student.gpa,
        "attendance": student.attendance,
        "subject_scores": [
            {"subject": s.subject_name, "marks": s.marks, "semester": s.semester} 
            for s in scores
        ]
    }
