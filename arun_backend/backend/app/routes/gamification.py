from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.db import get_db
from app.models import Badge, StudentBadge
from datetime import datetime

router = APIRouter(prefix="/gamification", tags=["gamification"])

class BadgeResponse(BaseModel):
    id: int
    name: str
    description: str
    class Config: from_attributes = True

class StudentBadgeResponse(BaseModel):
    badge_id: int
    earned_at: datetime
    class Config: from_attributes = True

class GamificationFetchRequest(BaseModel):
    student_id: int

@router.post("/fetch-badges", response_model=List[BadgeResponse])
def get_all_badges(db: Session = Depends(get_db)):
    return db.query(Badge).all()

@router.post("/fetch-student-badges", response_model=List[StudentBadgeResponse])
def get_student_badges(request: GamificationFetchRequest, db: Session = Depends(get_db)):
    return db.query(StudentBadge).filter(StudentBadge.student_id == request.student_id).all()
