"""
Behavioral Analysis Routes - Task 22

Provides endpoints for behavioral pattern analysis and at-risk detection.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Dict, Any, Optional

from app.db import get_db
from app.auth import get_current_user
from app.models import User, Student
from app.services.behavioral_analysis_service import get_behavioral_analysis_service

router = APIRouter(prefix="/api/behavioral", tags=["behavioral"])


# ============================================================================
# RESPONSE MODELS
# ============================================================================

class CorrelationResponse(BaseModel):
    """Correlation analysis response."""
    screen_time_vs_gpa: float
    focus_score_vs_trajectory: float
    sleep_vs_academic: float
    sample_size: int
    optimal_ranges: Dict[str, Dict[str, float]]
    interpretation: Dict[str, str]


class AtRiskFlag(BaseModel):
    """At-risk pattern flag."""
    flag: str
    severity: str
    description: str
    metric_value: Optional[float] = None
    threshold: Optional[float] = None
    metrics: Optional[Dict[str, float]] = None
    thresholds: Optional[Dict[str, float]] = None


class AtRiskResponse(BaseModel):
    """At-risk patterns response."""
    student_id: int
    flags: List[AtRiskFlag]
    risk_level: str
    message: str


class ComparisonMetric(BaseModel):
    """Comparison metric."""
    student: float
    optimal: float
    status: str


class ComparisonResponse(BaseModel):
    """Comparison to successful alumni response."""
    student_id: int
    screen_time: ComparisonMetric
    focus_score: ComparisonMetric
    sleep: ComparisonMetric
    overall_status: str
    message: str


class InsightsResponse(BaseModel):
    """Complete behavioral insights response."""
    correlations: CorrelationResponse
    at_risk_flags: List[AtRiskFlag]
    comparison: Dict[str, ComparisonMetric]
    recommendations: List[str]


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


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Ensure current user is an admin."""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


def interpret_correlations(correlations: Dict[str, Any]) -> Dict[str, str]:
    """Interpret correlation values."""
    interpretations = {}
    
    # Screen time vs GPA
    st_gpa = correlations['screen_time_vs_gpa']
    if st_gpa < -0.4:
        interpretations['screen_time_vs_gpa'] = "Strong negative correlation: Higher screen time associated with lower GPA"
    elif st_gpa < -0.2:
        interpretations['screen_time_vs_gpa'] = "Moderate negative correlation: Screen time may impact GPA"
    else:
        interpretations['screen_time_vs_gpa'] = "Weak correlation: Screen time has minimal impact on GPA"
    
    # Focus score vs trajectory
    fs_traj = correlations['focus_score_vs_trajectory']
    if fs_traj > 0.5:
        interpretations['focus_score_vs_trajectory'] = "Strong positive correlation: Higher focus score strongly predicts better employability"
    elif fs_traj > 0.3:
        interpretations['focus_score_vs_trajectory'] = "Moderate positive correlation: Focus score impacts employability"
    else:
        interpretations['focus_score_vs_trajectory'] = "Weak correlation: Focus score has minimal impact"
    
    # Sleep vs academic
    sleep_acad = correlations['sleep_vs_academic']
    if sleep_acad > 0.3:
        interpretations['sleep_vs_academic'] = "Positive correlation: Better sleep associated with higher GPA"
    elif sleep_acad > 0.1:
        interpretations['sleep_vs_academic'] = "Weak positive correlation: Sleep may impact academic performance"
    else:
        interpretations['sleep_vs_academic'] = "Minimal correlation: Sleep has limited impact on GPA"
    
    return interpretations


def calculate_risk_level(flags: List[Dict[str, Any]]) -> str:
    """Calculate overall risk level from flags."""
    if not flags:
        return "low"
    
    high_severity_count = sum(1 for f in flags if f.get('severity') == 'high')
    
    if high_severity_count >= 2:
        return "high"
    elif high_severity_count == 1 or len(flags) >= 3:
        return "medium"
    else:
        return "low"


def calculate_overall_status(comparison: Dict[str, Any]) -> str:
    """Calculate overall status from comparison."""
    statuses = [m['status'] for m in comparison.values()]
    
    good_count = statuses.count('good')
    poor_count = statuses.count('poor')
    
    if good_count >= 2:
        return "good"
    elif poor_count >= 2:
        return "poor"
    else:
        return "fair"


