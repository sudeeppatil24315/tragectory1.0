"""
Trajectory Score Calculation Service for Trajectory Engine MVP

This module implements trajectory score calculation using pure mathematics.
NO LLM is used for trajectory calculation - only weighted averaging and statistics.

Trajectory Score = Weighted average of similar alumni outcomes
- Range: 0-100 (employability score)
- 0-40: Low employability
- 41-70: Moderate employability  
- 71-100: High employability

Components:
1. Academic Score (25-40% depending on major)
2. Behavioral Score (30-50% depending on major)
3. Skills Score (30-40% depending on major)
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# MAJOR-SPECIFIC WEIGHTS
# ============================================================================

MAJOR_WEIGHTS = {
    'Computer Science': {
        'academic': 0.25,
        'behavioral': 0.35,
        'skills': 0.40
    },
    'Mechanical Engineering': {
        'academic': 0.40,
        'behavioral': 0.30,
        'skills': 0.30
    },
    'Business Administration': {
        'academic': 0.20,
        'behavioral': 0.50,
        'skills': 0.30
    },
    'Electrical Engineering': {
        'academic': 0.35,
        'behavioral': 0.30,
        'skills': 0.35
    },
    'Civil Engineering': {
        'academic': 0.40,
        'behavioral': 0.35,
        'skills': 0.25
    },
    'default': {
        'academic': 0.30,
        'behavioral': 0.40,
        'skills': 0.30
    }
}


# ============================================================================
# ALUMNI OUTCOME MAPPING
# ============================================================================

OUTCOME_SCORES = {
    'Tier1': (90, 100),  # FAANG, Top companies
    'Tier2': (65, 80),   # Mid-size, Product companies
    'Tier3': (50, 65),   # Service, Startups
    'Not Placed': (10, 30)
}


# ============================================================================
# COMPONENT SCORE CALCULATIONS (Task 8.1)
# ============================================================================

def calculate_academic_score(profile: Dict) -> float:
    """
    Calculate academic component score using FINAL-FORMULAS-COMPLETE.md
    
    Formula: 0.5×gpa_sigmoid + 0.25×attendance + 0.15×internal + 0.1×backlogs_inverse
    
    Args:
        profile: Student profile dict with keys:
            - gpa (float): 0-10 scale
            - attendance (float): 0-100 percentage
            - internal_marks (float): 0-100 (optional, default 75)
            - backlogs (int): Number of backlogs (optional, default 0)
    
    Returns:
        Academic score in [0, 1] range (NOT 0-100)
    """
    gpa = profile.get('gpa', 5.0)
    attendance = profile.get('attendance', 75.0)
    internal_marks = profile.get('internal_marks', 75.0)
    backlogs = profile.get('backlogs', 0)
    
    # Normalize GPA (0-10 scale)
    gpa_norm = (gpa - 0) / (10 - 0)
    
    # Apply sigmoid transform (midpoint=0.7, steepness=8)
    gpa_sigmoid = 1.0 / (1.0 + np.exp(-8.0 * (gpa_norm - 0.7)))
    
    # Normalize attendance (0-100 scale)
    attendance_norm = (attendance - 0) / (100 - 0)
    
    # Normalize internal marks (0-100 scale)
    internal_norm = (internal_marks - 0) / (100 - 0)
    
    # Inverse normalize backlogs (0-5 scale, lower is better)
    backlogs_inverse = 1.0 - ((backlogs - 0) / (5 - 0))
    backlogs_inverse = max(0.0, min(1.0, backlogs_inverse))
    
    # Calculate academic score (weights from FINAL-FORMULAS-COMPLETE.md)
    academic_score = (
        0.5 * gpa_sigmoid +
        0.25 * attendance_norm +
        0.15 * internal_norm +
        0.1 * backlogs_inverse
    )
    
    return float(np.clip(academic_score, 0.0, 1.0))


def calculate_grit(
    consistency: int,
    problem_solving: int,
    projects: int,
    study_hours: float
) -> float:
    """
    Calculate grit score using FINAL-FORMULAS-COMPLETE.md
    
    Formula: 0.3×consistency + 0.3×problem_solving + 0.2×projects + 0.2×study_hours
    
    Args:
        consistency: Consistency level 1-5
        problem_solving: Problem-solving skill 1-5
        projects: Number of projects (0-10+)
        study_hours: Study hours per day (0-8+)
    
    Returns:
        Grit score in [0, 1] range
    """
    # Normalize inputs
    consistency_norm = consistency / 5.0
    problem_solving_norm = problem_solving / 5.0
    projects_norm = min(projects / 10.0, 1.0)
    study_hours_norm = min(study_hours / 8.0, 1.0)
    
    # Calculate grit
    grit = (
        0.3 * consistency_norm +
        0.3 * problem_solving_norm +
        0.2 * projects_norm +
        0.2 * study_hours_norm
    )
    
    return float(np.clip(grit, 0.0, 1.0))


def calculate_behavioral_score(
    profile: Dict,
    wellbeing: Optional[List[Dict]] = None
) -> float:
    """
    Calculate behavioral component score using FINAL-FORMULAS-COMPLETE.md
    
    Formula: 0.2×study + 0.15×practice + 0.15×screen_inverse + 
             0.1×social_media_inverse + 0.15×distraction_inverse + 
             0.1×sleep_quality + 0.15×grit
    
    Args:
        profile: Student profile dict with keys:
            - study_hours_per_week (float): Hours per week (convert to daily)
            - practice_hours (float): Practice hours per day (optional, default 0)
            - project_count (int): Number of projects (for grit)
            - consistency (int): Consistency level 1-5 (for grit, optional default 3)
            - problem_solving (int): Problem-solving 1-5 (for grit, optional default 3)
        
        wellbeing: Optional list of digital wellbeing data dicts:
            - screen_time_hours (float)
            - social_media_hours (float)
            - distraction_level (int): 1-5 scale
            - sleep_duration_hours (float)
    
    Returns:
        Behavioral score in [0, 1] range (NOT 0-100)
    """
    # Study hours (convert weekly to daily, 0-8 hours/day)
    study_hours_weekly = profile.get('study_hours_per_week', 15.0)
    study_hours_daily = study_hours_weekly / 7.0
    study_norm = min(study_hours_daily / 8.0, 1.0)
    
    # Practice hours (0-6 hours/day)
    practice_hours = profile.get('practice_hours', 0.0)
    practice_norm = min(practice_hours / 6.0, 1.0)
    
    # Digital wellbeing metrics (if available)
    if wellbeing and len(wellbeing) > 0:
        recent = wellbeing[0]  # Most recent data
        
        # Screen time (inverse - lower is better, 0-12 hours)
        screen_time = recent.get('screen_time_hours', 6.0)
        screen_inverse = 1.0 - min(screen_time / 12.0, 1.0)
        
        # Social media (inverse - lower is better, 0-6 hours)
        social_media = recent.get('social_media_hours', 2.0)
        social_media_inverse = 1.0 - min(social_media / 6.0, 1.0)
        
        # Distraction level (inverse - lower is better, 1-5 scale)
        distraction = recent.get('distraction_level', 3)
        distraction_inverse = 1.0 - ((distraction - 1) / (5 - 1))
        
        # Sleep quality (optimal: 7-8 hours)
        sleep_hours = recent.get('sleep_duration_hours', 7.0)
        sleep_quality = 1.0 - abs(sleep_hours - 7.5) / 7.5
        sleep_quality = max(0.0, min(1.0, sleep_quality))
    else:
        # No wellbeing data - use neutral defaults
        screen_inverse = 0.5
        social_media_inverse = 0.5
        distraction_inverse = 0.5
        sleep_quality = 0.5
    
    # Calculate grit score
    consistency = profile.get('consistency', 3)
    problem_solving = profile.get('problem_solving', 3)
    projects = profile.get('project_count', 0)
    
    grit = calculate_grit(
        consistency=consistency,
        problem_solving=problem_solving,
        projects=projects,
        study_hours=study_hours_daily
    )
    
    # Calculate behavioral score (weights from FINAL-FORMULAS-COMPLETE.md)
    behavioral_score = (
        0.2 * study_norm +
        0.15 * practice_norm +
        0.15 * screen_inverse +
        0.1 * social_media_inverse +
        0.15 * distraction_inverse +
        0.1 * sleep_quality +
        0.15 * grit
    )
    
    return float(np.clip(behavioral_score, 0.0, 1.0))


def calculate_skill_score(
    profile: Dict,
    skills: Optional[List[Dict]] = None
) -> float:
    """
    Calculate skills component score using FINAL-FORMULAS-COMPLETE.md
    
    This function supports two modes:
    1. Market-weighted mode (when skills list provided with market_weight)
    2. Profile-based mode (when only profile provided)
    
    Market-weighted formula:
    weighted_skill = Σ(proficiency[i] × market_weight[i]) / Σ(market_weight[i])
    final = (base × 0.50) + (weighted × 0.50)
    
    Profile-based formula:
    0.15×languages + 0.15×problem_solving + 0.1×communication +
    0.1×teamwork + 0.15×projects + 0.2×deployment_bonus + 
    0.15×internship_bonus + 0.1×career_clarity
    
    Args:
        profile: Student profile dict with keys:
            - languages (str): Comma-separated list of languages
            - problem_solving (int): 1-5 scale
            - communication (int): 1-5 scale (optional, default 3)
            - teamwork (int): 1-5 scale (optional, default 3)
            - project_count (int): Number of projects
            - deployed (bool or str): Whether has deployed project
            - internship (bool or str): Whether has internship
            - career_clarity (int): 1-5 scale (optional, default 3)
        
        skills: Optional list of skill dicts with keys:
            - skill_name (str): Name of the skill
            - proficiency_score (float): 0-100 scale
            - market_weight (float): 0.5x, 1.0x, or 2.0x
            - If provided, will use market-weighted approach
    
    Returns:
        Skill score in [0, 1] range (NOT 0-100)
    """
    # Calculate base skill score from profile (always calculated)
    # Count programming languages
    languages_str = profile.get('languages', '')
    if languages_str:
        lang_count = len([l.strip() for l in languages_str.split(',') if l.strip()])
    else:
        lang_count = 0
    lang_norm = min(lang_count / 8.0, 1.0)  # Cap at 8 languages
    
    # Normalize problem-solving (1-5 scale)
    problem_solving = profile.get('problem_solving', 3)
    problem_solving_norm = (problem_solving - 1) / (5 - 1)
    
    # Normalize communication (1-5 scale)
    communication = profile.get('communication', 3)
    communication_norm = (communication - 1) / (5 - 1)
    
    # Normalize teamwork (1-5 scale)
    teamwork = profile.get('teamwork', 3)
    teamwork_norm = (teamwork - 1) / (5 - 1)
    
    # Normalize projects (0-10+)
    projects = profile.get('project_count', 0)
    projects_norm = min(projects / 10.0, 1.0)
    
    # Deployment bonus (0.2 if deployed, else 0)
    deployed = profile.get('deployed', False)
    if isinstance(deployed, str):
        deployed = deployed.lower() in ['yes', 'true', '1']
    deployment_bonus = 0.2 if deployed else 0.0
    
    # Internship bonus (0.15 if internship, else 0)
    internship = profile.get('internship', False)
    if isinstance(internship, str):
        internship = internship.lower() in ['yes', 'true', '1']
    internship_bonus = 0.15 if internship else 0.0
    
    # Normalize career clarity (1-5 scale)
    career_clarity = profile.get('career_clarity', 3)
    career_clarity_norm = (career_clarity - 1) / (5 - 1)
    
    # Calculate base skills score (weights from FINAL-FORMULAS-COMPLETE.md)
    base_skill_score = (
        0.15 * lang_norm +
        0.15 * problem_solving_norm +
        0.1 * communication_norm +
        0.1 * teamwork_norm +
        0.15 * projects_norm +
        deployment_bonus +
        internship_bonus +
        0.1 * career_clarity_norm
    )
    
    # If skills list provided with market weights, calculate weighted skill score
    if skills and len(skills) > 0:
        weighted_sum = 0.0
        weight_sum = 0.0
        
        for skill in skills:
            proficiency = skill.get('proficiency_score', 50.0)
            market_weight = skill.get('market_weight', 1.0)
            
            # Normalize proficiency from 0-100 to 0-1
            proficiency_norm = proficiency / 100.0
            
            weighted_sum += proficiency_norm * market_weight
            weight_sum += market_weight
        
        if weight_sum == 0:
            # No valid skills, return base score only
            logger.warning("No valid skills with weights, using base score only")
            return float(np.clip(base_skill_score, 0.0, 1.0))
        
        # Calculate weighted average
        weighted_skill_score = weighted_sum / weight_sum
        
        # Combine base score (50%) with weighted skill score (50%)
        # This ensures both profile-based and skill-based assessments matter
        final_skill_score = (base_skill_score * 0.50) + (weighted_skill_score * 0.50)
        
        logger.info(f"Skill score calculation: base={base_skill_score:.3f}, "
                   f"weighted={weighted_skill_score:.3f}, final={final_skill_score:.3f}")
        
        return float(np.clip(final_skill_score, 0.0, 1.0))
    
    # No skills list provided, return base score only
    return float(np.clip(base_skill_score, 0.0, 1.0))


def get_major_weights(major: str) -> Dict[str, float]:
    """
    Get component weights for a specific major.
    
    Args:
        major: Student's major (e.g., "Computer Science")
    
    Returns:
        Dict with keys: academic, behavioral, skills (weights sum to 1.0)
    """
    weights = MAJOR_WEIGHTS.get(major, MAJOR_WEIGHTS['default'])
    logger.info(f"Using weights for {major}: {weights}")
    return weights


# ============================================================================
# TRAJECTORY SCORE CALCULATION (Task 8.3)
# ============================================================================

def map_alumni_outcome_to_score(alumni: Dict) -> float:
    """
    Map alumni employment outcome to a score.
    
    Scoring:
    - Tier1 (FAANG, Top): 90-100 (average 95)
    - Tier2 (Mid-size, Product): 65-80 (average 72.5)
    - Tier3 (Service, Startup): 50-65 (average 57.5)
    - Not Placed: 10-30 (average 20)
    
    Args:
        alumni: Alumni dict with keys:
            - placement_status (str): "Placed" or "Not Placed"
            - company_tier (str): "Tier1", "Tier2", "Tier3"
            - outcome_score (float, optional): Pre-calculated score
    
    Returns:
        Outcome score in [0, 100] range
    """
    # If outcome_score already calculated, use it
    if 'outcome_score' in alumni and alumni['outcome_score'] > 0:
        return float(alumni['outcome_score'])
    
    placement_status = alumni.get('placement_status', 'Not Placed')
    company_tier = alumni.get('company_tier', '')
    
    if placement_status == 'Not Placed':
        return 20.0
    
    # Get score range for tier
    score_range = OUTCOME_SCORES.get(company_tier, OUTCOME_SCORES['Tier3'])
    
    # Return midpoint of range
    outcome_score = (score_range[0] + score_range[1]) / 2.0
    
    return float(outcome_score)


def calculate_trajectory_score(
    student_profile: Dict,
    similar_alumni: List[Dict],
    wellbeing: Optional[List[Dict]] = None,
    skills: Optional[List[Dict]] = None,
    student_id: Optional[int] = None,
    db_session = None
) -> Dict:
    """
    Calculate trajectory score using weighted averaging of similar alumni outcomes.
    
    Formula:
    1. Calculate component scores (academic, behavioral, skills) in [0, 1] range
    2. Apply major-specific weights
    3. Find similar alumni and their outcomes
    4. Calculate weighted average: Σ(similarity[i] × outcome[i]) / Σ(similarity[i])
    5. Apply interaction adjustments
    6. Convert to [0, 100] range
    7. Clamp to [0, 100]
    8. Calculate confidence and margin of error
    9. Calculate trend and velocity
    10. Predict employment tier
    
    Args:
        student_profile: Student profile dict
        similar_alumni: List of similar alumni with similarity scores
        wellbeing: Optional digital wellbeing data
        skills: Optional skills data
        student_id: Optional student ID (for trend calculation)
        db_session: Optional database session (for trend calculation)
    
    Returns:
        Dict with keys:
            - score (float): Trajectory score 0-100
            - academic_score (float): Academic component 0-100
            - behavioral_score (float): Behavioral component 0-100
            - skill_score (float): Skills component 0-100
            - component_weights (dict): Major-specific weights
            - similar_alumni_count (int): Number of matches
            - confidence (float): Confidence 0-1
            - margin_of_error (float): Margin of error 0-20
            - trend (str): "improving", "declining", or "stable"
            - velocity (float): Rate of change per week
            - predicted_tier (str): "Tier1", "Tier2", or "Tier3"
            - interpretation (str): Score meaning
    """
    # Calculate component scores (in 0-1 range)
    academic_score_01 = calculate_academic_score(student_profile)
    behavioral_score_01 = calculate_behavioral_score(student_profile, wellbeing)
    skill_score_01 = calculate_skill_score(student_profile, skills)
    
    # Convert to 0-100 for display
    academic_score = academic_score_01 * 100
    behavioral_score = behavioral_score_01 * 100
    skill_score = skill_score_01 * 100
    
    logger.info(f"Component scores - Academic: {academic_score:.1f}, "
                f"Behavioral: {behavioral_score:.1f}, Skills: {skill_score:.1f}")
    
    # Get major-specific weights
    major = student_profile.get('major', 'default')
    weights = get_major_weights(major)
    
    # If no similar alumni, return default score based on components
    if not similar_alumni or len(similar_alumni) == 0:
        logger.warning("No similar alumni found, using component-based score")
        
        # Calculate base score using 0-1 range components
        base_score_01 = (
            academic_score_01 * weights['academic'] +
            behavioral_score_01 * weights['behavioral'] +
            skill_score_01 * weights['skills']
        )
        
        # Convert to 0-100 range
        base_score = base_score_01 * 100
        
        # Calculate confidence (low due to no matches)
        confidence, margin_of_error = calculate_confidence(
            similar_alumni=[],
            student_profile=student_profile,
            wellbeing=wellbeing,
            skills=skills
        )
        
        # Calculate trend and velocity
        trend, velocity = calculate_trend_and_velocity(
            student_id=student_id or 0,
            current_score=base_score,
            db_session=db_session
        )
        
        # Predict tier
        predicted_tier = predict_tier(base_score)
        
        return {
            'score': float(np.clip(base_score, 0.0, 100.0)),
            'academic_score': academic_score,
            'behavioral_score': behavioral_score,
            'skill_score': skill_score,
            'component_weights': weights,
            'similar_alumni_count': 0,
            'confidence': confidence,
            'margin_of_error': margin_of_error,
            'trend': trend,
            'velocity': velocity,
            'predicted_tier': predicted_tier,
            'interpretation': interpret_score(base_score)
        }
    
    # Calculate weighted average of alumni outcomes
    weighted_sum = 0.0
    similarity_sum = 0.0
    
    for alumni in similar_alumni:
        similarity = alumni.get('similarity_score', 0.0)
        outcome_score = map_alumni_outcome_to_score(alumni)
        
        weighted_sum += similarity * outcome_score
        similarity_sum += similarity
    
    if similarity_sum == 0:
        logger.error("Similarity sum is zero, using default score")
        trajectory_score = 50.0
    else:
        trajectory_score = weighted_sum / similarity_sum
    
    # Apply interaction adjustments (works with 0-100 range)
    trajectory_score = apply_interaction_adjustments(
        trajectory_score,
        academic_score,
        behavioral_score,
        skill_score,
        wellbeing
    )
    
    # Clamp to [0, 100]
    trajectory_score = float(np.clip(trajectory_score, 0.0, 100.0))
    
    # Calculate confidence and margin of error
    confidence, margin_of_error = calculate_confidence(
        similar_alumni=similar_alumni,
        student_profile=student_profile,
        wellbeing=wellbeing,
        skills=skills
    )
    
    # Calculate trend and velocity
    trend, velocity = calculate_trend_and_velocity(
        student_id=student_id or 0,
        current_score=trajectory_score,
        db_session=db_session
    )
    
    # Predict tier
    predicted_tier = predict_tier(trajectory_score)
    
    logger.info(f"Final trajectory score: {trajectory_score:.1f} "
                f"(based on {len(similar_alumni)} similar alumni)")
    logger.info(f"Confidence: {confidence:.2f}, Margin: ±{margin_of_error:.1f}, "
                f"Trend: {trend}, Velocity: {velocity:.2f}, Tier: {predicted_tier}")
    
    return {
        'score': trajectory_score,
        'academic_score': academic_score,
        'behavioral_score': behavioral_score,
        'skill_score': skill_score,
        'component_weights': weights,
        'similar_alumni_count': len(similar_alumni),
        'confidence': confidence,
        'margin_of_error': margin_of_error,
        'trend': trend,
        'velocity': velocity,
        'predicted_tier': predicted_tier,
        'interpretation': interpret_score(trajectory_score)
    }


def apply_interaction_adjustments(
    base_score: float,
    academic_score: float,
    behavioral_score: float,
    skill_score: float,
    wellbeing: Optional[List[Dict]] = None
) -> float:
    """
    Apply interaction adjustments to trajectory score.
    
    Adjustments:
    - Burnout penalty: High academic + low sleep → -5 points
    - Distraction penalty: High screen time + low focus → -5 points
    - Grit bonus: High projects + consistent study → +5 points
    - Balance bonus: All components above 70 → +5 points
    
    Args:
        base_score: Base trajectory score
        academic_score: Academic component score
        behavioral_score: Behavioral component score
        skill_score: Skills component score
        wellbeing: Optional wellbeing data
    
    Returns:
        Adjusted score
    """
    adjusted_score = base_score
    
    # Burnout penalty
    if wellbeing and len(wellbeing) > 0:
        recent = wellbeing[0]
        sleep = recent.get('sleep_duration_hours', 7.0)
        
        if academic_score > 80 and sleep < 6.0:
            adjusted_score -= 5.0
            logger.info("Applied burnout penalty (-5): High academic + low sleep")
    
    # Distraction penalty
    if wellbeing and len(wellbeing) > 0:
        recent = wellbeing[0]
        screen_time = recent.get('screen_time_hours', 6.0)
        productive = recent.get('educational_app_hours', 0) + recent.get('productivity_hours', 0)
        distracting = recent.get('social_media_hours', 0) + recent.get('entertainment_hours', 0)
        
        if screen_time > 8.0 and distracting > productive:
            adjusted_score -= 5.0
            logger.info("Applied distraction penalty (-5): High screen time + low focus")
    
    # Grit bonus (high effort + consistency)
    if behavioral_score > 75:
        adjusted_score += 5.0
        logger.info("Applied grit bonus (+5): High behavioral score")
    
    # Balance bonus (well-rounded student)
    if academic_score > 70 and behavioral_score > 70 and skill_score > 70:
        adjusted_score += 5.0
        logger.info("Applied balance bonus (+5): All components above 70")
    
    return adjusted_score


def interpret_score(score: float) -> str:
    """
    Interpret trajectory score into human-readable text.
    
    Args:
        score: Trajectory score 0-100
    
    Returns:
        Interpretation string
    """
    if score >= 71:
        return "High employability - Strong placement likelihood, top-tier companies (FAANG, product companies)"
    elif score >= 41:
        return "Moderate employability - Average placement likelihood, mid-tier companies"
    else:
        return "Low employability - At-risk, needs significant improvement in academics, behavior, or skills"


# ============================================================================
# CONFIDENCE AND TREND CALCULATION (Task 9)
# ============================================================================

def calculate_confidence(
    similar_alumni: List[Dict],
    student_profile: Dict,
    wellbeing: Optional[List[Dict]] = None,
    skills: Optional[List[Dict]] = None
) -> Tuple[float, float]:
    """
    Calculate confidence score and margin of error for trajectory prediction.
    
    Confidence is based on 4 factors:
    1. Number of matches (more matches = higher confidence)
    2. Similarity consistency (similar scores = higher confidence)
    3. Outcome variance (similar outcomes = higher confidence)
    4. Data completeness (more data = higher confidence)
    
    Formula:
    confidence = average([num_matches_factor, similarity_factor, outcome_factor, data_factor])
    margin_of_error = (1 - confidence) × 20
    
    Args:
        similar_alumni: List of similar alumni with similarity scores
        student_profile: Student profile dict
        wellbeing: Optional wellbeing data
        skills: Optional skills data
    
    Returns:
        Tuple of (confidence, margin_of_error)
        - confidence: 0-1 scale (0 = no confidence, 1 = complete confidence)
        - margin_of_error: 0-20 scale (lower is better)
    
    Examples:
        >>> alumni = [{'similarity_score': 0.95, 'outcome_score': 90}, ...]
        >>> confidence, margin = calculate_confidence(alumni, profile)
        >>> confidence
        0.85
        >>> margin
        3.0
    """
    # Factor 1: Number of matches
    num_matches = len(similar_alumni)
    if num_matches >= 10:
        num_matches_factor = 1.0
    elif num_matches >= 5:
        num_matches_factor = 0.7
    else:
        num_matches_factor = 0.4
    
    logger.info(f"Confidence Factor 1 - Num matches: {num_matches} → {num_matches_factor:.2f}")
    
    # Factor 2: Similarity consistency (low std dev = high confidence)
    if num_matches > 0:
        similarity_scores = [a.get('similarity_score', 0.0) for a in similar_alumni]
        similarity_std = float(np.std(similarity_scores))
        
        if similarity_std < 0.1:
            similarity_factor = 1.0
        elif similarity_std < 0.2:
            similarity_factor = 0.7
        else:
            similarity_factor = 0.4
        
        logger.info(f"Confidence Factor 2 - Similarity std: {similarity_std:.3f} → {similarity_factor:.2f}")
    else:
        similarity_factor = 0.4
        logger.info("Confidence Factor 2 - No matches → 0.40")
    
    # Factor 3: Outcome variance (low std dev = high confidence)
    if num_matches > 0:
        outcome_scores = [map_alumni_outcome_to_score(a) for a in similar_alumni]
        outcome_std = float(np.std(outcome_scores))
        
        if outcome_std < 10:
            outcome_factor = 1.0
        elif outcome_std < 20:
            outcome_factor = 0.7
        else:
            outcome_factor = 0.4
        
        logger.info(f"Confidence Factor 3 - Outcome std: {outcome_std:.1f} → {outcome_factor:.2f}")
    else:
        outcome_factor = 0.4
        logger.info("Confidence Factor 3 - No matches → 0.40")
    
    # Factor 4: Data completeness
    required_fields = ['gpa', 'attendance', 'study_hours_per_week', 'project_count']
    complete_fields = sum(1 for field in required_fields if student_profile.get(field) is not None)
    
    # Add wellbeing data completeness
    if wellbeing and len(wellbeing) > 0:
        complete_fields += 1
    
    # Add skills data completeness
    if skills and len(skills) > 0:
        complete_fields += 1
    
    total_fields = len(required_fields) + 2  # +2 for wellbeing and skills
    data_factor = complete_fields / total_fields
    
    logger.info(f"Confidence Factor 4 - Data completeness: {complete_fields}/{total_fields} → {data_factor:.2f}")
    
    # Calculate overall confidence (average of all factors)
    confidence = float(np.mean([
        num_matches_factor,
        similarity_factor,
        outcome_factor,
        data_factor
    ]))
    
    # Calculate margin of error
    margin_of_error = (1.0 - confidence) * 20.0
    
    logger.info(f"Final Confidence: {confidence:.2f}, Margin of Error: ±{margin_of_error:.1f}")
    
    return confidence, margin_of_error


def calculate_trend_and_velocity(
    student_id: int,
    current_score: float,
    db_session = None
) -> Tuple[str, float]:
    """
    Calculate trend and velocity from historical trajectory scores.
    
    Trend indicates whether the student is improving, declining, or stable.
    Velocity measures the rate of change per week.
    
    Formula:
    recent_avg = average(last 3 scores)
    previous_avg = average(previous 3 scores)
    velocity = (recent_avg - previous_avg) / 3 per week
    
    Trend:
    - "improving" if velocity > 1
    - "declining" if velocity < -1
    - "stable" otherwise
    
    Args:
        student_id: Student ID
        current_score: Current trajectory score
        db_session: Optional database session (for fetching historical scores)
    
    Returns:
        Tuple of (trend, velocity)
        - trend: "improving", "declining", or "stable"
        - velocity: Rate of change per week (can be negative)
    
    Examples:
        >>> trend, velocity = calculate_trend_and_velocity(123, 75.0)
        >>> trend
        "improving"
        >>> velocity
        1.67
    """
    # If no database session, return default values
    if db_session is None:
        logger.warning("No database session provided, returning default trend")
        return "stable", 0.0
    
    # TODO: Fetch historical scores from database
    # For now, return default values
    # This will be implemented when we have the database connection
    
    logger.info("Trend calculation not yet implemented (requires database)")
    return "stable", 0.0


def predict_tier(score: float) -> str:
    """
    Predict employment tier based on trajectory score.
    
    Tier mapping:
    - 71-100: Tier1 (FAANG, top companies)
    - 41-70: Tier2 (mid-size, product companies)
    - 0-40: Tier3 (service, startups, at-risk)
    
    Args:
        score: Trajectory score 0-100
    
    Returns:
        Predicted tier: "Tier1", "Tier2", or "Tier3"
    """
    if score >= 71:
        return "Tier1"
    elif score >= 41:
        return "Tier2"
    else:
        return "Tier3"


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def calculate_component_contribution(
    academic_score: float,
    behavioral_score: float,
    skill_score: float,
    weights: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate how much each component contributes to final score.
    
    Args:
        academic_score: Academic component score (0-100)
        behavioral_score: Behavioral component score (0-100)
        skill_score: Skills component score (0-100)
        weights: Major-specific weights
    
    Returns:
        Dict with contribution of each component (0-100 scale)
    """
    return {
        'academic_contribution': academic_score * weights['academic'],
        'behavioral_contribution': behavioral_score * weights['behavioral'],
        'skill_contribution': skill_score * weights['skills']
    }


def validate_trajectory_result(result: Dict) -> bool:
    """
    Validate trajectory calculation result.
    
    Args:
        result: Trajectory result dict
    
    Returns:
        True if valid, False otherwise
    """
    if 'score' not in result:
        logger.error("Missing 'score' in result")
        return False
    
    score = result['score']
    if not (0 <= score <= 100):
        logger.error(f"Score out of range: {score}")
        return False
    
    if not np.isfinite(score):
        logger.error(f"Score is not finite: {score}")
        return False
    
    return True
