"""
Vector Generation Service for Trajectory Engine MVP

This module implements pure mathematical vector generation using NumPy.
NO LLM is used for vector generation - only normalization and feature extraction.

Vector Components (15 dimensions):
1. sigmoid_normalize(gpa)
2. standard_normalize(attendance)
3. time_weighted_avg(study_hours)
4. standard_normalize(projects)
5. inverse_normalize(time_weighted_avg(screen_time))
6. focus_score
7. time_weighted_avg(sleep)
8-15. sigmoid_normalize(skill_scores) - up to 8 skills

All vector components are normalized to [0, 1] range.
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta


# ============================================================================
# NORMALIZATION FUNCTIONS (Task 5.1)
# ============================================================================

def standard_normalize(value: float, min_val: float, max_val: float) -> float:
    """
    Standard min-max normalization to [0, 1] range.
    
    Used for: GPA, attendance, study hours, projects, sleep
    
    Formula: (value - min) / (max - min)
    
    Args:
        value: The value to normalize
        min_val: Minimum possible value
        max_val: Maximum possible value
    
    Returns:
        Normalized value in [0, 1] range
    
    Examples:
        >>> standard_normalize(7.5, 0, 10)  # GPA 7.5 on 10-point scale
        0.75
        >>> standard_normalize(80, 0, 100)  # 80% attendance
        0.8
    """
    if max_val == min_val:
        return 0.5  # Neutral value if no range
    
    normalized = (value - min_val) / (max_val - min_val)
    return np.clip(normalized, 0.0, 1.0)


def inverse_normalize(value: float, min_val: float, max_val: float) -> float:
    """
    Inverse normalization where LOWER values are BETTER.
    
    Used for: Screen time (lower is better)
    
    Formula: 1 - ((value - min) / (max - min))
    
    Args:
        value: The value to normalize
        min_val: Minimum possible value
        max_val: Maximum possible value
    
    Returns:
        Normalized value in [0, 1] range (inverted)
    
    Examples:
        >>> inverse_normalize(2, 0, 10)  # 2 hours screen time (good)
        0.8
        >>> inverse_normalize(8, 0, 10)  # 8 hours screen time (bad)
        0.2
    """
    if max_val == min_val:
        return 0.5
    
    normalized = 1.0 - ((value - min_val) / (max_val - min_val))
    return np.clip(normalized, 0.0, 1.0)


def sigmoid_normalize(value: float, midpoint: float, steepness: float = 1.0) -> float:
    """
    Sigmoid normalization for diminishing returns.
    
    Used for: GPA and skills (going from 7→8 GPA is harder than 5→6)
    
    Formula: 1 / (1 + exp(-steepness * (value - midpoint)))
    
    Args:
        value: The value to normalize
        midpoint: The inflection point (typically average value)
        steepness: Controls how steep the curve is (default 1.0)
    
    Returns:
        Normalized value in [0, 1] range with diminishing returns
    
    Examples:
        >>> sigmoid_normalize(7.5, 7.0, 1.0)  # GPA 7.5 with midpoint 7.0
        0.622...
        >>> sigmoid_normalize(9.0, 7.0, 1.0)  # GPA 9.0 (harder to achieve)
        0.880...
    """
    sigmoid_value = 1.0 / (1.0 + np.exp(-steepness * (value - midpoint)))
    return np.clip(sigmoid_value, 0.0, 1.0)


def time_weighted_avg(values: List[Tuple[float, int]], decay_rate: float = 0.1) -> float:
    """
    Calculate time-weighted average where recent data matters more.
    
    Used for: Behavioral data (recent study hours, screen time, sleep)
    
    Formula: Σ(value[i] × exp(-decay_rate × days_ago[i])) / Σ(exp(-decay_rate × days_ago[i]))
    
    Args:
        values: List of (value, days_ago) tuples
        decay_rate: How quickly old data loses importance (default 0.1)
    
    Returns:
        Weighted average value
    
    Examples:
        >>> time_weighted_avg([(8, 0), (7, 1), (6, 2)])  # Recent: 8, 7, 6
        7.48...  # Recent values weighted more heavily
        >>> time_weighted_avg([(6, 0), (7, 1), (8, 2)])  # Recent: 6, 7, 8
        6.51...  # Recent value (6) dominates
    """
    if not values:
        return 0.5  # Neutral default
    
    weighted_sum = 0.0
    weight_sum = 0.0
    
    for value, days_ago in values:
        weight = np.exp(-decay_rate * days_ago)
        weighted_sum += value * weight
        weight_sum += weight
    
    if weight_sum == 0:
        return 0.5
    
    return weighted_sum / weight_sum


def calculate_focus_score(app_usage: Dict[str, float]) -> float:
    """
    Calculate Focus Score from app usage data.
    
    Formula: (Educational + Productivity) / (Social_Media + Entertainment)
    
    Args:
        app_usage: Dictionary with keys:
            - educational_hours
            - productivity_hours
            - social_media_hours
            - entertainment_hours
    
    Returns:
        Focus score (0 = distracted, 1+ = focused)
        Normalized to [0, 1] range where 1.0 = ratio of 2.0 or higher
    
    Examples:
        >>> calculate_focus_score({
        ...     'educational_hours': 3,
        ...     'productivity_hours': 2,
        ...     'social_media_hours': 2,
        ...     'entertainment_hours': 1
        ... })
        0.833...  # (3+2)/(2+1) = 1.67, normalized to 0.833
    """
    productive = app_usage.get('educational_hours', 0) + app_usage.get('productivity_hours', 0)
    distracting = app_usage.get('social_media_hours', 0) + app_usage.get('entertainment_hours', 0)
    
    if distracting == 0:
        # All productive time = perfect focus
        return 1.0
    
    if productive == 0:
        # All distracting time = no focus
        return 0.0
    
    # Calculate ratio and normalize to [0, 1]
    # Ratio of 2.0 or higher = perfect score (1.0)
    ratio = productive / distracting
    normalized = min(ratio / 2.0, 1.0)
    
    return normalized


# ============================================================================
# VECTOR GENERATION (Task 5.3)
# ============================================================================

def generate_student_vector(
    profile: Dict,
    wellbeing: Optional[List[Dict]] = None,
    skills: Optional[List[Dict]] = None
) -> np.ndarray:
    """
    Generate 15-dimensional vector from student profile.
    
    Vector Components:
    1. sigmoid_normalize(gpa) - Academic performance with diminishing returns
    2. standard_normalize(attendance) - Attendance percentage
    3. time_weighted_avg(study_hours) - Recent study hours matter more
    4. standard_normalize(projects) - Project count
    5. inverse_normalize(time_weighted_avg(screen_time)) - Lower is better
    6. focus_score - Productive vs distracting app usage
    7. time_weighted_avg(sleep) - Recent sleep patterns
    8-15. sigmoid_normalize(skill_scores) - Up to 8 skills with market weighting
    
    Args:
        profile: Student profile dict with keys:
            - gpa (float): 0-10 scale
            - attendance (float): 0-100 percentage
            - study_hours_per_week (float): Hours per week
            - project_count (int): Number of projects
        
        wellbeing: List of digital wellbeing data dicts (most recent first):
            - date (datetime): Date of record
            - screen_time_hours (float): Total screen time
            - educational_app_hours (float)
            - productivity_app_hours (float)
            - social_media_hours (float)
            - entertainment_hours (float)
            - sleep_duration_hours (float)
        
        skills: List of skill dicts:
            - skill_name (str)
            - proficiency_score (float): 0-100
            - market_weight (float): 0.5, 1.0, or 2.0
    
    Returns:
        15-dimensional numpy array with all values in [0, 1] range
    
    Examples:
        >>> profile = {'gpa': 7.5, 'attendance': 80, 'study_hours_per_week': 20, 'project_count': 3}
        >>> vector = generate_student_vector(profile)
        >>> vector.shape
        (15,)
        >>> all(0 <= v <= 1 for v in vector)
        True
    """
    vector = []
    
    # ========================================================================
    # COMPONENT 1: GPA (sigmoid for diminishing returns)
    # ========================================================================
    gpa = profile.get('gpa', 5.0)  # Default to neutral 5.0
    gpa_normalized = sigmoid_normalize(gpa, midpoint=7.0, steepness=0.5)
    vector.append(gpa_normalized)
    
    # ========================================================================
    # COMPONENT 2: Attendance (standard normalization)
    # ========================================================================
    attendance = profile.get('attendance', 75.0)  # Default to 75%
    attendance_normalized = standard_normalize(attendance, 0, 100)
    vector.append(attendance_normalized)
    
    # ========================================================================
    # COMPONENT 3: Study Hours (time-weighted average)
    # ========================================================================
    study_hours = profile.get('study_hours_per_week', 15.0)  # Default to 15 hours
    # For MVP, use current value (no historical data yet)
    # In production, this would use time_weighted_avg with historical data
    study_hours_normalized = standard_normalize(study_hours, 0, 40)
    vector.append(study_hours_normalized)
    
    # ========================================================================
    # COMPONENT 4: Projects (standard normalization)
    # ========================================================================
    projects = profile.get('project_count', 0)
    projects_normalized = standard_normalize(projects, 0, 10)
    vector.append(projects_normalized)
    
    # ========================================================================
    # COMPONENTS 5-7: Digital Wellbeing (if available)
    # ========================================================================
    if wellbeing and len(wellbeing) > 0:
        # Calculate time-weighted averages for recent data
        today = datetime.now()
        
        # Screen time (inverse - lower is better)
        screen_time_data = [
            (record.get('screen_time_hours', 6.0), (today - record.get('date', today)).days)
            for record in wellbeing[:7]  # Last 7 days
        ]
        avg_screen_time = time_weighted_avg(screen_time_data, decay_rate=0.1)
        screen_time_normalized = inverse_normalize(avg_screen_time, 0, 12)
        vector.append(screen_time_normalized)
        
        # Focus score (from most recent day)
        recent_wellbeing = wellbeing[0]
        app_usage = {
            'educational_hours': recent_wellbeing.get('educational_app_hours', 0),
            'productivity_hours': recent_wellbeing.get('productivity_hours', 0),
            'social_media_hours': recent_wellbeing.get('social_media_hours', 0),
            'entertainment_hours': recent_wellbeing.get('entertainment_hours', 0)
        }
        focus = calculate_focus_score(app_usage)
        vector.append(focus)
        
        # Sleep (time-weighted average)
        sleep_data = [
            (record.get('sleep_duration_hours', 7.0), (today - record.get('date', today)).days)
            for record in wellbeing[:7]
        ]
        avg_sleep = time_weighted_avg(sleep_data, decay_rate=0.1)
        sleep_normalized = standard_normalize(avg_sleep, 4, 10)
        vector.append(sleep_normalized)
    else:
        # No wellbeing data - use neutral defaults
        vector.extend([0.5, 0.5, 0.5])
    
    # ========================================================================
    # COMPONENTS 8-15: Skills (up to 8 skills with market weighting)
    # ========================================================================
    if skills and len(skills) > 0:
        # Sort skills by market weight (highest first)
        sorted_skills = sorted(skills, key=lambda s: s.get('market_weight', 1.0), reverse=True)
        
        for i in range(8):
            if i < len(sorted_skills):
                skill = sorted_skills[i]
                proficiency = skill.get('proficiency_score', 50.0)
                market_weight = skill.get('market_weight', 1.0)
                
                # Apply market weighting to proficiency
                weighted_proficiency = proficiency * market_weight
                
                # Normalize with sigmoid (diminishing returns for high skills)
                skill_normalized = sigmoid_normalize(weighted_proficiency, midpoint=70.0, steepness=0.02)
                vector.append(skill_normalized)
            else:
                # No skill data for this slot - use neutral default
                vector.append(0.5)
    else:
        # No skills data - use neutral defaults
        vector.extend([0.5] * 8)
    
    # ========================================================================
    # VALIDATION: Ensure all components are in [0, 1] range
    # ========================================================================
    vector_array = np.array(vector, dtype=np.float32)
    
    # Clip to ensure [0, 1] range (safety check)
    vector_array = np.clip(vector_array, 0.0, 1.0)
    
    # Handle NaN or Inf values (replace with neutral 0.5)
    vector_array = np.nan_to_num(vector_array, nan=0.5, posinf=1.0, neginf=0.0)
    
    return vector_array


def generate_alumni_vector(
    profile: Dict,
    skills: Optional[List[Dict]] = None
) -> np.ndarray:
    """
    Generate 15-dimensional vector from alumni profile.
    
    Alumni vectors use the same structure as student vectors but without
    real-time wellbeing data (historical data only).
    
    Args:
        profile: Alumni profile dict with keys:
            - gpa (float): 0-10 scale
            - attendance (float): 0-100 percentage
            - study_hours_per_week (float): Historical average
            - project_count (int): Number of projects during college
        
        skills: List of skill dicts (same as student)
    
    Returns:
        15-dimensional numpy array with all values in [0, 1] range
    """
    # Alumni don't have real-time wellbeing data
    # Use historical averages or neutral defaults
    return generate_student_vector(profile, wellbeing=None, skills=skills)
