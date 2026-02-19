from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from app.db import get_db
from app.services import student_service

router = APIRouter(tags=["students"])

# --- Pydantic Schemas ---
class SubjectScoreBase(BaseModel):
    subject_name: str
    marks: float
    semester: int

class SubjectScoreCreate(BaseModel):
    student_id: int
    scores: List[SubjectScoreBase]

class StudentCreate(BaseModel):
    name: str
    usn: Optional[str] = None
    major: str
    semester: Optional[int] = 1
    gpa: float = Field(..., ge=0, le=10)
    attendance: float = Field(..., ge=0, le=100)
    user_id: Optional[int] = None

class StudentFetchRequest(BaseModel):
    student_id: int = Field(..., ge=1)

class StudentResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    usn: Optional[str] = None
    name: Optional[str] = "Unknown"
    major: Optional[str] = "Unspecified"
    semester: Optional[int] = 0
    gpa: Optional[float] = 0.0
    attendance: Optional[float] = 0.0
    
    class Config:
        from_attributes = True

# --- Routes ---

@router.post("/students", response_model=StudentResponse)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    """Create a new student profile with GPA and Attendance validation."""
    return student_service.create_student_profile(db, student.model_dump())

@router.post("/list", response_model=List[StudentResponse])
def list_students(db: Session = Depends(get_db)):
    """Retrieve all students via POST for data integrity."""
    return student_service.get_all_students(db)

@router.post("/subjects")
def add_subjects(data: SubjectScoreCreate, db: Session = Depends(get_db)):
    """Add multiple subject scores for a specific student."""
    scores_data = [s.model_dump() for s in data.scores]
    student_service.add_subject_scores(db, data.student_id, scores_data)
    return {"message": f"Successfully added {len(data.scores)} subject scores"}

@router.post("/full-profile")
def get_full_profile(request: StudentFetchRequest, db: Session = Depends(get_db)):
    """Get student basic info, cumulative GPA, attendance, and all subject scores via POST."""
    return student_service.get_full_student_profile(db, request.student_id)

@router.post("/debug-fetch")
def debug_students(db: Session = Depends(get_db)):
    """Raw debug endpoint to see what exactly is in the DB via POST."""
    from sqlalchemy import text
    result = db.execute(text("SELECT * FROM students")).fetchall()
    return [dict(row._mapping) for row in result]
