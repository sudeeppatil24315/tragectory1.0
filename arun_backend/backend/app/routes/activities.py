"""
STEP 3: API Routes for Student Activities (Schedule, To-Do, Planner)

This file contains all the endpoints students will use to:
1. Add/view/complete scheduled events
2. Add/view/complete to-do items
3. Create/view day plans

Each endpoint is explained with comments.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import date, time, datetime

from app.db import get_db
from app.models import StudentActivity

router = APIRouter(prefix="/activities", tags=["activities"])

# ===== PYDANTIC MODELS (Request/Response Schemas) =====

class ActivityCreate(BaseModel):
    """
    Schema for creating a new activity
    Used when student adds a schedule/todo/plan item
    """
    date: date  # Which day (e.g., 2026-02-17)
    title: str  # Activity name (e.g., "Study DSA")
    description: Optional[str] = None  # Optional details
    activity_type: str  # "schedule" | "todo" | "plan"
    category: Optional[str] = None  # "study" | "class" | "personal"
    start_time: Optional[time] = None  # For schedule/plan
    end_time: Optional[time] = None  # For schedule/plan
    duration_minutes: Optional[int] = None  # Optional
    priority: int = 2  # 1=high, 2=medium, 3=low

class ActivityResponse(BaseModel):
    """
    Schema for returning activity data
    """
    id: int
    student_id: int
    date: date
    title: str
    description: Optional[str]
    activity_type: str
    category: Optional[str]
    start_time: Optional[time]
    end_time: Optional[time]
    is_completed: bool
    priority: int
    created_at: datetime
    
    class Config:
        from_attributes = True  # Allows conversion from SQLAlchemy model

class ActivityUpdate(BaseModel):
    """
    Schema for updating an activity (e.g., marking as complete)
    """
    is_completed: Optional[bool] = None
    title: Optional[str] = None
    start_time: Optional[time] = None
    end_time: Optional[time] = None

class ActivityFetchRequest(BaseModel):
    """
    Schema for fetching activities via POST
    """
    student_id: int
    activity_date: Optional[date] = None
    activity_type: Optional[str] = None

class TodayScheduleRequest(BaseModel):
    """
    Schema for fetching today's schedule
    """
    student_id: int

class PendingTodosRequest(BaseModel):
    """
    Schema for fetching pending todos
    """
    student_id: int

# ===== API ENDPOINTS =====

@router.post("/", response_model=ActivityResponse)
def create_activity(
    activity: ActivityCreate,
    student_id: int,  # In real app, get from JWT token
    db: Session = Depends(get_db)
):
    """
    CREATE: Add a new activity (schedule/todo/plan)
    
    Example usage:
    POST /activities?student_id=1
    {
        "date": "2026-02-17",
        "title": "Study Data Structures",
        "activity_type": "schedule",
        "start_time": "09:00",
        "end_time": "11:00",
        "category": "study",
        "priority": 1
    }
    """
    db_activity = StudentActivity(
        student_id=student_id,
        **activity.model_dump()
    )
    db.add(db_activity)
    db.commit()
    db.refresh(db_activity)
    return db_activity

@router.post("/fetch", response_model=List[ActivityResponse])
def get_activities(
    request: ActivityFetchRequest,
    db: Session = Depends(get_db)
):
    """
    READ: Get activities with optional filters (POST method)
    
    Example usage:
    POST /activities/fetch
    {
        "student_id": 1,
        "activity_date": "2026-02-17",
        "activity_type": "schedule"
    }
    """
    query = db.query(StudentActivity).filter(StudentActivity.student_id == request.student_id)
    
    if request.activity_date:
        query = query.filter(StudentActivity.date == request.activity_date)
    
    if request.activity_type:
        query = query.filter(StudentActivity.activity_type == request.activity_type)
    
    return query.order_by(StudentActivity.date, StudentActivity.start_time).all()

@router.patch("/{activity_id}", response_model=ActivityResponse)
def update_activity(
    activity_id: int,
    updates: ActivityUpdate,
    db: Session = Depends(get_db)
):
    """
    UPDATE: Modify an activity (e.g., mark as complete)
    
    Example:
    PATCH /activities/123
    {
        "is_completed": true
    }
    """
    activity = db.query(StudentActivity).filter(StudentActivity.id == activity_id).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Update only provided fields
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(activity, field, value)
    
    # If marking as complete, record timestamp
    if updates.is_completed:
        activity.completed_at = datetime.utcnow()
    
    db.commit()
    db.refresh(activity)
    return activity

@router.delete("/{activity_id}")
def delete_activity(
    activity_id: int,
    db: Session = Depends(get_db)
):
    """
    DELETE: Remove an activity
    
    Example:
    DELETE /activities/123
    """
    activity = db.query(StudentActivity).filter(StudentActivity.id == activity_id).first()
    
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    db.delete(activity)
    db.commit()
    return {"message": "Activity deleted successfully"}

# ===== CONVENIENCE ENDPOINTS =====

@router.post("/schedule/today", response_model=List[ActivityResponse])
def get_today_schedule(
    request: TodayScheduleRequest,
    db: Session = Depends(get_db)
):
    """
    Quick endpoint to get today's schedule (POST method)
    
    Example:
    POST /activities/schedule/today
    {
        "student_id": 1
    }
    """
    today = date.today()
    return db.query(StudentActivity).filter(
        StudentActivity.student_id == request.student_id,
        StudentActivity.date == today,
        StudentActivity.activity_type == "schedule"
    ).order_by(StudentActivity.start_time).all()

@router.post("/todos/pending", response_model=List[ActivityResponse])
def get_pending_todos(
    request: PendingTodosRequest,
    db: Session = Depends(get_db)
):
    """
    Quick endpoint to get all incomplete todos (POST method)
    
    Example:
    POST /activities/todos/pending
    {
        "student_id": 1
    }
    """
    return db.query(StudentActivity).filter(
        StudentActivity.student_id == request.student_id,
        StudentActivity.activity_type == "todo",
        StudentActivity.is_completed == False
    ).order_by(StudentActivity.priority, StudentActivity.date).all()
