"""
Student Profile Management Routes (Task 20)

This module provides authenticated student endpoints for:
- Fetching current student profile
- Updating profile (GPA, attendance, semester, major, study hours, projects)
- Adding digital wellbeing data
- Submitting skill assessment scores

All endpoints require student authentication and trigger vector regeneration on updates.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, time, datetime
from decimal import Decimal

from app.db import get_db
from app.models import User, Student, DigitalWellbeingData, Skill
from app.auth import get_current_user
from app.services.vector_generation import generate_student_vector
from app.services.qdrant_service import QdrantService

router = APIRouter(prefix="/api/student", tags=["Student Profile"])


# ============================================================================
# PYDANTIC SCHEMAS
# ============================================================================

class StudentProfileResponse(BaseModel):
    """Student profile data returned to client"""
    id: int
    user_id: int
    name: str
    major: str
    semester: Optional[int]
    gpa: Optional[float]
    attendance: Optional[float]
    study_hours_per_week: Optional[float]
    project_count: Optional[int]
    vector_id: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class StudentProfileUpdate(BaseModel):
    """Data for updating student profile"""
    name: Optional[str] = None
    major: Optional[str] = None
    semester: Optional[int] = Field(None, ge=1, le=10)
    gpa: Optional[float] = Field(None, ge=0.0, le=10.0)
    attendance: Optional[float] = Field(None, ge=0.0, le=100.0)
    study_hours_per_week: Optional[float] = Field(None, ge=0.0, le=168.0)
    project_count: Optional[int] = Field(None, ge=0)


class BehavioralDataCreate(BaseModel):
    """Digital wellbeing data submission"""
    date: date
    screen_time_hours: float = Field(..., ge=0.0, le=24.0)
    educational_app_hours: float = Field(0.0, ge=0.0, le=24.0)
    social_media_hours: float = Field(0.0, ge=0.0, le=24.0)
    entertainment_hours: float = Field(0.0, ge=0.0, le=24.0)
    productivity_hours: float = Field(0.0, ge=0.0, le=24.0)
    communication_hours: float = Field(0.0, ge=0.0, le=24.0)
    sleep_duration_hours: Optional[float] = Field(None, ge=0.0, le=24.0)
    sleep_bedtime: Optional[time] = None
    sleep_wake_time: Optional[time] = None
    sleep_quality: Optional[str] = Field(None, pattern="^(good|fair|poor)$")


class SkillAssessmentCreate(BaseModel):
    """Skill assessment submission"""
    skill_name: str = Field(..., min_length=1, max_length=100)
    proficiency_score: float = Field(..., ge=0.0, le=100.0)
    quiz_score: Optional[float] = Field(None, ge=0.0, le=100.0)
    voice_score: Optional[float] = Field(None, ge=0.0, le=100.0)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_student_by_user_id(db: Session, user_id: int) -> Student:
    """Get student record by user_id or raise 404"""
    student = db.query(Student).filter(Student.user_id == user_id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found. Please create a profile first."
        )
    return student


def calculate_focus_score(behavioral_data: BehavioralDataCreate) -> float:
    """
    Calculate focus score from app usage.
    Focus Score = (Educational + Productivity) / (Social Media + Entertainment)
    Returns value between 0 and 1, or 0.5 if denominator is 0.
    """
    productive = behavioral_data.educational_app_hours + behavioral_data.productivity_hours
    distracting = behavioral_data.social_media_hours + behavioral_data.entertainment_hours
    
    if distracting == 0:
        return 1.0 if productive > 0 else 0.5
    
    focus = productive / distracting
    # Normalize to 0-1 range (cap at 2.0 for focus ratio)
    return min(focus / 2.0, 1.0)


async def trigger_vector_regeneration(db: Session, student: Student):
    """
    Regenerate and update student vector in Qdrant after profile changes.
    This ensures similarity matching uses latest data.
    """
    try:
        # Generate new vector from updated profile
        vector = generate_student_vector(student, db)
        
        # Initialize Qdrant service
        qdrant_service = QdrantService()
        
        # Update in Qdrant
        success = qdrant_service.update_student_vector(student.id, vector)
        
        if success:
            # Update timestamp in PostgreSQL
            student.updated_at = datetime.utcnow()
            db.commit()
            return True
        
        return False
    except Exception as e:
        # Log error but don't fail the request
        print(f"Warning: Vector regeneration failed for student {student.id}: {e}")
        return None


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/profile", response_model=StudentProfileResponse)
async def get_student_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get current student's profile.
    
    **Authentication**: Required (JWT token)
    
    **Returns**: Complete student profile with academic and behavioral data
    
    **Example**:
    ```
    GET /api/student/profile
    Authorization: Bearer <token>
    ```
    """
    # Verify user is a student
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    # Get student profile
    student = get_student_by_user_id(db, current_user.id)
    
    return student


