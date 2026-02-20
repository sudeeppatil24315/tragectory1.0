from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.db import get_db
from app.models import BehavioralMetric, DigitalWellbeingData as DigitalWellbeingDailyModel, DailyLog
from datetime import date, datetime

router = APIRouter(prefix="/metrics", tags=["metrics"])

class BehavioralMetricSchema(BaseModel):
    study_hours_per_week: float
    project_count: int
    skill_score: float
    class Config: from_attributes = True

class DigitalWellbeingDaily(BaseModel):
    date: date
    total_screen_time: float
    educational_time: float
    social_time: float
    entertainment_time: float
    productivity_time: float
    communication_time: float
    sleep_hours: float
    sleep_schedule: str
    use_phone_while_studying: bool
    distraction_level: float
    mental_exhaustion: bool
    focus_score: float
    class Config: from_attributes = True

class DailyLogSchema(BaseModel):
    date: date
    activity_description: str
    mood_score: float
    focus_hours: float
    class Config: from_attributes = True

class SkillAssessmentSchema(BaseModel):
    quiz_score: float
    voice_score: float
    final_score: float
    created_at: datetime
    class Config: from_attributes = True

class MetricFetchRequest(BaseModel):
    student_id: int

@router.post("/fetch-behavioral", response_model=BehavioralMetricSchema)
def get_behavioral_metrics(request: MetricFetchRequest, db: Session = Depends(get_db)):
    return db.query(BehavioralMetric).filter(BehavioralMetric.student_id == request.student_id).first()

@router.post("/fetch-wellbeing", response_model=List[DigitalWellbeingDaily])
def get_wellbeing_data(request: MetricFetchRequest, db: Session = Depends(get_db)):
    return db.query(DigitalWellbeingDailyModel).filter(DigitalWellbeingDailyModel.student_id == request.student_id).order_by(DigitalWellbeingDailyModel.date.desc()).all()

@router.post("/wellbeing/sync", response_model=DigitalWellbeingDaily)
def sync_wellbeing(data: DigitalWellbeingDaily, student_id: int, db: Session = Depends(get_db)):
    db_wellbeing = DigitalWellbeingDailyModel(
        student_id=student_id,
        date=data.date,
        total_screen_time=data.total_screen_time,
        educational_time=data.educational_time,
        social_time=data.social_time,
        entertainment_time=data.entertainment_time,
        productivity_time=data.productivity_time,
        communication_time=data.communication_time,
        sleep_hours=data.sleep_hours,
        sleep_schedule=data.sleep_schedule,
        use_phone_while_studying=data.use_phone_while_studying,
        distraction_level=data.distraction_level,
        mental_exhaustion=data.mental_exhaustion,
        focus_score=data.focus_score
    )
    db.add(db_wellbeing)
    db.commit()
    db.refresh(db_wellbeing)
    return db_wellbeing

@router.post("/fetch-skills", response_model=List[SkillAssessmentSchema])
def get_skill_assessments(request: MetricFetchRequest, db: Session = Depends(get_db)):
    from app.models import SkillAssessment
    return db.query(SkillAssessment).filter(SkillAssessment.student_id == request.student_id).order_by(SkillAssessment.created_at.desc()).all()

@router.post("/logs/add", response_model=DailyLogSchema)
def add_daily_log(data: DailyLogSchema, student_id: int, db: Session = Depends(get_db)):
    """Add a new daily activity log."""
    db_log = DailyLog(
        student_id=student_id,
        date=data.date,
        activity_description=data.activity_description,
        mood_score=data.mood_score,
        focus_hours=data.focus_hours
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log

@router.post("/logs/fetch", response_model=List[DailyLogSchema])
def get_daily_logs(request: MetricFetchRequest, db: Session = Depends(get_db)):
    """Fetch all activity logs for a specific student."""
    return db.query(DailyLog).filter(DailyLog.student_id == request.student_id).order_by(DailyLog.date.desc()).all()
