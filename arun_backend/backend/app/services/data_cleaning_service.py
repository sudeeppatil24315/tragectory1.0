"""
Data Cleaning Service - LLM Job #1

This service uses Ollama LLM to clean and standardize student/alumni data.
Features:
- Fix typos in major names ("Comp Sci" → "Computer Science")
- Normalize GPA to 10.0 scale
- Standardize skill names ("ReactJS" → "React")
- Trim whitespace and fix capitalization
- Return cleaned data in JSON format with quality score
- Rule-based fallback when LLM unavailable

Temperature: 0.1 (very deterministic for data cleaning)
Max Tokens: 500
"""

import json
import re
import logging
from typing import Dict, Any, Optional
from app.services.ollama_client import get_ollama_client

logger = logging.getLogger(__name__)


class DataCleaningService:
    """
    Data cleaning service using Ollama LLM with rule-based fallback.
    
    This service cleans and standardizes messy student/alumni data:
    - Fixes typos and inconsistent naming
    - Normalizes GPA scales
    - Standardizes skill names
    - Fixes capitalization and whitespace
    
    Uses LLM for intelligent cleaning with rule-based fallback.
    """
    
    # Common major name mappings (for fallback)
    MAJOR_MAPPINGS = {
        "comp sci": "Computer Science",
        "computer sci": "Computer Science",
        "cs": "Computer Science",
        "cse": "Computer Science",
        "it": "Information Technology",
        "info tech": "Information Technology",
        "mech": "Mechanical Engineering",
        "mechanical": "Mechanical Engineering",
        "mech eng": "Mechanical Engineering",
        "civil": "Civil Engineering",
        "civil eng": "Civil Engineering",
        "electrical": "Electrical Engineering",
        "elec": "Electrical Engineering",
        "eee": "Electrical Engineering",
        "ece": "Electronics Engineering",
        "electronics": "Electronics Engineering",
        "bba": "Business Administration",
        "business": "Business Administration",
        "mba": "Business Administration",
        "data sci": "Data Science",
        "ds": "Data Science",
    }
    
    # Common skill name mappings (for fallback)
    SKILL_MAPPINGS = {
        "reactjs": "React",
        "react.js": "React",
        "react js": "React",
        "nodejs": "Node.js",
        "node.js": "Node.js",
        "node js": "Node.js",
        "javascript": "JavaScript",
        "js": "JavaScript",
        "typescript": "TypeScript",
        "ts": "TypeScript",
        "python3": "Python",
        "py": "Python",
        "java script": "JavaScript",
        "c++": "C++",
        "cpp": "C++",
        "c plus plus": "C++",
        "html5": "HTML",
        "css3": "CSS",
        "mongodb": "MongoDB",
        "mongo": "MongoDB",
        "postgresql": "PostgreSQL",
        "postgres": "PostgreSQL",
        "mysql": "MySQL",
        "my sql": "MySQL",
    }
    
    def __init__(self):
        """Initialize data cleaning service with Ollama client."""
        self.client = get_ollama_client()
        logger.info("Data cleaning service initialized")
    
    def clean_student_record(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean and standardize a student/alumni record.
        
        This method:
        1. Attempts to clean using LLM (intelligent, context-aware)
        2. Falls back to rule-based cleaning if LLM unavailable
        3. Returns cleaned data with quality score
        
        Args:
            raw_data: Raw student/alumni data dict with fields:
                - name: Student name (may have typos, wrong case)
                - major: Major name (may be abbreviated or misspelled)
                - gpa: GPA (may be on wrong scale)
                - skills: List of skill names (may be inconsistent)
                - ... other fields
        
        Returns:
            dict: Cleaned data with:
                - cleaned_data: Standardized data dict
                - quality_score: 0-100 (confidence in cleaning)
                - method: "llm" or "rule-based"
                - changes: List of changes made
        """
        logger.info(f"Cleaning record for: {raw_data.get('name', 'Unknown')}")
        
        # Try LLM cleaning first
        if self.client.is_available():
            try:
                result = self._clean_with_llm(raw_data)
                if result['success']:
                    logger.info("LLM cleaning successful")
                    return result
                else:
                    logger.warning(f"LLM cleaning failed: {result.get('error', 'Unknown')}")
            except Exception as e:
                logger.error(f"LLM cleaning error: {str(e)}")
        
        # Fallback to rule-based cleaning
        logger.info("Using rule-based fallback cleaning")
        return self._clean_with_rules(raw_data)
    
    def _clean_with_llm(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean data using Ollama LLM.
        
        Uses temperature 0.1 for very deterministic cleaning.
        """
        # Build prompt
        prompt = self._build_cleaning_prompt(raw_data)
        
        # Generate with LLM
        result = self.client.generate(
            prompt=prompt,
            temperature=0.1,  # Very deterministic
            max_tokens=500
        )
        
        if not result['success']:
            return {
                'success': False,
                'error': result.get('error', 'LLM generation failed')
            }
        
        # Parse JSON response
        try:
            cleaned_data = self._parse_llm_response(result['text'])
            
            # Calculate quality score based on changes made
            changes = self._identify_changes(raw_data, cleaned_data)
            quality_score = self._calculate_quality_score(changes, result)
            
            return {
                'success': True,
                'cleaned_data': cleaned_data,
                'quality_score': quality_score,
                'method': 'llm',
                'changes': changes,
                'response_time': result['response_time']
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response: {str(e)}")
            return {
                'success': False,
                'error': f'JSON parsing failed: {str(e)}'
            }
    
    def _build_cleaning_prompt(self, raw_data: Dict[str, Any]) -> str:
        """
        Build prompt for LLM data cleaning.
        
        The prompt instructs the LLM to:
        - Fix typos and inconsistent naming
        - Normalize GPA to 10.0 scale
        - Standardize skill names
        - Fix capitalization
        - Return JSON format
        """
        prompt = f"""You are a data cleaning assistant. Clean and standardize the following student/alumni record.

RULES:
1. Fix typos in major names (e.g., "Comp Sci" → "Computer Science")
2. Normalize GPA to 10.0 scale if needed (e.g., 3.5/4.0 → 8.75/10.0)
3. Standardize skill names (e.g., "ReactJS" → "React", "nodejs" → "Node.js")
4. Fix capitalization (proper case for names, title case for majors)
5. Trim whitespace
6. Keep all other fields unchanged

RAW DATA:
{json.dumps(raw_data, indent=2)}

Return ONLY a JSON object with the cleaned data. No explanations, just the JSON.

CLEANED DATA:"""
        
        return prompt
    
    def _parse_llm_response(self, response_text: str) -> Dict[str, Any]:
        """
        Parse LLM response to extract cleaned JSON data.
        
        Handles cases where LLM includes extra text before/after JSON.
        """
        # Try to find JSON in response
        # Look for { ... } pattern
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        
        if json_match:
            json_str = json_match.group(0)
            return json.loads(json_str)
        else:
            # Try parsing entire response
            return json.loads(response_text)
    
    def _clean_with_rules(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Clean data using rule-based approach (fallback).
        
        This method applies predefined rules for common cleaning tasks:
        - Major name standardization
        - GPA normalization
        - Skill name standardization
        - Capitalization fixes
        """
        cleaned_data = raw_data.copy()
        changes = []
        
        # Clean name (proper case)
        if 'name' in cleaned_data and cleaned_data['name']:
            original = cleaned_data['name']
            cleaned_data['name'] = cleaned_data['name'].strip().title()
            if original != cleaned_data['name']:
                changes.append(f"Name: '{original}' → '{cleaned_data['name']}'")
        
        # Clean major (standardize)
        if 'major' in cleaned_data and cleaned_data['major']:
            original = cleaned_data['major']
            major_lower = original.lower().strip()
            
            # Check mappings
            if major_lower in self.MAJOR_MAPPINGS:
                cleaned_data['major'] = self.MAJOR_MAPPINGS[major_lower]
                changes.append(f"Major: '{original}' → '{cleaned_data['major']}'")
            else:
                # Just fix capitalization
                cleaned_data['major'] = original.strip().title()
                if original != cleaned_data['major']:
                    changes.append(f"Major: '{original}' → '{cleaned_data['major']}'")
        
        # Normalize GPA to 10.0 scale
        if 'gpa' in cleaned_data and cleaned_data['gpa']:
            original = cleaned_data['gpa']
            gpa = float(original)
            
            # Detect scale and normalize
            if gpa <= 4.0:
                # Assume 4.0 scale, convert to 10.0
                cleaned_data['gpa'] = round((gpa / 4.0) * 10.0, 2)
                changes.append(f"GPA: {original}/4.0 → {cleaned_data['gpa']}/10.0")
            elif gpa <= 5.0:
                # Assume 5.0 scale, convert to 10.0
                cleaned_data['gpa'] = round((gpa / 5.0) * 10.0, 2)
                changes.append(f"GPA: {original}/5.0 → {cleaned_data['gpa']}/10.0")
            # else: already on 10.0 scale
        
        # Clean skills (standardize names)
        if 'skills' in cleaned_data and isinstance(cleaned_data['skills'], list):
            original_skills = cleaned_data['skills'].copy()
            cleaned_skills = []
            
            for skill in original_skills:
                if isinstance(skill, str):
                    skill_lower = skill.lower().strip()
                    
                    # Check mappings
                    if skill_lower in self.SKILL_MAPPINGS:
                        cleaned_skills.append(self.SKILL_MAPPINGS[skill_lower])
                        if skill != self.SKILL_MAPPINGS[skill_lower]:
                            changes.append(f"Skill: '{skill}' → '{self.SKILL_MAPPINGS[skill_lower]}'")
                    else:
                        # Just fix capitalization
                        cleaned_skill = skill.strip().title()
                        cleaned_skills.append(cleaned_skill)
                        if skill != cleaned_skill:
                            changes.append(f"Skill: '{skill}' → '{cleaned_skill}'")
            
            cleaned_data['skills'] = cleaned_skills
        
        # Calculate quality score (lower for rule-based)
        quality_score = 75.0  # Rule-based is less confident than LLM
        if len(changes) > 0:
            quality_score = 80.0  # Higher if we made changes
        
        return {
            'success': True,
            'cleaned_data': cleaned_data,
            'quality_score': quality_score,
            'method': 'rule-based',
            'changes': changes
        }
    
    def _identify_changes(
        self,
        original: Dict[str, Any],
        cleaned: Dict[str, Any]
    ) -> list[str]:
        """
        Identify what changes were made during cleaning.
        
        Returns list of change descriptions.
        """
        changes = []
        
        for key in original.keys():
            if key in cleaned:
                if original[key] != cleaned[key]:
                    changes.append(f"{key}: '{original[key]}' → '{cleaned[key]}'")
        
        return changes
    
    def _calculate_quality_score(
        self,
        changes: list[str],
        llm_result: Dict[str, Any]
    ) -> float:
        """
        Calculate quality score for cleaned data.
        
        Factors:
        - Number of changes made (more changes = more cleaning needed)
        - LLM response time (faster = more confident)
        - LLM success (always high for successful LLM cleaning)
        
        Returns score 0-100.
        """
        base_score = 90.0  # LLM cleaning is high quality
        
        # Adjust based on number of changes
        if len(changes) == 0:
            # No changes needed - data was already clean
            return 95.0
        elif len(changes) <= 3:
            # Few changes - good quality
            return 90.0
        elif len(changes) <= 6:
            # Moderate changes - decent quality
            return 85.0
        else:
            # Many changes - lower confidence
            return 80.0
    
    def clean_batch(
        self,
        records: list[Dict[str, Any]]
    ) -> list[Dict[str, Any]]:
        """
        Clean multiple records in batch.
        
        Uses parallel processing if LLM is available.
        
        Args:
            records: List of raw data dicts
        
        Returns:
            list: List of cleaning results
        """
        logger.info(f"Cleaning batch of {len(records)} records")
        
        results = []
        for record in records:
            result = self.clean_student_record(record)
            results.append(result)
        
        # Log summary
        successful = sum(1 for r in results if r.get('success', False))
        llm_count = sum(1 for r in results if r.get('method') == 'llm')
        
        logger.info(f"Batch cleaning complete: {successful}/{len(records)} successful, "
                   f"{llm_count} used LLM, {len(records)-llm_count} used rules")
        
        return results


# Global service instance (singleton pattern)
_data_cleaning_service: Optional[DataCleaningService] = None


def get_data_cleaning_service() -> DataCleaningService:
    """
    Get or create the global data cleaning service instance.
    
    Returns:
        DataCleaningService: The global service instance
    """
    global _data_cleaning_service
    
    if _data_cleaning_service is None:
        _data_cleaning_service = DataCleaningService()
        logger.info("Created global data cleaning service instance")
    
    return _data_cleaning_service