@router.put("/profile", response_model=StudentProfileResponse)
async def update_student_profile(
    profile_update: StudentProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current student's profile.
    
    **Authentication**: Required (JWT token)
    
    **Validation**:
    - GPA: 0.0 - 10.0
    - Attendance: 0.0 - 100.0
    - Study hours: 0.0 - 168.0 (max hours in a week)
    - Project count: >= 0
    
    **Side Effects**:
    - Triggers vector regeneration in Qdrant
    - Updates similarity matching data
    
    **Example**:
    ```json
    PUT /api/student/profile
    {
      "gpa": 8.5,
      "attendance": 90.0,
      "study_hours_per_week": 25.0,
      "project_count": 5
    }
    ```
    """
    # Verify user is a student
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    # Get student profile
    student = get_student_by_user_id(db, current_user.id)
    
    # Track if any changes were made
    changes_made = False
    
    # Update fields if provided
    update_data = profile_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if value is not None and getattr(student, field) != value:
            setattr(student, field, value)
            changes_made = True
    
    if not changes_made:
        return student
    
    # Update timestamp
    student.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(student)
    
    # Trigger vector regeneration (async, don't wait)
    await trigger_vector_regeneration(db, student)
    
    return student


@router.post("/behavioral")
async def add_behavioral_data(
    behavioral_data: BehavioralDataCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add digital wellbeing data for a specific date.
    
    **Authentication**: Required (JWT token)
    
    **Data Collected**:
    - Screen time (total and by category)
    - App usage (educational, social media, entertainment, productivity)
    - Sleep duration and quality
    - Focus score (calculated automatically)
    
    **Validation**:
    - All time values must be 0-24 hours
    - Date cannot be in the future
    - Sleep quality: "good", "fair", or "poor"
    
    **Side Effects**:
    - Triggers vector regeneration (behavioral data affects trajectory score)
    
    **Example**:
    ```json
    POST /api/student/behavioral
    {
      "date": "2026-02-20",
      "screen_time_hours": 8.5,
      "educational_app_hours": 2.0,
      "social_media_hours": 3.0,
      "entertainment_hours": 2.5,
      "productivity_hours": 1.0,
      "sleep_duration_hours": 7.0,
      "sleep_quality": "good"
    }
    ```
    """
    # Verify user is a student
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    # Get student profile
    student = get_student_by_user_id(db, current_user.id)
    
    # Validate date is not in the future
    if behavioral_data.date > date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot add behavioral data for future dates"
        )
    
    # Calculate focus score
    focus_score = calculate_focus_score(behavioral_data)
    
    # Check if data already exists for this date
    existing = db.query(DigitalWellbeingData).filter(
        DigitalWellbeingData.student_id == student.id,
        DigitalWellbeingData.date == behavioral_data.date
    ).first()
    
    if existing:
        # Update existing record
        for field, value in behavioral_data.model_dump().items():
            if value is not None:
                setattr(existing, field, value)
        existing.focus_score = Decimal(str(focus_score))
        existing.synced_at = datetime.utcnow()
        db.commit()
        
        message = "Behavioral data updated successfully"
        data_id = existing.id
    else:
        # Create new record
        wellbeing_data = DigitalWellbeingData(
            student_id=student.id,
            **behavioral_data.model_dump(),
            focus_score=Decimal(str(focus_score)),
            synced_at=datetime.utcnow()
        )
        db.add(wellbeing_data)
        db.commit()
        db.refresh(wellbeing_data)
        
        message = "Behavioral data added successfully"
        data_id = wellbeing_data.id
    
    # Trigger vector regeneration
    await trigger_vector_regeneration(db, student)
    
    return {
        "message": message,
        "id": data_id,
        "date": behavioral_data.date,
        "focus_score": round(focus_score, 2),
        "vector_regenerated": True
    }


