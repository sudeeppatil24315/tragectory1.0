"""
Recommendation Engine - LLM Job #2

Generates personalized recommendations for students based on:
- Student profile and gaps
- Similar alumni success stories
- Behavioral patterns

Temperature: 0.7 (creative for recommendations)
Max Tokens: 800
"""

import logging
from typing import Dict, Any, List, Optional
from app.services.ollama_client import get_ollama_client

logger = logging.getLogger(__name__)


class RecommendationEngine:
    """Generate AI-powered recommendations for students."""
    
    def __init__(self):
        self.client = get_ollama_client()
        logger.info("Recommendation engine initialized")
    
    def generate_recommendations(
        self,
        student_profile: Dict[str, Any],
        gap_analysis: Dict[str, Any],
        similar_alumni: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Generate 3-5 actionable recommendations.
        
        Returns:
            dict: {
                'recommendations': List of recommendation dicts,
                'success': bool,
                'method': 'llm' or 'template'
            }
        """
        logger.info(f"Generating recommendations for student")
        
        # Try LLM first
        if self.client.is_available():
            try:
                return self._generate_with_llm(student_profile, gap_analysis, similar_alumni)
            except Exception as e:
                logger.error(f"LLM generation failed: {str(e)}")
        
        # Fallback to template-based
        return self._generate_with_templates(student_profile, gap_analysis)
    
    def _generate_with_llm(
        self,
        student_profile: Dict[str, Any],
        gap_analysis: Dict[str, Any],
        similar_alumni: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate recommendations using LLM."""
        
        prompt = f"""You are a career advisor. Generate 3-5 actionable recommendations for this student.

STUDENT PROFILE:
- Major: {student_profile.get('major', 'Unknown')}
- GPA: {student_profile.get('gpa', 0)}/10.0
- Trajectory Score: {student_profile.get('trajectory_score', 50)}/100

KEY GAPS:
{self._format_gaps(gap_analysis)}

SIMILAR SUCCESSFUL ALUMNI:
{self._format_alumni(similar_alumni)}

Generate 3-5 specific, actionable recommendations. For each:
1. Title (short, clear)
2. Description (specific actions)
3. Impact (High/Medium/Low)
4. Estimated points improvement (+X points)
5. Timeline (e.g., "2 weeks", "1 month")

Format as JSON array:
[{{"title": "...", "description": "...", "impact": "High", "estimated_points": 5, "timeline": "2 weeks"}}]

RECOMMENDATIONS:"""
        
        result = self.client.generate(
            prompt=prompt,
            temperature=0.7,
            max_tokens=800
        )
        
        if result['success']:
            import json, re
            json_match = re.search(r'\[.*\]', result['text'], re.DOTALL)
            if json_match:
                recommendations = json.loads(json_match.group(0))
                return {
                    'recommendations': recommendations,
                    'success': True,
                    'method': 'llm'
                }
        
        raise Exception("LLM generation failed")
    
    def _generate_with_templates(
        self,
        student_profile: Dict[str, Any],
        gap_analysis: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate recommendations using templates (fallback)."""
        
        recommendations = []
        gpa = student_profile.get('gpa', 5.0)
        
        # Template recommendations based on common gaps
        if gpa < 7.0:
            recommendations.append({
                "title": "Improve Academic Performance",
                "description": "Focus on core subjects, attend office hours, form study groups",
                "impact": "High",
                "estimated_points": 8,
                "timeline": "1 semester"
            })
        
        recommendations.append({
            "title": "Build Technical Projects",
            "description": "Create 2-3 portfolio projects showcasing your skills",
            "impact": "High",
            "estimated_points": 10,
            "timeline": "2 months"
        })
        
        recommendations.append({
            "title": "Improve Digital Wellbeing",
            "description": "Reduce social media to <2 hours/day, improve sleep to 7+ hours",
            "impact": "Medium",
            "estimated_points": 5,
            "timeline": "1 month"
        })
        
        return {
            'recommendations': recommendations[:5],
            'success': True,
            'method': 'template'
        }
    
    def _format_gaps(self, gap_analysis: Dict[str, Any]) -> str:
        """Format gaps for prompt."""
        if not gap_analysis:
            return "No significant gaps identified"
        
        gaps = gap_analysis.get('gaps', [])
        return "\n".join([f"- {g}" for g in gaps[:5]])
    
    def _format_alumni(self, similar_alumni: List[Dict[str, Any]]) -> str:
        """Format alumni for prompt."""
        if not similar_alumni:
            return "No similar alumni data available"
        
        lines = []
        for alumni in similar_alumni[:3]:
            lines.append(f"- {alumni.get('company_tier', 'Unknown')} company, "
                        f"Similarity: {alumni.get('similarity_score', 0):.0%}")
        return "\n".join(lines)


_recommendation_engine: Optional[RecommendationEngine] = None

def get_recommendation_engine() -> RecommendationEngine:
    global _recommendation_engine
    if _recommendation_engine is None:
        _recommendation_engine = RecommendationEngine()
    return _recommendation_engine
