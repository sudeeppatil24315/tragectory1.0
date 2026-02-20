"""
Skill Assessment Routes - Task 21

Implements quiz-based and voice-based skill assessments with market demand weighting.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from decimal import Decimal

from app.db import get_db
from app.auth import get_current_user
from app.models import User, Student, Skill
from app.services.voice_evaluation_service import get_voice_evaluation_service
from app.services.skill_demand_service import get_skill_demand_service
from app.services.vector_generation import generate_student_vector
from app.services.qdrant_service import QdrantService

router = APIRouter(prefix="/api/skills", tags=["skills"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class QuizQuestion(BaseModel):
    """Single quiz question."""
    question: str
    answer: int = Field(..., ge=1, le=5, description="Answer on 1-5 scale (Beginner to Expert)")


class QuizSubmission(BaseModel):
    """Quiz submission for a skill."""
    skill_name: str = Field(..., min_length=1, max_length=100)
    questions: List[QuizQuestion] = Field(..., min_items=1, max_items=20)
    
    @validator('questions')
    def validate_questions(cls, v):
        if len(v) < 10:
            raise ValueError('Quiz must have at least 10 questions')
        return v


class VoiceEvalSubmission(BaseModel):
    """Voice evaluation submission (text-based MVP)."""
    skill_name: str = Field(..., min_length=1, max_length=100)
    question: str = Field(..., min_length=10)
    answer: str = Field(..., min_length=20)


class SkillResponse(BaseModel):
    """Skill assessment response."""
    id: int
    skill_name: str
    proficiency_score: float
    quiz_score: Optional[float]
    voice_score: Optional[float]
    market_weight: float
    market_weight_reasoning: Optional[str]
    demand_level: str
    last_assessed_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class QuizResultResponse(BaseModel):
    """Quiz result response."""
    skill_name: str
    quiz_score: float
    questions_count: int
    message: str


class VoiceEvalResultResponse(BaseModel):
    """Voice evaluation result response."""
    skill_name: str
    voice_score: float
    overall_score: float
    dimensions: dict
    feedback: str
    message: str


class CombinedSkillScoreResponse(BaseModel):
    """Combined skill score response."""
    skill_name: str
    quiz_score: Optional[float]
    voice_score: Optional[float]
    proficiency_score: float
    market_weight: float
    demand_level: str
    weighted_score: float
    message: str


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def require_student(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Student:
    """Ensure current user is a student."""
    if current_user.role != "student":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only students can access this endpoint"
        )
    
    student = db.query(Student).filter(Student.user_id == current_user.id).first()
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student profile not found"
        )
    
    return student


def calculate_quiz_score(questions: List[QuizQuestion]) -> float:
    """
    Calculate quiz score from answers.
    Formula: (Σ scores / (N × 5)) × 100
    """
    total_score = sum(q.answer for q in questions)
    max_score = len(questions) * 5
    return round((total_score / max_score) * 100, 2)


def calculate_combined_score(quiz_score: Optional[float], voice_score: Optional[float]) -> float:
    """
    Calculate combined skill score.
    Formula: (quiz_score × 0.60) + (voice_score × 0.40)
    """
    if quiz_score is not None and voice_score is not None:
        return round((quiz_score * 0.60) + (voice_score * 0.40), 2)
    elif quiz_score is not None:
        return quiz_score
    elif voice_score is not None:
        return voice_score
    else:
        return 0.0


async def trigger_vector_regeneration(student: Student, db: Session):
    """Trigger vector regeneration after skill update."""
    try:
        # Generate new vector
        vector = generate_student_vector(student, db)
        
        # Initialize Qdrant service
        qdrant = QdrantService()
        
        # Update in Qdrant
        if qdrant.is_available:
            success = qdrant.update_student_vector(student.id, vector)
            if not success:
                print(f"Failed to update vector for student {student.id}")
    except Exception as e:
        # Log error but don't fail the request
        print(f"Vector regeneration failed: {str(e)}")


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/quiz", response_model=QuizResultResponse, status_code=status.HTTP_200_OK)
async def submit_quiz(
    submission: QuizSubmission,
    student: Student = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Submit quiz answers for skill assessment.
    
    - Scores each question on 1-5 scale (Beginner to Expert)
    - Calculates overall quiz_score = (Σ scores / (N × 5)) × 100
    - Stores quiz_score in skills table
    - Updates proficiency_score if voice_score exists
    """
    # Calculate quiz score
    quiz_score = calculate_quiz_score(submission.questions)
    
    # Find or create skill record
    skill = db.query(Skill).filter(
        Skill.student_id == student.id,
        Skill.skill_name == submission.skill_name
    ).first()
    
    if skill:
        # Update existing skill
        skill.quiz_score = Decimal(str(quiz_score))
        skill.last_assessed_at = datetime.utcnow()
        
        # Recalculate proficiency score
        skill.proficiency_score = Decimal(str(calculate_combined_score(
            quiz_score,
            float(skill.voice_score) if skill.voice_score else None
        )))
    else:
        # Create new skill
        skill = Skill(
            student_id=student.id,
            skill_name=submission.skill_name,
            quiz_score=Decimal(str(quiz_score)),
            proficiency_score=Decimal(str(quiz_score)),  # Only quiz for now
            last_assessed_at=datetime.utcnow()
        )
        db.add(skill)
    
    db.commit()
    db.refresh(skill)
    
    # Trigger vector regeneration (async)
    await trigger_vector_regeneration(student, db)
    
    return QuizResultResponse(
        skill_name=submission.skill_name,
        quiz_score=quiz_score,
        questions_count=len(submission.questions),
        message=f"Quiz completed successfully. Score: {quiz_score}/100"
    )


