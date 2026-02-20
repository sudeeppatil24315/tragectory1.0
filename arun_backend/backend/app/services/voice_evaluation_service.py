"""
Voice Evaluation Service - LLM Job #3

Evaluates technical answers for skill assessment.
Text-based MVP (full VAPI integration deferred to 90-day plan).

Temperature: 0.3 (slightly creative)
Max Tokens: 400
"""

import logging
from typing import Dict, Any, Optional
from app.services.ollama_client import get_ollama_client

logger = logging.getLogger(__name__)


class VoiceEvaluationService:
    """Evaluate technical answers using LLM."""
    
    def __init__(self):
        self.client = get_ollama_client()
        logger.info("Voice evaluation service initialized")
    
    def evaluate_response(
        self,
        question: str,
        answer: str,
        skill: str
    ) -> Dict[str, Any]:
        """
        Evaluate a technical answer.
        
        Returns:
            dict: {
                'overall_score': 0-100,
                'dimensions': {
                    'technical_accuracy': 0-10,
                    'communication_clarity': 0-10,
                    'depth': 0-10,
                    'completeness': 0-10
                },
                'feedback': str,
                'success': bool
            }
        """
        logger.info(f"Evaluating answer for skill: {skill}")
        
        if self.client.is_available():
            try:
                return self._evaluate_with_llm(question, answer, skill)
            except Exception as e:
                logger.error(f"LLM evaluation failed: {str(e)}")
        
        return self._evaluate_with_keywords(question, answer, skill)
    
    def _evaluate_with_llm(
        self,
        question: str,
        answer: str,
        skill: str
    ) -> Dict[str, Any]:
        """Evaluate using LLM."""
        
        prompt = f"""Evaluate this technical answer for {skill} skill assessment.

QUESTION: {question}

ANSWER: {answer}

Score on 4 dimensions (0-10 each):
1. Technical Accuracy: Is the answer correct?
2. Communication Clarity: Is it well-explained?
3. Depth of Understanding: Does it show deep knowledge?
4. Completeness: Does it cover all aspects?

Provide scores and brief feedback.

Format as JSON:
{{"technical_accuracy": X, "communication_clarity": X, "depth": X, "completeness": X, "feedback": "..."}}

EVALUATION:"""
        
        result = self.client.generate(
            prompt=prompt,
            temperature=0.3,
            max_tokens=400
        )
        
        if result['success']:
            import json, re
            json_match = re.search(r'\{.*\}', result['text'], re.DOTALL)
            if json_match:
                eval_data = json.loads(json_match.group(0))
                
                # Calculate overall score
                overall = (
                    eval_data.get('technical_accuracy', 5) +
                    eval_data.get('communication_clarity', 5) +
                    eval_data.get('depth', 5) +
                    eval_data.get('completeness', 5)
                ) * 2.5  # Scale to 0-100
                
                return {
                    'overall_score': round(overall, 1),
                    'dimensions': {
                        'technical_accuracy': eval_data.get('technical_accuracy', 5),
                        'communication_clarity': eval_data.get('communication_clarity', 5),
                        'depth': eval_data.get('depth', 5),
                        'completeness': eval_data.get('completeness', 5)
                    },
                    'feedback': eval_data.get('feedback', ''),
                    'success': True,
                    'method': 'llm'
                }
        
        raise Exception("LLM evaluation failed")
    
    def _evaluate_with_keywords(
        self,
        question: str,
        answer: str,
        skill: str
    ) -> Dict[str, Any]:
        """Keyword-based fallback scoring."""
        
        answer_lower = answer.lower()
        
        # Simple keyword scoring
        score = 50  # Base score
        
        # Check for technical terms
        if len(answer) > 50:
            score += 10
        if len(answer) > 100:
            score += 10
        
        # Check for code-related terms
        code_terms = ['function', 'class', 'method', 'variable', 'return', 'if', 'for', 'while']
        score += sum(5 for term in code_terms if term in answer_lower)
        
        score = min(score, 100)
        
        return {
            'overall_score': score,
            'dimensions': {
                'technical_accuracy': score // 10,
                'communication_clarity': score // 10,
                'depth': score // 10,
                'completeness': score // 10
            },
            'feedback': 'Evaluated using keyword-based scoring',
            'success': True,
            'method': 'keyword'
        }


_voice_evaluation_service: Optional[VoiceEvaluationService] = None

def get_voice_evaluation_service() -> VoiceEvaluationService:
    global _voice_evaluation_service
    if _voice_evaluation_service is None:
        _voice_evaluation_service = VoiceEvaluationService()
    return _voice_evaluation_service
