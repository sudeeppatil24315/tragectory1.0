"""
Gap Analysis Service - LLM Job #4

Calculates gaps between student and successful alumni.
Generates narrative explaining why gaps matter.

Temperature: 0.7 (creative for narratives)
Max Tokens: 600
"""

import logging
from typing import Dict, Any, List, Optional
from app.services.ollama_client import get_ollama_client

logger = logging.getLogger(__name__)


class GapAnalysisService:
    """Calculate and explain gaps between student and alumni."""
    
    def __init__(self):
        self.client = get_ollama_client()
        logger.info("Gap analysis service initialized")
    
    def calculate_gaps(
        self,
        student: Dict[str, Any],
        alumni_avg: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Calculate gaps (pure math).
        
        Returns:
            dict: {
                'gaps': List of gap dicts with percentage and absolute values,
                'priority_gaps': Top 3 gaps by impact
            }
        """
        gaps = []
        
        # GPA gap
        if 'gpa' in student and 'gpa' in alumni_avg:
            student_gpa = student['gpa']
            alumni_gpa = alumni_avg['gpa']
            if alumni_gpa > 0:
                pct_gap = abs(student_gpa - alumni_gpa) / alumni_gpa * 100
                abs_gap = alumni_gpa - student_gpa
                gaps.append({
                    'metric': 'GPA',
                    'student_value': student_gpa,
                    'alumni_average': alumni_gpa,
                    'percentage_gap': round(pct_gap, 1),
                    'absolute_gap': round(abs_gap, 2),
                    'impact': 'High' if abs_gap > 1.0 else 'Medium'
                })
        
        # Attendance gap
        if 'attendance' in student and 'attendance' in alumni_avg:
            student_att = student['attendance']
            alumni_att = alumni_avg['attendance']
            if alumni_att > 0:
                pct_gap = abs(student_att - alumni_att) / alumni_att * 100
                abs_gap = alumni_att - student_att
                gaps.append({
                    'metric': 'Attendance',
                    'student_value': student_att,
                    'alumni_average': alumni_att,
                    'percentage_gap': round(pct_gap, 1),
                    'absolute_gap': round(abs_gap, 1),
                    'impact': 'High' if abs_gap > 10 else 'Medium'
                })
        
        # Study hours gap
        if 'study_hours_per_week' in student and 'study_hours_per_week' in alumni_avg:
            student_hours = student['study_hours_per_week']
            alumni_hours = alumni_avg['study_hours_per_week']
            if alumni_hours > 0:
                pct_gap = abs(student_hours - alumni_hours) / alumni_hours * 100
                abs_gap = alumni_hours - student_hours
                gaps.append({
                    'metric': 'Study Hours',
                    'student_value': student_hours,
                    'alumni_average': alumni_hours,
                    'percentage_gap': round(pct_gap, 1),
                    'absolute_gap': round(abs_gap, 1),
                    'impact': 'Medium'
                })
        
        # Sort by impact and absolute gap
        priority_gaps = sorted(gaps, key=lambda x: abs(x['absolute_gap']), reverse=True)[:3]
        
        return {
            'gaps': gaps,
            'priority_gaps': priority_gaps
        }
    
    def generate_narrative(
        self,
        gaps: List[Dict[str, Any]],
        alumni_stories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate narrative explaining gaps.
        
        Returns:
            dict: {
                'narrative': str,
                'success': bool,
                'method': 'llm' or 'template'
            }
        """
        logger.info("Generating gap narrative")
        
        if self.client.is_available():
            try:
                return self._generate_with_llm(gaps, alumni_stories)
            except Exception as e:
                logger.error(f"LLM narrative generation failed: {str(e)}")
        
        return self._generate_with_template(gaps)
    
    def _generate_with_llm(
        self,
        gaps: List[Dict[str, Any]],
        alumni_stories: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate narrative using LLM."""
        
        gaps_text = "\n".join([
            f"- {g['metric']}: Student {g['student_value']}, Alumni Avg {g['alumni_average']} "
            f"(Gap: {g['absolute_gap']:+.1f})"
            for g in gaps[:5]
        ])
        
        prompt = f"""You are a career advisor. Explain why these gaps matter for career outcomes.

STUDENT GAPS:
{gaps_text}

SUCCESSFUL ALUMNI:
{len(alumni_stories)} similar alumni placed in good companies

Write a motivating, data-driven narrative (2-3 paragraphs) explaining:
1. Why these gaps impact placement chances
2. How closing gaps improves trajectory score
3. Reference similar alumni who closed these gaps

Keep it friendly, supportive, and actionable.

NARRATIVE:"""
        
        result = self.client.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=600
        )
        
        if result['success']:
            return {
                'narrative': result['text'].strip(),
                'success': True,
                'method': 'llm'
            }
        
        raise Exception("LLM narrative generation failed")
    
    def _generate_with_template(self, gaps: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Template-based narrative (fallback)."""
        
        if not gaps:
            narrative = "Great job! Your profile is well-aligned with successful alumni."
        else:
            top_gap = gaps[0]
            narrative = f"""Based on analysis of successful alumni, we've identified key areas for improvement.

Your {top_gap['metric']} is currently {top_gap['student_value']}, while successful alumni average {top_gap['alumni_average']}. Closing this gap could improve your trajectory score by 5-10 points.

Focus on the priority gaps first - they have the highest impact on your placement chances. Small, consistent improvements in these areas will significantly boost your employability."""
        
        return {
            'narrative': narrative,
            'success': True,
            'method': 'template'
        }


_gap_analysis_service: Optional[GapAnalysisService] = None

def get_gap_analysis_service() -> GapAnalysisService:
    global _gap_analysis_service
    if _gap_analysis_service is None:
        _gap_analysis_service = GapAnalysisService()
    return _gap_analysis_service