@router.post("/voice-eval", response_model=VoiceEvalResultResponse, status_code=status.HTTP_200_OK)
async def submit_voice_evaluation(
    submission: VoiceEvalSubmission,
    student: Student = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Submit voice evaluation (text-based MVP).
    
    - Uses LLM to evaluate technical answer
    - Scores on 4 dimensions (0-10 each): technical accuracy, clarity, depth, completeness
    - Calculates overall_score = (sum of dimensions) × 2.5 to get 0-100 scale
    - Stores voice_score in skills table
    - Updates proficiency_score: (quiz_score × 0.60) + (voice_score × 0.40)
    """
    # Evaluate answer using LLM
    voice_service = get_voice_evaluation_service()
    evaluation = voice_service.evaluate_response(
        question=submission.question,
        answer=submission.answer,
        skill=submission.skill_name
    )
    
    voice_score = evaluation['overall_score']
    
    # Find or create skill record
    skill = db.query(Skill).filter(
        Skill.student_id == student.id,
        Skill.skill_name == submission.skill_name
    ).first()
    
    if skill:
        # Update existing skill
        skill.voice_score = Decimal(str(voice_score))
        skill.last_assessed_at = datetime.utcnow()
        
        # Recalculate proficiency score
        skill.proficiency_score = Decimal(str(calculate_combined_score(
            float(skill.quiz_score) if skill.quiz_score else None,
            voice_score
        )))
    else:
        # Create new skill
        skill = Skill(
            student_id=student.id,
            skill_name=submission.skill_name,
            voice_score=Decimal(str(voice_score)),
            proficiency_score=Decimal(str(voice_score)),  # Only voice for now
            last_assessed_at=datetime.utcnow()
        )
        db.add(skill)
    
    db.commit()
    db.refresh(skill)
    
    # Trigger vector regeneration (async)
    await trigger_vector_regeneration(student, db)
    
    return VoiceEvalResultResponse(
        skill_name=submission.skill_name,
        voice_score=voice_score,
        overall_score=voice_score,
        dimensions=evaluation['dimensions'],
        feedback=evaluation['feedback'],
        message=f"Voice evaluation completed. Score: {voice_score}/100"
    )


@router.post("/analyze-demand/{skill_name}", response_model=CombinedSkillScoreResponse, status_code=status.HTTP_200_OK)
async def analyze_skill_demand(
    skill_name: str,
    student: Student = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Analyze skill market demand and update weighting.
    
    - Calls LLM skill demand analysis service
    - Assigns market_weight: 0.5x (Low), 1.0x (Medium), 2.0x (High)
    - Stores market_weight and reasoning in skills table
    - Calculates weighted_score for trajectory calculation
    """
    # Find skill record
    skill = db.query(Skill).filter(
        Skill.student_id == student.id,
        Skill.skill_name == skill_name
    ).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill '{skill_name}' not found. Please complete quiz or voice evaluation first."
        )
    
    # Analyze market demand
    demand_service = get_skill_demand_service()
    demand_analysis = demand_service.analyze_skill_demand(
        skill=skill_name,
        major=student.major,
        year=2026
    )
    
    # Update skill with market demand data
    skill.market_weight = Decimal(str(demand_analysis['market_weight']))
    skill.market_weight_reasoning = demand_analysis['reasoning']
    
    db.commit()
    db.refresh(skill)
    
    # Calculate weighted score (for display)
    proficiency = float(skill.proficiency_score)
    market_weight = float(skill.market_weight)
    weighted_score = proficiency * market_weight
    
    # Trigger vector regeneration (async)
    await trigger_vector_regeneration(student, db)
    
    return CombinedSkillScoreResponse(
        skill_name=skill_name,
        quiz_score=float(skill.quiz_score) if skill.quiz_score else None,
        voice_score=float(skill.voice_score) if skill.voice_score else None,
        proficiency_score=proficiency,
        market_weight=market_weight,
        demand_level=demand_analysis['demand_level'],
        weighted_score=round(weighted_score, 2),
        message=f"Market demand analyzed. {demand_analysis['demand_level']} demand ({market_weight}x weight)"
    )


