"""
Prediction API Endpoint for Trajectory Engine MVP

This module implements the trajectory prediction endpoint that:
1. Fetches student profile and wellbeing data
2. Generates student vector
3. Finds similar alumni using Qdrant
4. Calculates trajectory score with confidence and trend
5. Returns comprehensive prediction results

NO LLM is used for trajectory calculation - only pure mathematics.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional
from pydantic import BaseModel
import logging

from app.db import get_db
from app.auth import get_current_user
from app.models import User, Student, DigitalWellbeingData, Skill
from app.services.vector_generation import generate_student_vector
from app.services.qdrant_service import QdrantService
from app.services.similarity_service import find_similar_alumni
from app.services.trajectory_service import calculate_trajectory_score

# Configure logging
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api", tags=["prediction"])

# Initialize Qdrant service
qdrant = QdrantService(host="localhost", port=6333)


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class PredictionRequest(BaseModel):
    """Request model for trajectory prediction"""
    student_id: Optional[int] = None  # If None, use current user's student profile
    
    class Config:
        json_schema_extra = {
            "example": {
                "student_id": 123
            }
        }


class ComponentScores(BaseModel):
    """Component scores breakdown"""
    academic: float
    behavioral: float
    skills: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "academic": 72.4,
                "behavioral": 48.0,
                "skills": 52.6
            }
        }


class ComponentWeights(BaseModel):
    """Major-specific component weights"""
    academic: float
    behavioral: float
    skills: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "academic": 0.25,
                "behavioral": 0.35,
                "skills": 0.40
            }
        }


class SimilarAlumni(BaseModel):
    """Similar alumni information"""
    alumni_id: int
    similarity_score: float
    company_tier: str
    outcome_score: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "alumni_id": 1,
                "similarity_score": 0.95,
                "company_tier": "Tier1",
                "outcome_score": 95.0
            }
        }


class TrajectoryPrediction(BaseModel):
    """Complete trajectory prediction response"""
    # Core scores
    trajectory_score: float
    component_scores: ComponentScores
    component_weights: ComponentWeights
    
    # Confidence metrics
    confidence: float
    margin_of_error: float
    
    # Trend analysis
    trend: str
    velocity: float
    
    # Prediction
    predicted_tier: str
    interpretation: str
    
    # Similar alumni
    similar_alumni_count: int
    similar_alumni: list[SimilarAlumni]
    
    class Config:
        json_schema_extra = {
            "example": {
                "trajectory_score": 75.7,
                "component_scores": {
                    "academic": 72.4,
                    "behavioral": 48.0,
                    "skills": 52.6
                },
                "component_weights": {
                    "academic": 0.25,
                    "behavioral": 0.35,
                    "skills": 0.40
                },
                "confidence": 0.77,
                "margin_of_error": 4.5,
                "trend": "stable",
                "velocity": 0.0,
                "predicted_tier": "Tier1",
                "interpretation": "High employability - Strong placement likelihood",
                "similar_alumni_count": 3,
                "similar_alumni": [
                    {
                        "alumni_id": 1,
                        "similarity_score": 0.95,
                        "company_tier": "Tier1",
                        "outcome_score": 95.0
                    }
                ]
            }
        }


# ============================================================================
# PREDICTION ENDPOINT
# ============================================================================

@router.post("/predict", response_model=TrajectoryPrediction)
async def predict_trajectory(
    request: PredictionRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Calculate trajectory score for a student.
    
    This endpoint:
    1. Fetches student profile and wellbeing data from database
    2. Generates student vector
    3. Finds similar alumni using Qdrant
    4. Calculates trajectory score with confidence and trend
    5. Returns comprehensive prediction results
    
    **Authentication:** Required (JWT token)
    
    **Permissions:**
    - Students can only predict their own trajectory
    - Admins can predict any student's trajectory
    
    **Returns:**
    - trajectory_score: 0-100 (employability score)
    - component_scores: Academic, behavioral, skills breakdown
    - confidence: 0-1 (prediction confidence)
    - margin_of_error: 0-20 (uncertainty range)
    - trend: "improving", "declining", or "stable"
    - predicted_tier: "Tier1", "Tier2", or "Tier3"
    - similar_alumni: Top 5 most similar alumni
    
    **Example:**
    ```json
    {
        "student_id": 123
    }
    ```
    """
    try:
        # Determine which student to predict for
        if request.student_id is None:
            # Use current user's student profile
            student = db.query(Student).filter(
                Student.user_id == current_user.id
            ).first()
            
            if not student:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Student profile not found for current user"
                )
            
            student_id = student.id
        else:
            # Use specified student_id
            student_id = request.student_id
            
            # Check permissions (only admin can predict for other students)
            if current_user.role != "admin":
                # Verify this is the current user's student profile
                student = db.query(Student).filter(
                    Student.id == student_id,
                    Student.user_id == current_user.id
                ).first()
                
                if not student:
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="You can only predict your own trajectory"
                    )
            else:
                # Admin can predict for any student
                student = db.query(Student).filter(
                    Student.id == student_id
                ).first()
                
                if not student:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"Student with id {student_id} not found"
                    )
        
        logger.info(f"Predicting trajectory for student {student_id}")
        
        # Helper function to safely convert to float
        def safe_float(value, default=0.0):
            """Safely convert value to float, handling None and Decimal"""
            if value is None:
                return default
            try:
                return float(value)
            except (TypeError, ValueError):
                return default
        
        def safe_int(value, default=0):
            """Safely convert value to int, handling None"""
            if value is None:
                return default
            try:
                return int(value)
            except (TypeError, ValueError):
                return default
        
        # Fetch student profile data (convert Decimal to float, handle None)
        student_profile = {
            'gpa': safe_float(student.gpa, 5.0),
            'attendance': safe_float(student.attendance, 75.0),
            'internal_marks': safe_float(getattr(student, 'internal_marks', None), 75.0),
            'backlogs': safe_int(getattr(student, 'backlogs', None), 0),
            'study_hours_per_week': safe_float(student.study_hours_per_week, 15.0),
            'practice_hours': safe_float(getattr(student, 'practice_hours', None), 0.0),
            'project_count': safe_int(student.project_count, 0),
            'consistency': safe_float(getattr(student, 'consistency', None), 3.0),
            'problem_solving': safe_float(getattr(student, 'problem_solving', None), 3.0),
            'languages': str(getattr(student, 'languages', '') or ''),
            'communication': safe_float(getattr(student, 'communication', None), 3.0),
            'teamwork': safe_float(getattr(student, 'teamwork', None), 3.0),
            'deployed': bool(getattr(student, 'deployed', False)),
            'internship': bool(getattr(student, 'internship', False)),
            'career_clarity': safe_float(getattr(student, 'career_clarity', None), 3.0),
            'major': str(student.major) if student.major else 'default'
        }
        
        # Fetch digital wellbeing data (most recent 30 days)
        wellbeing_records = db.query(DigitalWellbeingData).filter(
            DigitalWellbeingData.student_id == student_id
        ).order_by(DigitalWellbeingData.date.desc()).limit(30).all()
        
        wellbeing = []
        if wellbeing_records:
            for record in wellbeing_records:
                wellbeing.append({
                    'screen_time_hours': safe_float(record.screen_time_hours, 6.0),
                    'social_media_hours': safe_float(record.social_media_hours, 2.0),
                    'distraction_level': safe_float(getattr(record, 'distraction_level', None), 3.0),
                    'sleep_duration_hours': safe_float(record.sleep_duration_hours, 7.0)
                })
        
        # Fetch skills data
        skills_records = db.query(Skill).filter(
            Skill.student_id == student_id
        ).all()
        
        skills = []
        if skills_records:
            for skill in skills_records:
                skills.append({
                    'skill_name': str(skill.skill_name),
                    'proficiency_score': safe_float(skill.proficiency_score, 50.0),
                    'market_weight': safe_float(skill.market_weight, 1.0)
                })
        
        # Generate student vector
        logger.info("Generating student vector")
        student_vector = generate_student_vector(student_profile, wellbeing)
        
        # Check if Qdrant is available
        if not qdrant.is_available:
            logger.warning("Qdrant not available, using default score")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Vector database unavailable. Please try again later."
            )
        
        # Find similar alumni
        logger.info("Finding similar alumni")
        similar_alumni = find_similar_alumni(
            student_vector=student_vector,
            qdrant_service=qdrant,
            major=student_profile['major'],
            top_k=5
        )
        
        # Calculate trajectory score
        logger.info("Calculating trajectory score")
        result = calculate_trajectory_score(
            student_profile=student_profile,
            similar_alumni=similar_alumni,
            wellbeing=wellbeing if wellbeing else None,
            skills=skills if skills else None,
            student_id=student_id,
            db_session=db
        )
        
        # Format similar alumni for response
        similar_alumni_list = []
        for alumni in similar_alumni[:5]:  # Top 5
            similar_alumni_list.append(SimilarAlumni(
                alumni_id=alumni.get('alumni_id', 0),
                similarity_score=alumni.get('similarity_score', 0.0),
                company_tier=alumni.get('company_tier', 'Unknown'),
                outcome_score=alumni.get('outcome_score', 0.0)
            ))
        
        # Build response
        response = TrajectoryPrediction(
            trajectory_score=result['score'],
            component_scores=ComponentScores(
                academic=result['academic_score'],
                behavioral=result['behavioral_score'],
                skills=result['skill_score']
            ),
            component_weights=ComponentWeights(
                academic=result['component_weights']['academic'],
                behavioral=result['component_weights']['behavioral'],
                skills=result['component_weights']['skills']
            ),
            confidence=result['confidence'],
            margin_of_error=result['margin_of_error'],
            trend=result['trend'],
            velocity=result['velocity'],
            predicted_tier=result['predicted_tier'],
            interpretation=result['interpretation'],
            similar_alumni_count=result['similar_alumni_count'],
            similar_alumni=similar_alumni_list
        )
        
        logger.info(f"Prediction complete: score={result['score']:.1f}, "
                   f"confidence={result['confidence']:.2f}, tier={result['predicted_tier']}")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error predicting trajectory: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate trajectory: {str(e)}"
        )


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@router.get("/predict/health")
async def prediction_health():
    """
    Check if prediction service is healthy.
    
    Returns:
    - status: "healthy" or "degraded"
    - qdrant_available: Boolean
    - message: Status message
    """
    qdrant_available = qdrant.is_available
    
    if qdrant_available:
        return {
            "status": "healthy",
            "qdrant_available": True,
            "message": "Prediction service is fully operational"
        }
    else:
        return {
            "status": "degraded",
            "qdrant_available": False,
            "message": "Vector database unavailable - predictions may be limited"
        }
