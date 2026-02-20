"""
Skill Market Demand Analysis - LLM Job #5

Analyzes skill demand in job market.
Assigns market weight: 0.5x (Low), 1.0x (Medium), 2.0x (High)

Temperature: 0.2 (mostly deterministic)
Max Tokens: 300
"""

import logging
from typing import Dict, Any, Optional
from app.services.ollama_client import get_ollama_client

logger = logging.getLogger(__name__)


class SkillDemandService:
    """Analyze skill market demand using LLM."""
    
    # Default weights for common skills (fallback)
    DEFAULT_WEIGHTS = {
        # High demand (2.0x)
        'python': 2.0,
        'react': 2.0,
        'node.js': 2.0,
        'aws': 2.0,
        'docker': 2.0,
        'kubernetes': 2.0,
        'machine learning': 2.0,
        'data science': 2.0,
        'typescript': 2.0,
        
        # Medium demand (1.0x)
        'java': 1.0,
        'javascript': 1.0,
        'sql': 1.0,
        'git': 1.0,
        'html': 1.0,
        'css': 1.0,
        'c++': 1.0,
        
        # Low demand (0.5x)
        'jquery': 0.5,
        'flash': 0.5,
        'php': 0.5,
        'perl': 0.5,
    }
    
    def __init__(self):
        self.client = get_ollama_client()
        self.cache = {}  # Simple in-memory cache
        logger.info("Skill demand service initialized")
    
    def analyze_skill_demand(
        self,
        skill: str,
        major: str = "Computer Science",
        year: int = 2026
    ) -> Dict[str, Any]:
        """
        Analyze skill market demand.
        
        Returns:
            dict: {
                'skill': str,
                'market_weight': float (0.5, 1.0, or 2.0),
                'demand_level': str ('Low', 'Medium', 'High'),
                'reasoning': str,
                'success': bool,
                'method': 'llm' or 'default'
            }
        """
        logger.info(f"Analyzing demand for skill: {skill}")
        
        # Check cache
        cache_key = f"{skill.lower()}_{major}_{year}"
        if cache_key in self.cache:
            logger.info("Returning cached result")
            return self.cache[cache_key]
        
        # Try LLM
        if self.client.is_available():
            try:
                result = self._analyze_with_llm(skill, major, year)
                self.cache[cache_key] = result
                return result
            except Exception as e:
                logger.error(f"LLM analysis failed: {str(e)}")
        
        # Fallback to default weights
        result = self._analyze_with_defaults(skill)
        self.cache[cache_key] = result
        return result
    
    def _analyze_with_llm(
        self,
        skill: str,
        major: str,
        year: int
    ) -> Dict[str, Any]:
        """Analyze using LLM."""
        
        prompt = f"""Analyze market demand for the skill "{skill}" in {year} for {major} graduates.

Assign EXACTLY ONE weight:
- 2.0x = High Demand (trending, high salary premium, many job postings)
- 1.0x = Medium Demand (standard, stable demand)
- 0.5x = Low Demand (outdated, declining, low demand)

Provide brief reasoning (job market trends, salary data, placement success).

Format as JSON:
{{"market_weight": 2.0, "reasoning": "..."}}

ANALYSIS:"""
        
        result = self.client.generate(
            prompt=prompt,
            temperature=0.2,
            max_tokens=300
        )
        
        if result['success']:
            import json, re
            json_match = re.search(r'\{.*\}', result['text'], re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                weight = data.get('market_weight', 1.0)
                
                # Ensure valid weight
                if weight not in [0.5, 1.0, 2.0]:
                    weight = 1.0
                
                demand_level = {0.5: 'Low', 1.0: 'Medium', 2.0: 'High'}[weight]
                
                return {
                    'skill': skill,
                    'market_weight': weight,
                    'demand_level': demand_level,
                    'reasoning': data.get('reasoning', ''),
                    'success': True,
                    'method': 'llm'
                }
        
        raise Exception("LLM analysis failed")
    
    def _analyze_with_defaults(self, skill: str) -> Dict[str, Any]:
        """Use default weights (fallback)."""
        
        skill_lower = skill.lower().strip()
        weight = self.DEFAULT_WEIGHTS.get(skill_lower, 1.0)
        demand_level = {0.5: 'Low', 1.0: 'Medium', 2.0: 'High'}[weight]
        
        reasoning = f"Default weight based on general market trends for {skill}"
        
        return {
            'skill': skill,
            'market_weight': weight,
            'demand_level': demand_level,
            'reasoning': reasoning,
            'success': True,
            'method': 'default'
        }
    
    def get_cached_demand(self, skill: str) -> Optional[Dict[str, Any]]:
        """Get cached demand analysis."""
        cache_key = f"{skill.lower()}_Computer Science_2026"
        return self.cache.get(cache_key)
    
    def clear_cache(self):
        """Clear the demand cache."""
        self.cache.clear()
        logger.info("Skill demand cache cleared")


_skill_demand_service: Optional[SkillDemandService] = None

def get_skill_demand_service() -> SkillDemandService:
    global _skill_demand_service
    if _skill_demand_service is None:
        _skill_demand_service = SkillDemandService()
    return _skill_demand_service