@router.get("/", response_model=List[SkillResponse], status_code=status.HTTP_200_OK)
async def get_student_skills(
    student: Student = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Get all skills for current student.
    
    Returns list of skills with scores, market weights, and demand levels.
    """
    skills = db.query(Skill).filter(Skill.student_id == student.id).all()
    
    # Convert to response format
    response = []
    for skill in skills:
        demand_level = {0.5: 'Low', 1.0: 'Medium', 2.0: 'High'}.get(
            float(skill.market_weight) if skill.market_weight else 1.0,
            'Medium'
        )
        
        response.append(SkillResponse(
            id=skill.id,
            skill_name=skill.skill_name,
            proficiency_score=float(skill.proficiency_score),
            quiz_score=float(skill.quiz_score) if skill.quiz_score else None,
            voice_score=float(skill.voice_score) if skill.voice_score else None,
            market_weight=float(skill.market_weight) if skill.market_weight else 1.0,
            market_weight_reasoning=skill.market_weight_reasoning,
            demand_level=demand_level,
            last_assessed_at=skill.last_assessed_at
        ))
    
    return response


@router.get("/{skill_name}", response_model=SkillResponse, status_code=status.HTTP_200_OK)
async def get_skill_details(
    skill_name: str,
    student: Student = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Get details for a specific skill.
    """
    skill = db.query(Skill).filter(
        Skill.student_id == student.id,
        Skill.skill_name == skill_name
    ).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill '{skill_name}' not found"
        )
    
    demand_level = {0.5: 'Low', 1.0: 'Medium', 2.0: 'High'}.get(
        float(skill.market_weight) if skill.market_weight else 1.0,
        'Medium'
    )
    
    return SkillResponse(
        id=skill.id,
        skill_name=skill.skill_name,
        proficiency_score=float(skill.proficiency_score),
        quiz_score=float(skill.quiz_score) if skill.quiz_score else None,
        voice_score=float(skill.voice_score) if skill.voice_score else None,
        market_weight=float(skill.market_weight) if skill.market_weight else 1.0,
        market_weight_reasoning=skill.market_weight_reasoning,
        demand_level=demand_level,
        last_assessed_at=skill.last_assessed_at
    )


@router.delete("/{skill_name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_skill(
    skill_name: str,
    student: Student = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Delete a skill assessment.
    """
    skill = db.query(Skill).filter(
        Skill.student_id == student.id,
        Skill.skill_name == skill_name
    ).first()
    
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill '{skill_name}' not found"
        )
    
    db.delete(skill)
    db.commit()
    
    # Trigger vector regeneration (async)
    await trigger_vector_regeneration(student, db)
    
    return None
