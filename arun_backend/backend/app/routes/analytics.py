from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.db import get_db
from app.models import TrajectoryScore, Recommendation, GapAnalysis
from datetime import datetime

router = APIRouter(prefix="/analytics", tags=["analytics"])

class TrajectoryResponse(BaseModel):
    student_id: int
    score: float
    confidence_level: str
    calculated_at: datetime
    class Config: from_attributes = True

class RecommendationResponse(BaseModel):
    id: int
    student_id: int
    content: str
    impact_level: str
    estimated_score_gain: float
    completed: bool
    class Config: from_attributes = True

class GapAnalysisResponse(BaseModel):
    metric_name: str
    student_value: float
    alumni_average: float
    gap_percentage: float
    narrative: str
    class Config: from_attributes = True

class AnalyticsFetchRequest(BaseModel):
    student_id: int

@router.post("/fetch-trajectory", response_model=TrajectoryResponse)
def get_trajectory_score(request: AnalyticsFetchRequest, db: Session = Depends(get_db)):
    score = db.query(TrajectoryScore).filter(TrajectoryScore.student_id == request.student_id).order_by(TrajectoryScore.calculated_at.desc()).first()
    if not score:
        raise HTTPException(status_code=404, detail="No trajectory score found for this student")
    return score

@router.post("/fetch-recommendations", response_model=List[RecommendationResponse])
def get_recommendations(request: AnalyticsFetchRequest, db: Session = Depends(get_db)):
    return db.query(Recommendation).filter(Recommendation.student_id == request.student_id).all()

@router.post("/fetch-gap-analysis", response_model=List[GapAnalysisResponse])
def get_gap_analysis(request: AnalyticsFetchRequest, db: Session = Depends(get_db)):
    return db.query(GapAnalysis).filter(GapAnalysis.student_id == request.student_id).all()

@router.post("/generate-vector")
def trigger_vector_generation(request: AnalyticsFetchRequest, db: Session = Depends(get_db)):
    """Trigger the creation and storage of a student's semantic vector profile."""
    from app.services import vector_gen_service
    result = vector_gen_service.generate_and_store_student_vector(db, request.student_id)
    if "error" in result:
        raise HTTPException(status_code=404, detail=result["error"])
    return result