def generate_recommendations(
    at_risk_flags: List[Dict[str, Any]],
    comparison: Dict[str, Any]
) -> List[str]:
    """Generate behavioral recommendations."""
    recommendations = []
    
    # Check at-risk flags
    for flag in at_risk_flags:
        if flag['flag'] == 'excessive_screen_time':
            recommendations.append("Reduce screen time to under 8 hours/day. Use app blockers during study hours.")
        elif flag['flag'] == 'low_focus_score':
            recommendations.append("Increase educational app usage and reduce social media. Aim for focus score > 0.5.")
        elif flag['flag'] == 'insufficient_sleep':
            recommendations.append("Prioritize sleep: aim for 7-8 hours/night. Set consistent bedtime and wake time.")
        elif flag['flag'] == 'at_risk_pattern':
            recommendations.append("URGENT: Multiple risk factors detected. Reduce social media, improve sleep, and seek academic support.")
    
    # Check comparison
    if comparison.get('screen_time', {}).get('status') == 'poor':
        recommendations.append("Your screen time is above optimal range. Successful alumni average 5 hours/day.")
    
    if comparison.get('focus_score', {}).get('status') == 'poor':
        recommendations.append("Your focus score is below optimal. Increase time on educational apps and productivity tools.")
    
    if comparison.get('sleep', {}).get('status') == 'poor':
        recommendations.append("Your sleep duration is below optimal. Successful alumni average 7.5 hours/night.")
    
    if not recommendations:
        recommendations.append("Great job! Your behavioral patterns are healthy. Keep maintaining good habits.")
    
    return recommendations


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.get("/correlations", response_model=CorrelationResponse, status_code=status.HTTP_200_OK)
async def get_correlations(
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Get behavioral correlations (Admin only).
    
    Calculates:
    - Screen time vs GPA correlation
    - Focus score vs trajectory score correlation
    - Sleep duration vs academic performance correlation
    - Optimal ranges for each metric
    """
    service = get_behavioral_analysis_service()
    correlations = service.calculate_correlations(db)
    interpretations = interpret_correlations(correlations)
    
    return CorrelationResponse(
        screen_time_vs_gpa=correlations['screen_time_vs_gpa'],
        focus_score_vs_trajectory=correlations['focus_score_vs_trajectory'],
        sleep_vs_academic=correlations['sleep_vs_academic'],
        sample_size=correlations['sample_size'],
        optimal_ranges=correlations['optimal_ranges'],
        interpretation=interpretations
    )


@router.get("/at-risk", response_model=AtRiskResponse, status_code=status.HTTP_200_OK)
async def get_at_risk_patterns(
    student: Student = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Get at-risk behavioral patterns for current student.
    
    Identifies:
    - High social media + low sleep + declining GPA
    - Excessive screen time (>8 hours/day)
    - Low focus score (<0.5)
    - Insufficient sleep (<6 hours)
    """
    service = get_behavioral_analysis_service()
    flags = service.identify_at_risk_patterns(student, db)
    risk_level = calculate_risk_level(flags)
    
    # Convert to response format
    flag_responses = [
        AtRiskFlag(
            flag=f['flag'],
            severity=f['severity'],
            description=f['description'],
            metric_value=f.get('metric_value'),
            threshold=f.get('threshold'),
            metrics=f.get('metrics'),
            thresholds=f.get('thresholds')
        )
        for f in flags
    ]
    
    message = {
        'low': "No significant risk factors detected. Keep up the good work!",
        'medium': "Some concerning patterns detected. Review recommendations below.",
        'high': "ALERT: Multiple high-risk patterns detected. Immediate action recommended."
    }[risk_level]
    
    return AtRiskResponse(
        student_id=student.id,
        flags=flag_responses,
        risk_level=risk_level,
        message=message
    )


@router.get("/comparison", response_model=ComparisonResponse, status_code=status.HTTP_200_OK)
async def get_comparison_to_alumni(
    student: Student = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Compare student's behavioral patterns to successful alumni.
    
    Returns comparison for:
    - Screen time
    - Focus score
    - Sleep duration
    """
    service = get_behavioral_analysis_service()
    
    # Get correlations to get optimal ranges
    correlations = service.calculate_correlations(db)
    optimal_ranges = correlations['optimal_ranges']
    
    # Get comparison
    comparison = service.compare_to_successful_alumni(student, db, optimal_ranges)
    
    if not comparison:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No behavioral data found for student"
        )
    
    overall_status = calculate_overall_status(comparison)
    
    message = {
        'good': "Your behavioral patterns align well with successful alumni!",
        'fair': "Your patterns are average. Some improvements recommended.",
        'poor': "Your patterns differ significantly from successful alumni. Review recommendations."
    }[overall_status]
    
    return ComparisonResponse(
        student_id=student.id,
        screen_time=ComparisonMetric(**comparison['screen_time']),
        focus_score=ComparisonMetric(**comparison['focus_score']),
        sleep=ComparisonMetric(**comparison['sleep']),
        overall_status=overall_status,
        message=message
    )


@router.get("/insights", response_model=InsightsResponse, status_code=status.HTTP_200_OK)
async def get_behavioral_insights(
    student: Student = Depends(require_student),
    db: Session = Depends(get_db)
):
    """
    Get complete behavioral insights for current student.
    
    Combines:
    - Correlations
    - At-risk patterns
    - Comparison to successful alumni
    - Personalized recommendations
    """
    service = get_behavioral_analysis_service()
    
    # Get correlations
    correlations_data = service.calculate_correlations(db)
    interpretations = interpret_correlations(correlations_data)
    
    correlations = CorrelationResponse(
        screen_time_vs_gpa=correlations_data['screen_time_vs_gpa'],
        focus_score_vs_trajectory=correlations_data['focus_score_vs_trajectory'],
        sleep_vs_academic=correlations_data['sleep_vs_academic'],
        sample_size=correlations_data['sample_size'],
        optimal_ranges=correlations_data['optimal_ranges'],
        interpretation=interpretations
    )
    
    # Get at-risk patterns
    at_risk_flags = service.identify_at_risk_patterns(student, db)
    
    # Get comparison
    comparison = service.compare_to_successful_alumni(
        student,
        db,
        correlations_data['optimal_ranges']
    )
    
    # Generate recommendations
    recommendations = generate_recommendations(at_risk_flags, comparison)
    
    return InsightsResponse(
        correlations=correlations,
        at_risk_flags=[
            AtRiskFlag(
                flag=f['flag'],
                severity=f['severity'],
                description=f['description'],
                metric_value=f.get('metric_value'),
                threshold=f.get('threshold'),
                metrics=f.get('metrics'),
                thresholds=f.get('thresholds')
            )
            for f in at_risk_flags
        ],
        comparison={
            k: ComparisonMetric(**v) for k, v in comparison.items()
        } if comparison else {},
        recommendations=recommendations
    )
