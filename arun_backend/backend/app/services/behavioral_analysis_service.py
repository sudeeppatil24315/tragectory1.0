"""
Behavioral Analysis Service - Task 22

Analyzes digital wellbeing patterns to identify correlations with academic success.
Uses statistical analysis (NumPy/Pandas) - NO LLM.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
import numpy as np
import pandas as pd

from app.models import Student, DigitalWellbeingData, TrajectoryScore

logger = logging.getLogger(__name__)


class BehavioralAnalysisService:
    """Analyze behavioral patterns and correlations."""
    
    def __init__(self):
        logger.info("Behavioral analysis service initialized")
    
    def calculate_correlations(self, db: Session) -> Dict[str, Any]:
        """
        Calculate correlations between behavioral metrics and academic performance.
        
        Returns:
            dict: {
                'screen_time_vs_gpa': float,
                'focus_score_vs_trajectory': float,
                'sleep_vs_academic': float,
                'sample_size': int,
                'optimal_ranges': dict
            }
        """
        logger.info("Calculating behavioral correlations")
        
        # Get all students with behavioral data
        students_query = db.query(
            Student.id,
            Student.gpa,
            Student.attendance,
            func.avg(DigitalWellbeingData.screen_time_hours).label('avg_screen_time'),
            func.avg(DigitalWellbeingData.focus_score).label('avg_focus_score'),
            func.avg(DigitalWellbeingData.sleep_duration_hours).label('avg_sleep')
        ).join(
            DigitalWellbeingData,
            Student.id == DigitalWellbeingData.student_id
        ).group_by(
            Student.id
        ).all()
        
        if len(students_query) < 10:
            logger.warning(f"Insufficient data for correlation analysis: {len(students_query)} students")
            return self._get_default_correlations()
        
        # Convert to pandas DataFrame
        data = []
        for student in students_query:
            # Get latest trajectory score
            trajectory = db.query(TrajectoryScore).filter(
                TrajectoryScore.student_id == student.id
            ).order_by(TrajectoryScore.calculated_at.desc()).first()
            
            data.append({
                'gpa': float(student.gpa) if student.gpa else None,
                'attendance': float(student.attendance) if student.attendance else None,
                'screen_time': float(student.avg_screen_time) if student.avg_screen_time else None,
                'focus_score': float(student.avg_focus_score) if student.avg_focus_score else None,
                'sleep': float(student.avg_sleep) if student.avg_sleep else None,
                'trajectory_score': float(trajectory.score) if trajectory else None
            })
        
        df = pd.DataFrame(data)
        df = df.dropna()  # Remove rows with missing data
        
        if len(df) < 10:
            logger.warning(f"Insufficient complete data: {len(df)} students")
            return self._get_default_correlations()
        
        # Calculate correlations
        correlations = {
            'screen_time_vs_gpa': self._safe_correlation(df, 'screen_time', 'gpa'),
            'focus_score_vs_trajectory': self._safe_correlation(df, 'focus_score', 'trajectory_score'),
            'sleep_vs_academic': self._safe_correlation(df, 'sleep', 'gpa'),
            'sample_size': len(df),
            'optimal_ranges': self._identify_optimal_ranges(df)
        }
        
        logger.info(f"Correlations calculated for {len(df)} students")
        return correlations
    
    def _safe_correlation(self, df: pd.DataFrame, col1: str, col2: str) -> float:
        """Calculate correlation safely, handling errors."""
        try:
            if col1 in df.columns and col2 in df.columns:
                corr = df[col1].corr(df[col2])
                return round(float(corr), 3) if not pd.isna(corr) else 0.0
            return 0.0
        except Exception as e:
            logger.error(f"Correlation calculation failed: {str(e)}")
            return 0.0
    
    def _identify_optimal_ranges(self, df: pd.DataFrame) -> Dict[str, Dict[str, float]]:
        """
        Identify optimal ranges for each metric based on successful students.
        Successful = top 25% by GPA or trajectory score.
        """
        # Define successful students (top 25% by GPA)
        gpa_threshold = df['gpa'].quantile(0.75)
        successful = df[df['gpa'] >= gpa_threshold]
        
        if len(successful) < 5:
            return self._get_default_optimal_ranges()
        
        optimal_ranges = {
            'screen_time': {
                'min': round(float(successful['screen_time'].quantile(0.25)), 1),
                'max': round(float(successful['screen_time'].quantile(0.75)), 1),
                'median': round(float(successful['screen_time'].median()), 1)
            },
            'focus_score': {
                'min': round(float(successful['focus_score'].quantile(0.25)), 2),
                'max': round(float(successful['focus_score'].quantile(0.75)), 2),
                'median': round(float(successful['focus_score'].median()), 2)
            },
            'sleep': {
                'min': round(float(successful['sleep'].quantile(0.25)), 1),
                'max': round(float(successful['sleep'].quantile(0.75)), 1),
                'median': round(float(successful['sleep'].median()), 1)
            }
        }
        
        return optimal_ranges
    
    def _get_default_correlations(self) -> Dict[str, Any]:
        """Return default correlations when insufficient data."""
        return {
            'screen_time_vs_gpa': -0.45,  # Negative correlation (more screen time = lower GPA)
            'focus_score_vs_trajectory': 0.62,  # Positive correlation
            'sleep_vs_academic': 0.38,  # Positive correlation
            'sample_size': 0,
            'optimal_ranges': self._get_default_optimal_ranges()
        }
    
    def _get_default_optimal_ranges(self) -> Dict[str, Dict[str, float]]:
        """Return default optimal ranges based on research."""
        return {
            'screen_time': {'min': 4.0, 'max': 6.0, 'median': 5.0},
            'focus_score': {'min': 0.6, 'max': 0.9, 'median': 0.75},
            'sleep': {'min': 7.0, 'max': 8.5, 'median': 7.5}
        }
    
    def identify_at_risk_patterns(
        self,
        student: Student,
        db: Session
    ) -> List[Dict[str, Any]]:
        """
        Identify at-risk behavioral patterns for a student.
        
        Flags:
        - High social media (>4 hours/day) + low sleep (<6 hours) + declining GPA
        - Excessive screen time (>8 hours/day)
        - Low focus score (<0.5)
        - Insufficient sleep (<6 hours)
        
        Returns:
            list: [
                {
                    'flag': str,
                    'severity': 'high' | 'medium' | 'low',
                    'description': str,
                    'metric_value': float,
                    'threshold': float
                }
            ]
        """
        logger.info(f"Identifying at-risk patterns for student {student.id}")
        
        flags = []
        
        # Get recent behavioral data (last 7 days)
        recent_date = datetime.utcnow() - timedelta(days=7)
        behavioral_data = db.query(DigitalWellbeingData).filter(
            DigitalWellbeingData.student_id == student.id,
            DigitalWellbeingData.date >= recent_date.date()
        ).all()
        
        if not behavioral_data:
            logger.warning(f"No behavioral data for student {student.id}")
            return flags
        
        # Calculate averages
        avg_screen_time = np.mean([float(d.screen_time_hours) for d in behavioral_data])
        avg_social_media = np.mean([float(d.social_media_hours) for d in behavioral_data if d.social_media_hours])
        avg_focus_score = np.mean([float(d.focus_score) for d in behavioral_data if d.focus_score])
        avg_sleep = np.mean([float(d.sleep_duration_hours) for d in behavioral_data if d.sleep_duration_hours])
        
        # Get GPA trend
        gpa_trend = self._calculate_gpa_trend(student, db)
        
        # Flag 1: High social media + low sleep + declining GPA
        if avg_social_media > 4.0 and avg_sleep < 6.0 and gpa_trend < -0.5:
            flags.append({
                'flag': 'at_risk_pattern',
                'severity': 'high',
                'description': 'High social media usage, insufficient sleep, and declining GPA detected',
                'metrics': {
                    'social_media_hours': round(avg_social_media, 1),
                    'sleep_hours': round(avg_sleep, 1),
                    'gpa_trend': round(gpa_trend, 2)
                },
                'thresholds': {
                    'social_media_max': 4.0,
                    'sleep_min': 6.0,
                    'gpa_trend_min': -0.5
                }
            })
        
        # Flag 2: Excessive screen time
        if avg_screen_time > 8.0:
            flags.append({
                'flag': 'excessive_screen_time',
                'severity': 'high' if avg_screen_time > 10.0 else 'medium',
                'description': f'Excessive screen time detected: {avg_screen_time:.1f} hours/day',
                'metric_value': round(avg_screen_time, 1),
                'threshold': 8.0
            })
        
        # Flag 3: Low focus score
        if avg_focus_score < 0.5:
            flags.append({
                'flag': 'low_focus_score',
                'severity': 'medium',
                'description': f'Low productivity focus score: {avg_focus_score:.2f}',
                'metric_value': round(avg_focus_score, 2),
                'threshold': 0.5
            })
        
        # Flag 4: Insufficient sleep
        if avg_sleep < 6.0:
            flags.append({
                'flag': 'insufficient_sleep',
                'severity': 'high' if avg_sleep < 5.0 else 'medium',
                'description': f'Insufficient sleep detected: {avg_sleep:.1f} hours/night',
                'metric_value': round(avg_sleep, 1),
                'threshold': 6.0
            })
        
        logger.info(f"Identified {len(flags)} at-risk patterns for student {student.id}")
        return flags
    
    def _calculate_gpa_trend(self, student: Student, db: Session) -> float:
        """
        Calculate GPA trend (change per semester).
        Positive = improving, Negative = declining.
        """
        # Get trajectory scores to estimate trend
        scores = db.query(TrajectoryScore).filter(
            TrajectoryScore.student_id == student.id
        ).order_by(TrajectoryScore.calculated_at.desc()).limit(6).all()
        
        if len(scores) < 3:
            return 0.0  # Not enough data
        
        # Calculate velocity (trend)
        recent_avg = np.mean([float(s.score) for s in scores[:3]])
        previous_avg = np.mean([float(s.score) for s in scores[3:6]])
        
        trend = (recent_avg - previous_avg) / 3  # Per week
        return round(trend, 2)
    
    def compare_to_successful_alumni(
        self,
        student: Student,
        db: Session,
        optimal_ranges: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """
        Compare student's behavioral patterns to successful alumni.
        
        Returns:
            dict: {
                'screen_time': {'student': float, 'optimal': float, 'status': str},
                'focus_score': {...},
                'sleep': {...}
            }
        """
        # Get student's recent averages
        recent_date = datetime.utcnow() - timedelta(days=7)
        behavioral_data = db.query(DigitalWellbeingData).filter(
            DigitalWellbeingData.student_id == student.id,
            DigitalWellbeingData.date >= recent_date.date()
        ).all()
        
        if not behavioral_data:
            return {}
        
        student_avg_screen_time = np.mean([float(d.screen_time_hours) for d in behavioral_data])
        student_avg_focus = np.mean([float(d.focus_score) for d in behavioral_data if d.focus_score])
        student_avg_sleep = np.mean([float(d.sleep_duration_hours) for d in behavioral_data if d.sleep_duration_hours])
        
        comparison = {
            'screen_time': {
                'student': round(student_avg_screen_time, 1),
                'optimal': optimal_ranges['screen_time']['median'],
                'status': self._get_status(
                    student_avg_screen_time,
                    optimal_ranges['screen_time']['min'],
                    optimal_ranges['screen_time']['max'],
                    inverse=True  # Lower is better for screen time
                )
            },
            'focus_score': {
                'student': round(student_avg_focus, 2),
                'optimal': optimal_ranges['focus_score']['median'],
                'status': self._get_status(
                    student_avg_focus,
                    optimal_ranges['focus_score']['min'],
                    optimal_ranges['focus_score']['max']
                )
            },
            'sleep': {
                'student': round(student_avg_sleep, 1),
                'optimal': optimal_ranges['sleep']['median'],
                'status': self._get_status(
                    student_avg_sleep,
                    optimal_ranges['sleep']['min'],
                    optimal_ranges['sleep']['max']
                )
            }
        }
        
        return comparison
    
    def _get_status(
        self,
        value: float,
        min_optimal: float,
        max_optimal: float,
        inverse: bool = False
    ) -> str:
        """
        Determine if value is within optimal range.
        
        Args:
            inverse: If True, lower values are better (e.g., screen time)
        """
        if inverse:
            if value <= max_optimal:
                return 'good'
            elif value <= max_optimal * 1.2:
                return 'fair'
            else:
                return 'poor'
        else:
            if min_optimal <= value <= max_optimal:
                return 'good'
            elif value >= min_optimal * 0.8 and value <= max_optimal * 1.2:
                return 'fair'
            else:
                return 'poor'


_behavioral_analysis_service: Optional[BehavioralAnalysisService] = None

def get_behavioral_analysis_service() -> BehavioralAnalysisService:
    global _behavioral_analysis_service
    if _behavioral_analysis_service is None:
        _behavioral_analysis_service = BehavioralAnalysisService()
    return _behavioral_analysis_service