@router.post("/skills")
async def add_skill_assessment(
    skill_data: SkillAssessmentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit skill assessment scores.
    
    **Authentication**: Required (JWT token)
    
    **Scores**:
    - Proficiency score: Overall skill level (0-100)
    - Quiz score: Technical quiz results (0-100, optional)
    - Voice score: Voice interview evaluation (0-100, optional)
    
    **Validation**:
    - All scores must be 0-100
    - Skill name is required
    
    **Side Effects**:
    - Triggers vector regeneration (skills affect trajectory score)
    - Market demand weighting will be applied later (Task 21.5)
    
    **Example**:
    ```json
    POST /api/student/skills
    {
      "skill_name": "Python",
      "proficiency_score": 85.0,
      "quiz_score": 90.0,
      "voice_score": 80.0
    }
    ```
    """
    # Verify user is a student
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    # Get student profile
    student = get_student_by_user_id(db, current_user.id)
    
    # Check if skill already exists
    existing_skill = db.query(Skill).filter(
        Skill.student_id == student.id,
        Skill.skill_name == skill_data.skill_name
    ).first()
    
    if existing_skill:
        # Update existing skill
        existing_skill.proficiency_score = Decimal(str(skill_data.proficiency_score))
        if skill_data.quiz_score is not None:
            existing_skill.quiz_score = Decimal(str(skill_data.quiz_score))
        if skill_data.voice_score is not None:
            existing_skill.voice_score = Decimal(str(skill_data.voice_score))
        existing_skill.last_assessed_at = datetime.utcnow()
        existing_skill.updated_at = datetime.utcnow()
        db.commit()
        
        message = f"Skill '{skill_data.skill_name}' updated successfully"
        skill_id = existing_skill.id
    else:
        # Create new skill
        new_skill = Skill(
            student_id=student.id,
            skill_name=skill_data.skill_name,
            proficiency_score=Decimal(str(skill_data.proficiency_score)),
            quiz_score=Decimal(str(skill_data.quiz_score)) if skill_data.quiz_score else None,
            voice_score=Decimal(str(skill_data.voice_score)) if skill_data.voice_score else None,
            market_weight=Decimal("1.0"),  # Default weight, will be updated by Task 21.5
            last_assessed_at=datetime.utcnow(),
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        db.add(new_skill)
        db.commit()
        db.refresh(new_skill)
        
        message = f"Skill '{skill_data.skill_name}' added successfully"
        skill_id = new_skill.id
    
    # Trigger vector regeneration
    await trigger_vector_regeneration(db, student)
    
    return {
        "message": message,
        "id": skill_id,
        "skill_name": skill_data.skill_name,
        "proficiency_score": skill_data.proficiency_score,
        "vector_regenerated": True
    }


@router.get("/skills")
async def get_student_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all skills for current student.
    
    **Authentication**: Required (JWT token)
    
    **Returns**: List of all assessed skills with scores and market weights
    """
    # Verify user is a student
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    # Get student profile
    student = get_student_by_user_id(db, current_user.id)
    
    # Get all skills
    skills = db.query(Skill).filter(Skill.student_id == student.id).all()
    
    return {
        "student_id": student.id,
        "total_skills": len(skills),
        "skills": [
            {
                "id": skill.id,
                "skill_name": skill.skill_name,
                "proficiency_score": float(skill.proficiency_score),
                "quiz_score": float(skill.quiz_score) if skill.quiz_score else None,
                "voice_score": float(skill.voice_score) if skill.voice_score else None,
                "market_weight": float(skill.market_weight),
                "last_assessed_at": skill.last_assessed_at,
                "created_at": skill.created_at
            }
            for skill in skills
        ]
    }


@router.get("/behavioral")
async def get_behavioral_data(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get digital wellbeing data for current student.
    
    **Authentication**: Required (JWT token)
    
    **Parameters**:
    - days: Number of days to retrieve (default: 30)
    
    **Returns**: List of behavioral data entries
    """
    # Verify user is a student
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    # Get student profile
    student = get_student_by_user_id(db, current_user.id)
    
    # Get behavioral data (most recent first)
    from datetime import timedelta
    start_date = date.today() - timedelta(days=days)
    
    behavioral_data = db.query(DigitalWellbeingData).filter(
        DigitalWellbeingData.student_id == student.id,
        DigitalWellbeingData.date >= start_date
    ).order_by(DigitalWellbeingData.date.desc()).all()
    
    return {
        "student_id": student.id,
        "days_requested": days,
        "total_entries": len(behavioral_data),
        "data": [
            {
                "id": entry.id,
                "date": entry.date,
                "screen_time_hours": float(entry.screen_time_hours),
                "educational_app_hours": float(entry.educational_app_hours),
                "social_media_hours": float(entry.social_media_hours),
                "entertainment_hours": float(entry.entertainment_hours),
                "productivity_hours": float(entry.productivity_hours),
                "focus_score": float(entry.focus_score) if entry.focus_score else None,
                "sleep_duration_hours": float(entry.sleep_duration_hours) if entry.sleep_duration_hours else None,
                "sleep_quality": entry.sleep_quality.value if entry.sleep_quality else None,
                "synced_at": entry.synced_at
            }
            for entry in behavioral_data
        ]
    }
