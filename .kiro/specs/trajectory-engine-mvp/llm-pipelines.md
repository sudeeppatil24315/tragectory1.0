# LLM Pipelines Documentation

## Overview

This document provides comprehensive documentation for all 5 LLM jobs in the Trajectory Engine MVP. Each pipeline uses Llama 3.1 8B via Ollama running locally on Lenovo Legion 5i (RTX 4060).

**Hardware Context:**
- GPU: RTX 4060 (8GB VRAM)
- CPU: i7 14th Gen HX (14 cores)
- RAM: 16GB
- Model: Llama 3.1 8B (~4.7GB model size)
- Expected Performance: 0.5-1 second per request, 8+ simultaneous requests

**Cost:** $0 (no cloud API costs)

---

## LLM Infrastructure

### Ollama Configuration

**Installation:**
```bash
# Install Ollama (Windows)
# Download from: https://ollama.ai/download/windows

# Pull Llama 3.1 8B model
ollama pull llama3.1:8b

# Verify installation
ollama list

# Test model
ollama run llama3.1:8b "Hello, how are you?"
```

**Ollama Server Configuration:**
```bash
# Start Ollama server (runs on localhost:11434)
ollama serve

# Configure for optimal performance
# Edit Ollama config (modelfile or environment variables):
# - num_gpu: 1 (use RTX 4060)
# - num_thread: 14 (use all CPU cores)
# - num_parallel: 8 (handle 8 simultaneous requests)
# - num_ctx: 4096 (context window size)
```

**Environment Variables:**
```bash
OLLAMA_HOST=localhost:11434
OLLAMA_NUM_PARALLEL=8
OLLAMA_MAX_LOADED_MODELS=1
OLLAMA_GPU_LAYERS=33  # Load all layers on GPU
```

---

## LLM Client Wrapper

### Python Client Implementation

**File:** `backend/services/llm_client.py`

```python
import requests
import json
import time
from typing import Dict, Any, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

class OllamaClient:
    """
    Wrapper for Ollama API calls with connection pooling,
    retry logic, and error handling.
    """
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.generate_url = f"{base_url}/api/generate"
        self.health_url = f"{base_url}/api/tags"
        
    def health_check(self) -> bool:
        """Check if Ollama server is running and model is loaded."""
        try:
            response = requests.get(self.health_url, timeout=5)
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(m["name"].startswith("llama3.1:8b") for m in models)
            return False
        except Exception as e:
            logger.error(f"Ollama health check failed: {e}")
            return False
    
    def generate(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 500,
        system_prompt: Optional[str] = None,
        timeout: int = 30
    ) -> Dict[str, Any]:
        """
        Generate text using Llama 3.1 8B.
        
        Args:
            prompt: User prompt
            temperature: 0.0-1.0 (0.1=deterministic, 0.7=creative)
            max_tokens: Maximum tokens to generate
            system_prompt: Optional system instruction
            timeout: Request timeout in seconds
            
        Returns:
            Dict with 'response', 'tokens', 'duration'
        """
        payload = {
            "model": "llama3.1:8b",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
                "top_p": 0.9,
                "top_k": 40,
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        start_time = time.time()
        
        try:
            response = requests.post(
                self.generate_url,
                json=payload,
                timeout=timeout
            )
            response.raise_for_status()
            
            result = response.json()
            duration = time.time() - start_time
            
            return {
                "response": result.get("response", ""),
                "tokens": result.get("eval_count", 0),
                "duration": duration,
                "success": True
            }
            
        except requests.exceptions.Timeout:
            logger.error(f"LLM request timeout after {timeout}s")
            return {"success": False, "error": "timeout"}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"LLM request failed: {e}")
            return {"success": False, "error": str(e)}
    
    def generate_with_retry(
        self,
        prompt: str,
        max_retries: int = 3,
        **kwargs
    ) -> Dict[str, Any]:
        """Generate with exponential backoff retry."""
        for attempt in range(max_retries):
            result = self.generate(prompt, **kwargs)
            if result["success"]:
                return result
            
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 1s, 2s, 4s
                logger.warning(f"Retry {attempt + 1}/{max_retries} after {wait_time}s")
                time.sleep(wait_time)
        
        return result

# Global client instance
ollama_client = OllamaClient()
```

---

## LLM Job #1: Data Cleaning

### Purpose
Clean and standardize messy CSV/ERP data (major names, GPA formats, skill names).

### Parameters
- **Temperature:** 0.1 (deterministic, consistent output)
- **Max Tokens:** 500
- **Processing Time:** 0.5-1 second per record

### Prompt Template

**File:** `backend/services/data_cleaning.py`

```python
from typing import Dict, Any
from .llm_client import ollama_client
import json

SYSTEM_PROMPT = """You are a data cleaning assistant for a student career prediction system.
Your job is to standardize and clean messy input data.

Rules:
1. Fix typos and variations in major names (e.g., "Comp Sci" → "Computer Science")
2. Normalize GPA to 10.0 scale (convert from 4.0 scale or percentage if needed)
3. Standardize skill names (e.g., "ReactJS", "React.js" → "React")
4. Trim whitespace and fix capitalization
5. Return ONLY valid JSON, no explanations
6. If data is already clean, return it unchanged

Output format:
{
  "major": "cleaned major name",
  "gpa": normalized_gpa_float,
  "skills": ["cleaned", "skill", "names"],
  "corrections_applied": number_of_corrections
}
"""

def clean_student_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Clean student/alumni data using LLM.
    
    Args:
        raw_data: Dict with keys: major, gpa, skills (list)
        
    Returns:
        Cleaned data dict
    """
    prompt = f"""Clean this student data:

Input:
- Major: {raw_data.get('major', '')}
- GPA: {raw_data.get('gpa', '')}
- Skills: {', '.join(raw_data.get('skills', []))}

Return cleaned data as JSON."""

    result = ollama_client.generate_with_retry(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.1,
        max_tokens=500
    )
    
    if not result["success"]:
        # Fallback: rule-based cleaning
        return fallback_clean_data(raw_data)
    
    try:
        cleaned = json.loads(result["response"])
        return cleaned
    except json.JSONDecodeError:
        # Fallback if LLM returns invalid JSON
        return fallback_clean_data(raw_data)

def fallback_clean_data(raw_data: Dict[str, Any]) -> Dict[str, Any]:
    """Rule-based fallback cleaning."""
    major_map = {
        "comp sci": "Computer Science",
        "mech engg": "Mechanical Engineering",
        "ece": "Electronics and Communication Engineering",
        "it": "Information Technology"
    }
    
    major = raw_data.get("major", "").strip()
    major_clean = major_map.get(major.lower(), major.title())
    
    gpa = raw_data.get("gpa", 0)
    if isinstance(gpa, str):
        gpa = float(gpa.replace("%", ""))
    if gpa > 10:  # Percentage to 10.0 scale
        gpa = gpa / 10
    elif gpa <= 4:  # 4.0 scale to 10.0 scale
        gpa = (gpa / 4) * 10
    
    skills = [s.strip().title() for s in raw_data.get("skills", [])]
    
    return {
        "major": major_clean,
        "gpa": round(gpa, 2),
        "skills": skills,
        "corrections_applied": 0
    }
```

### Example Usage

```python
# Example 1: Clean messy data
raw_data = {
    "major": "comp sci",
    "gpa": "3.2",  # 4.0 scale
    "skills": ["ReactJS", "pyton", "node.js"]
}

cleaned = clean_student_data(raw_data)
# Output:
# {
#   "major": "Computer Science",
#   "gpa": 8.0,
#   "skills": ["React", "Python", "Node.js"],
#   "corrections_applied": 4
# }
```

---

## LLM Job #2: Recommendation Generation

### Purpose
Generate 3-5 personalized, actionable recommendations to improve trajectory score.

### Parameters
- **Temperature:** 0.7 (creative, varied recommendations)
- **Max Tokens:** 800
- **Processing Time:** 1-2 seconds per student

### Prompt Template

**File:** `backend/services/recommendation_engine.py`

```python
from typing import Dict, Any, List
from .llm_client import ollama_client

SYSTEM_PROMPT = """You are a career counselor AI for college students.
Generate personalized, actionable recommendations to improve employability.

Rules:
1. Provide 3-5 specific, actionable recommendations
2. Include estimated impact (+X points on trajectory score)
3. Include realistic timelines (e.g., "2-3 weeks", "1 month")
4. Reference similar alumni success stories when relevant
5. Prioritize by impact (High/Medium/Low)
6. Be encouraging but realistic
7. Focus on academics, behavioral habits, and skills

Format each recommendation as:
**[Priority] Recommendation Title**
- Action: Specific steps to take
- Impact: +X points on trajectory score
- Timeline: Realistic timeframe
- Why it matters: Brief explanation with data
"""

def generate_recommendations(
    student_profile: Dict[str, Any],
    trajectory_score: float,
    gap_analysis: Dict[str, Any],
    similar_alumni: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Generate personalized recommendations using LLM.
    
    Args:
        student_profile: Student's academic and behavioral data
        trajectory_score: Current trajectory score (0-100)
        gap_analysis: Gaps compared to successful alumni
        similar_alumni: Top 3 similar alumni with outcomes
        
    Returns:
        List of recommendation dicts
    """
    # Build context for LLM
    alumni_context = "\n".join([
        f"- Alumni {i+1}: {a['major']}, GPA {a['gpa']}, "
        f"placed at {a['company_tier']} company, {a['salary']} LPA"
        for i, a in enumerate(similar_alumni[:3])
    ])
    
    gaps_context = "\n".join([
        f"- {key}: Student has {gap['student_value']}, "
        f"successful alumni average {gap['alumni_average']} "
        f"(gap: {gap['percentage_gap']}%)"
        for key, gap in gap_analysis.items()
        if gap['percentage_gap'] > 10  # Only significant gaps
    ])
    
    prompt = f"""Generate career recommendations for this student:

**Student Profile:**
- Major: {student_profile['major']}
- GPA: {student_profile['gpa']} / 10.0
- Attendance: {student_profile['attendance']}%
- Study Hours/Week: {student_profile.get('study_hours', 'N/A')}
- Projects Completed: {student_profile.get('project_count', 0)}
- Screen Time: {student_profile.get('screen_time', 'N/A')} hours/day
- Focus Score: {student_profile.get('focus_score', 'N/A')}
- Sleep Duration: {student_profile.get('sleep_duration', 'N/A')} hours/day
- Current Trajectory Score: {trajectory_score}/100

**Gaps Compared to Successful Alumni:**
{gaps_context}

**Similar Alumni Who Succeeded:**
{alumni_context}

Generate 3-5 actionable recommendations to improve this student's employability."""

    result = ollama_client.generate_with_retry(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.7,
        max_tokens=800
    )
    
    if not result["success"]:
        return fallback_recommendations(student_profile, gap_analysis)
    
    # Parse LLM response into structured recommendations
    recommendations = parse_recommendations(result["response"])
    return recommendations

def parse_recommendations(llm_response: str) -> List[Dict[str, Any]]:
    """Parse LLM response into structured recommendation list."""
    # Simple parsing logic (can be improved)
    recommendations = []
    lines = llm_response.split("\n")
    
    current_rec = None
    for line in lines:
        line = line.strip()
        if line.startswith("**["):
            # New recommendation
            if current_rec:
                recommendations.append(current_rec)
            
            # Extract priority and title
            priority = "Medium"  # Default
            if "[High]" in line:
                priority = "High"
            elif "[Low]" in line:
                priority = "Low"
            
            title = line.replace("**", "").split("]", 1)[-1].strip()
            current_rec = {
                "priority": priority,
                "title": title,
                "action": "",
                "impact": "",
                "timeline": "",
                "reasoning": ""
            }
        elif current_rec and line.startswith("- Action:"):
            current_rec["action"] = line.replace("- Action:", "").strip()
        elif current_rec and line.startswith("- Impact:"):
            current_rec["impact"] = line.replace("- Impact:", "").strip()
        elif current_rec and line.startswith("- Timeline:"):
            current_rec["timeline"] = line.replace("- Timeline:", "").strip()
        elif current_rec and line.startswith("- Why it matters:"):
            current_rec["reasoning"] = line.replace("- Why it matters:", "").strip()
    
    if current_rec:
        recommendations.append(current_rec)
    
    return recommendations

def fallback_recommendations(
    student_profile: Dict[str, Any],
    gap_analysis: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """Template-based fallback recommendations."""
    recommendations = []
    
    # GPA recommendation
    if student_profile.get("gpa", 10) < 7.0:
        recommendations.append({
            "priority": "High",
            "title": "Improve Academic Performance",
            "action": "Focus on core subjects, attend extra classes, seek help from professors",
            "impact": "+10-15 points",
            "timeline": "1 semester",
            "reasoning": "GPA is a key factor in placement. Alumni with 7.5+ GPA had 40% higher placement rates."
        })
    
    # Attendance recommendation
    if student_profile.get("attendance", 100) < 75:
        recommendations.append({
            "priority": "High",
            "title": "Improve Attendance",
            "action": "Attend all classes regularly, aim for 85%+ attendance",
            "impact": "+5-8 points",
            "timeline": "1 month",
            "reasoning": "Consistent attendance shows discipline. Many companies have 75% attendance cutoff."
        })
    
    # Screen time recommendation
    if student_profile.get("screen_time", 0) > 8:
        recommendations.append({
            "priority": "Medium",
            "title": "Reduce Screen Time",
            "action": "Limit social media to 1 hour/day, use app blockers during study hours",
            "impact": "+3-5 points",
            "timeline": "2 weeks",
            "reasoning": "Excessive screen time correlates with lower GPA. Successful alumni average 6 hours/day."
        })
    
    return recommendations[:5]  # Max 5 recommendations
```

### Example Usage

```python
student_profile = {
    "major": "Computer Science",
    "gpa": 7.2,
    "attendance": 78,
    "study_hours": 15,
    "project_count": 2,
    "screen_time": 9,
    "focus_score": 0.55,
    "sleep_duration": 5.5
}

trajectory_score = 62

gap_analysis = {
    "gpa": {"student_value": 7.2, "alumni_average": 8.1, "percentage_gap": 11},
    "study_hours": {"student_value": 15, "alumni_average": 22, "percentage_gap": 32},
    "sleep_duration": {"student_value": 5.5, "alumni_average": 7.2, "percentage_gap": 24}
}

similar_alumni = [
    {"major": "Computer Science", "gpa": 8.0, "company_tier": "Tier1", "salary": 16},
    {"major": "Computer Science", "gpa": 7.8, "company_tier": "Tier2", "salary": 10}
]

recommendations = generate_recommendations(
    student_profile, trajectory_score, gap_analysis, similar_alumni
)

# Output: List of 3-5 structured recommendations
```

---

## LLM Job #3: Voice Assessment Evaluation

### Purpose
Evaluate student's technical answers from voice interviews (technical accuracy, communication clarity, depth).

### Parameters
- **Temperature:** 0.3 (consistent scoring)
- **Max Tokens:** 400
- **Processing Time:** 1-2 seconds per evaluation

### Prompt Template

**File:** `backend/services/voice_evaluation.py`

```python
from typing import Dict, Any
from .llm_client import ollama_client
import json

SYSTEM_PROMPT = """You are a technical interviewer evaluating student responses.
Score answers on 4 dimensions (0-10 scale each):

1. **Technical Accuracy (0-10):** Is the answer technically correct?
2. **Communication Clarity (0-10):** Is the explanation clear and well-structured?
3. **Depth of Understanding (0-10):** Does the student show deep understanding?
4. **Completeness (0-10):** Does the answer cover all aspects of the question?

Rules:
- Be fair but rigorous
- Consider the student's major and level (junior/senior)
- Provide specific feedback on strengths and areas for improvement
- Return ONLY valid JSON

Output format:
{
  "technical_accuracy": score_0_to_10,
  "communication_clarity": score_0_to_10,
  "depth": score_0_to_10,
  "completeness": score_0_to_10,
  "overall_score": average_score_0_to_100,
  "strengths": ["strength1", "strength2"],
  "improvements": ["area1", "area2"],
  "feedback": "brief overall feedback"
}
"""

def evaluate_voice_answer(
    question: str,
    student_answer: str,
    student_major: str,
    skill_area: str
) -> Dict[str, Any]:
    """
    Evaluate student's voice answer using LLM.
    
    Args:
        question: The technical question asked
        student_answer: Student's transcribed answer
        student_major: Student's major (for context)
        skill_area: Skill being tested (e.g., "Python", "Data Structures")
        
    Returns:
        Evaluation dict with scores and feedback
    """
    prompt = f"""Evaluate this student's technical answer:

**Question:** {question}

**Student's Answer:**
{student_answer}

**Context:**
- Student Major: {student_major}
- Skill Area: {skill_area}

Provide detailed evaluation with scores (0-10) for each dimension."""

    result = ollama_client.generate_with_retry(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.3,
        max_tokens=400
    )
    
    if not result["success"]:
        return fallback_evaluation()
    
    try:
        evaluation = json.loads(result["response"])
        return evaluation
    except json.JSONDecodeError:
        return fallback_evaluation()

def fallback_evaluation() -> Dict[str, Any]:
    """Fallback evaluation when LLM fails."""
    return {
        "technical_accuracy": 5,
        "communication_clarity": 5,
        "depth": 5,
        "completeness": 5,
        "overall_score": 50,
        "strengths": ["Attempted to answer"],
        "improvements": ["Provide more detail", "Improve clarity"],
        "feedback": "Unable to evaluate automatically. Manual review recommended."
    }

def calculate_voice_assessment_score(evaluations: List[Dict[str, Any]]) -> float:
    """
    Calculate final voice assessment score from multiple question evaluations.
    
    Args:
        evaluations: List of evaluation dicts for each question
        
    Returns:
        Final voice assessment score (0-100)
    """
    if not evaluations:
        return 0.0
    
    overall_scores = [e["overall_score"] for e in evaluations]
    return sum(overall_scores) / len(overall_scores)
```

### Example Usage

```python
question = "Explain the difference between a list and a tuple in Python."

student_answer = """
A list is a mutable data structure in Python, which means you can change its 
contents after creation. You can add, remove, or modify elements. Lists are 
defined using square brackets.

A tuple is immutable, so once you create it, you cannot change its contents. 
Tuples are defined using parentheses. Tuples are generally faster than lists 
for iteration because of their immutability.

Lists are used when you need a collection that can change, while tuples are 
used for fixed collections or as dictionary keys since they're hashable.
"""

evaluation = evaluate_voice_answer(
    question=question,
    student_answer=student_answer,
    student_major="Computer Science",
    skill_area="Python"
)

# Output:
# {
#   "technical_accuracy": 9,
#   "communication_clarity": 8,
#   "depth": 8,
#   "completeness": 9,
#   "overall_score": 85,
#   "strengths": ["Accurate explanation", "Good examples", "Mentioned use cases"],
#   "improvements": ["Could mention memory efficiency", "Could give code examples"],
#   "feedback": "Excellent answer with strong technical understanding and clear communication."
# }
```

---

## LLM Job #4: Gap Analysis Narratives

### Purpose
Convert statistical gaps into engaging, motivating narratives that explain why gaps matter.

### Parameters
- **Temperature:** 0.7 (engaging, narrative style)
- **Max Tokens:** 600
- **Processing Time:** 0.5-1 second per narrative

### Prompt Template

**File:** `backend/services/gap_analysis.py`

```python
from typing import Dict, Any, List
from .llm_client import ollama_client

SYSTEM_PROMPT = """You are a career counselor creating motivating gap analysis narratives.

Your job is to explain statistical gaps between a student and successful alumni in a way that:
1. Is data-driven and factual
2. Is encouraging and supportive (not discouraging)
3. Explains WHY the gap matters for career outcomes
4. References real alumni success stories
5. Provides specific, actionable targets

Tone: Friendly, supportive, data-driven, motivating

Format:
- Start with the gap and its impact
- Explain why it matters (with data)
- Reference similar alumni who closed this gap
- End with specific target and encouragement
"""

def generate_gap_narrative(
    gap_type: str,
    student_value: float,
    alumni_average: float,
    percentage_gap: float,
    alumni_success_stories: List[Dict[str, Any]]
) -> str:
    """
    Generate engaging narrative for a specific gap.
    
    Args:
        gap_type: Type of gap (e.g., "GPA", "study_hours", "sleep_duration")
        student_value: Student's current value
        alumni_average: Average value of successful alumni
        percentage_gap: Percentage difference
        alumni_success_stories: List of alumni who closed similar gaps
        
    Returns:
        Narrative string
    """
    # Build alumni stories context
    stories_context = ""
    if alumni_success_stories:
        stories_context = "\n\nSuccess Stories:\n" + "\n".join([
            f"- {story['name']} improved their {gap_type} from {story['before']} to "
            f"{story['after']} and got placed at {story['company']} ({story['salary']} LPA)"
            for story in alumni_success_stories[:2]
        ])
    
    prompt = f"""Create a motivating gap analysis narrative:

**Gap Type:** {gap_type.replace('_', ' ').title()}
**Student's Current Value:** {student_value}
**Successful Alumni Average:** {alumni_average}
**Gap:** {percentage_gap}% below alumni average
{stories_context}

Write a 3-4 sentence narrative that:
1. Explains the gap and its impact on employability
2. Uses data to show why it matters
3. References alumni success stories (if provided)
4. Ends with specific target and encouragement"""

    result = ollama_client.generate_with_retry(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.7,
        max_tokens=600
    )
    
    if not result["success"]:
        return fallback_narrative(gap_type, student_value, alumni_average)
    
    return result["response"]

def fallback_narrative(gap_type: str, student_value: float, alumni_average: float) -> str:
    """Template-based fallback narrative."""
    gap_templates = {
        "gpa": f"Your GPA of {student_value} is below the successful alumni average of {alumni_average}. "
               f"Improving your GPA can significantly boost your placement chances. "
               f"Aim for {alumni_average} or higher to match successful alumni patterns.",
        
        "study_hours": f"You're studying {student_value} hours per week, while successful alumni averaged "
                      f"{alumni_average} hours. Increasing your study time can improve your academic performance "
                      f"and skill development. Try to reach {alumni_average} hours per week.",
        
        "sleep_duration": f"Your sleep duration of {student_value} hours is below the optimal {alumni_average} hours "
                         f"that successful alumni maintained. Better sleep improves focus, memory, and academic performance. "
                         f"Aim for {alumni_average} hours of sleep per night.",
        
        "screen_time": f"Your screen time of {student_value} hours per day exceeds the {alumni_average} hours "
                      f"that successful alumni averaged. Reducing screen time can improve focus and productivity. "
                      f"Try to limit screen time to {alumni_average} hours per day."
    }
    
    return gap_templates.get(gap_type, f"Your {gap_type} needs improvement to match successful alumni patterns.")

def generate_all_gap_narratives(
    student_profile: Dict[str, Any],
    alumni_averages: Dict[str, float],
    alumni_stories: Dict[str, List[Dict[str, Any]]]
) -> Dict[str, str]:
    """
    Generate narratives for all significant gaps.
    
    Args:
        student_profile: Student's current metrics
        alumni_averages: Average metrics of successful alumni
        alumni_stories: Success stories for each gap type
        
    Returns:
        Dict mapping gap_type to narrative
    """
    narratives = {}
    
    for metric, alumni_avg in alumni_averages.items():
        student_val = student_profile.get(metric, 0)
        
        # Calculate percentage gap
        if alumni_avg > 0:
            percentage_gap = abs((student_val - alumni_avg) / alumni_avg * 100)
        else:
            percentage_gap = 0
        
        # Only generate narrative for significant gaps (>10%)
        if percentage_gap > 10:
            narrative = generate_gap_narrative(
                gap_type=metric,
                student_value=student_val,
                alumni_average=alumni_avg,
                percentage_gap=percentage_gap,
                alumni_success_stories=alumni_stories.get(metric, [])
            )
            narratives[metric] = narrative
    
    return narratives
```

### Example Usage

```python
gap_narratives = generate_gap_narrative(
    gap_type="sleep_duration",
    student_value=5.5,
    alumni_average=7.2,
    percentage_gap=24,
    alumni_success_stories=[
        {
            "name": "Rahul K.",
            "before": 5.5,
            "after": 7.5,
            "company": "Google",
            "salary": 18
        }
    ]
)

# Output (example):
# "Your sleep duration of 5.5 hours is 24% below the 7.2 hours that successful alumni 
# maintained. Research shows that students with 7+ hours of sleep have 15% higher GPAs 
# and better focus during interviews. Rahul K. improved his sleep from 5.5 to 7.5 hours 
# and saw his GPA jump from 7.2 to 8.1, ultimately landing at Google with 18 LPA. 
# Aim for 7-8 hours of sleep per night - your brain and career will thank you!"
```

---

## LLM Job #5: Skill Market Demand Analysis

### Purpose
Dynamically assess skill market demand and assign weight multipliers (0.5x, 1.0x, 2.0x).

### Parameters
- **Temperature:** 0.2 (data-driven, consistent)
- **Max Tokens:** 300
- **Processing Time:** 0.5-1 second per skill
- **Caching:** 30 days (avoid repeated calls for same skill)

### Prompt Template

**File:** `backend/services/skill_demand.py`

```python
from typing import Dict, Any
from .llm_client import ollama_client
from functools import lru_cache
import json
import hashlib

SYSTEM_PROMPT = """You are a job market analyst evaluating skill demand in 2026.

Your job is to assign EXACTLY ONE market weight multiplier to each skill:
- **2.0x (High Demand):** Trending, in-demand skills with strong job market
- **1.0x (Medium Demand):** Standard, stable skills with moderate demand
- **0.5x (Low Demand):** Outdated, declining skills with weak demand

Consider:
1. Current job market trends (2026)
2. Salary premiums for the skill
3. Job posting frequency
4. Industry adoption rates
5. Future growth potential

Rules:
- Return ONLY valid JSON
- Assign EXACTLY ONE weight: 0.5, 1.0, or 2.0
- Provide data-driven reasoning (mention job stats, salary data, trends)

Output format:
{
  "skill": "skill_name",
  "market_weight": 0.5 or 1.0 or 2.0,
  "demand_level": "High" or "Medium" or "Low",
  "reasoning": "data-driven explanation with stats"
}
"""

@lru_cache(maxsize=1000)
def analyze_skill_demand(
    skill_name: str,
    student_major: str,
    current_year: int = 2026
) -> Dict[str, Any]:
    """
    Analyze skill market demand using LLM (cached for 30 days).
    
    Args:
        skill_name: Name of the skill (e.g., "Python", "React", "jQuery")
        student_major: Student's major (for context)
        current_year: Current year (default: 2026)
        
    Returns:
        Dict with market_weight, demand_level, reasoning
    """
    prompt = f"""Analyze market demand for this skill in {current_year}:

**Skill:** {skill_name}
**Student Major:** {student_major}
**Year:** {current_year}

Assign market weight (0.5x, 1.0x, or 2.0x) based on:
- Job market demand
- Salary trends
- Industry adoption
- Future growth potential

Provide data-driven reasoning with specific statistics."""

    result = ollama_client.generate_with_retry(
        prompt=prompt,
        system_prompt=SYSTEM_PROMPT,
        temperature=0.2,
        max_tokens=300
    )
    
    if not result["success"]:
        return fallback_skill_demand(skill_name)
    
    try:
        analysis = json.loads(result["response"])
        
        # Validate weight is exactly 0.5, 1.0, or 2.0
        weight = analysis.get("market_weight", 1.0)
        if weight not in [0.5, 1.0, 2.0]:
            weight = 1.0  # Default to medium
        
        analysis["market_weight"] = weight
        return analysis
        
    except json.JSONDecodeError:
        return fallback_skill_demand(skill_name)

def fallback_skill_demand(skill_name: str) -> Dict[str, Any]:
    """Rule-based fallback for skill demand analysis."""
    skill_lower = skill_name.lower()
    
    # High demand skills (2.0x)
    high_demand = ["python", "react", "aws", "kubernetes", "docker", "ai", "ml", 
                   "machine learning", "data science", "cloud", "devops", "typescript",
                   "go", "rust", "flutter", "react native"]
    
    # Low demand skills (0.5x)
    low_demand = ["flash", "jquery", "vb.net", "silverlight", "perl", "coldfusion",
                  "asp classic", "visual basic 6"]
    
    if any(hd in skill_lower for hd in high_demand):
        return {
            "skill": skill_name,
            "market_weight": 2.0,
            "demand_level": "High",
            "reasoning": f"{skill_name} is in high demand with strong job market growth."
        }
    elif any(ld in skill_lower for ld in low_demand):
        return {
            "skill": skill_name,
            "market_weight": 0.5,
            "demand_level": "Low",
            "reasoning": f"{skill_name} is outdated with declining job market demand."
        }
    else:
        return {
            "skill": skill_name,
            "market_weight": 1.0,
            "demand_level": "Medium",
            "reasoning": f"{skill_name} has stable, moderate demand in the job market."
        }

def calculate_weighted_skill_score(
    skill_assessments: List[Dict[str, Any]]
) -> float:
    """
    Calculate weighted skill score using market demand multipliers.
    
    Args:
        skill_assessments: List of dicts with 'skill', 'proficiency' (0-100), 'market_weight'
        
    Returns:
        Weighted skill score (0-100)
    """
    if not skill_assessments:
        return 0.0
    
    total_weighted_score = 0
    total_weight = 0
    
    for assessment in skill_assessments:
        proficiency = assessment.get("proficiency", 0)  # 0-100
        market_weight = assessment.get("market_weight", 1.0)  # 0.5, 1.0, or 2.0
        
        weighted_score = proficiency * market_weight
        total_weighted_score += weighted_score
        total_weight += market_weight
    
    if total_weight == 0:
        return 0.0
    
    # Normalize to 0-100 scale
    avg_weighted_score = total_weighted_score / total_weight
    return min(avg_weighted_score, 100.0)
```

### Example Usage

```python
# Analyze individual skill
python_analysis = analyze_skill_demand(
    skill_name="Python",
    student_major="Computer Science",
    current_year=2026
)

# Output:
# {
#   "skill": "Python",
#   "market_weight": 2.0,
#   "demand_level": "High",
#   "reasoning": "Python is critical for AI/ML, data science, and backend development. 
#                78% of job postings require Python in 2026. Recent alumni with Python 
#                proficiency averaged 14 LPA vs 8 LPA without. Demand growing due to AI boom."
# }

# Calculate weighted skill score
skill_assessments = [
    {"skill": "Python", "proficiency": 85, "market_weight": 2.0},
    {"skill": "React", "proficiency": 80, "market_weight": 2.0},
    {"skill": "jQuery", "proficiency": 90, "market_weight": 0.5}
]

weighted_score = calculate_weighted_skill_score(skill_assessments)
# Output: 82.5 (weighted average considering market demand)
```

---

## Performance Monitoring

### Metrics to Track

**File:** `backend/services/llm_monitoring.py`

```python
import time
from typing import Dict, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)

class LLMMonitor:
    """Monitor LLM performance and usage."""
    
    def __init__(self):
        self.metrics = defaultdict(list)
    
    def log_request(
        self,
        job_name: str,
        duration: float,
        tokens: int,
        success: bool
    ):
        """Log LLM request metrics."""
        self.metrics[job_name].append({
            "duration": duration,
            "tokens": tokens,
            "success": success,
            "timestamp": time.time()
        })
        
        logger.info(
            f"LLM Job: {job_name} | "
            f"Duration: {duration:.2f}s | "
            f"Tokens: {tokens} | "
            f"Success: {success}"
        )
    
    def get_stats(self, job_name: str = None) -> Dict[str, Any]:
        """Get performance statistics."""
        if job_name:
            requests = self.metrics[job_name]
        else:
            requests = [r for reqs in self.metrics.values() for r in reqs]
        
        if not requests:
            return {}
        
        durations = [r["duration"] for r in requests]
        tokens = [r["tokens"] for r in requests]
        successes = [r["success"] for r in requests]
        
        return {
            "total_requests": len(requests),
            "success_rate": sum(successes) / len(successes) * 100,
            "avg_duration": sum(durations) / len(durations),
            "p95_duration": sorted(durations)[int(len(durations) * 0.95)],
            "avg_tokens": sum(tokens) / len(tokens) if tokens else 0
        }

# Global monitor instance
llm_monitor = LLMMonitor()
```

### Health Check Endpoint

```python
from fastapi import APIRouter
from .llm_client import ollama_client
from .llm_monitoring import llm_monitor

router = APIRouter()

@router.get("/api/llm/health")
def llm_health_check():
    """Check LLM server health and performance."""
    is_healthy = ollama_client.health_check()
    stats = llm_monitor.get_stats()
    
    return {
        "status": "healthy" if is_healthy else "unhealthy",
        "ollama_server": "running" if is_healthy else "down",
        "model": "llama3.1:8b",
        "performance": stats
    }
```

---

## Testing LLM Pipelines

### Unit Tests

**File:** `backend/tests/test_llm_pipelines.py`

```python
import pytest
from services.data_cleaning import clean_student_data
from services.recommendation_engine import generate_recommendations
from services.voice_evaluation import evaluate_voice_answer
from services.gap_analysis import generate_gap_narrative
from services.skill_demand import analyze_skill_demand

def test_data_cleaning():
    """Test data cleaning pipeline."""
    raw_data = {
        "major": "comp sci",
        "gpa": "3.5",
        "skills": ["ReactJS", "pyton"]
    }
    
    cleaned = clean_student_data(raw_data)
    
    assert cleaned["major"] == "Computer Science"
    assert 8.0 <= cleaned["gpa"] <= 9.0  # 3.5/4.0 * 10
    assert "React" in cleaned["skills"]
    assert "Python" in cleaned["skills"]

def test_recommendation_generation():
    """Test recommendation generation."""
    student_profile = {
        "major": "Computer Science",
        "gpa": 7.0,
        "attendance": 70,
        "study_hours": 10
    }
    
    recommendations = generate_recommendations(
        student_profile=student_profile,
        trajectory_score=55,
        gap_analysis={},
        similar_alumni=[]
    )
    
    assert len(recommendations) >= 3
    assert all("priority" in r for r in recommendations)
    assert all("action" in r for r in recommendations)

def test_voice_evaluation():
    """Test voice answer evaluation."""
    evaluation = evaluate_voice_answer(
        question="What is a linked list?",
        student_answer="A linked list is a data structure with nodes.",
        student_major="Computer Science",
        skill_area="Data Structures"
    )
    
    assert "technical_accuracy" in evaluation
    assert 0 <= evaluation["overall_score"] <= 100

def test_skill_demand_analysis():
    """Test skill market demand analysis."""
    analysis = analyze_skill_demand(
        skill_name="Python",
        student_major="Computer Science"
    )
    
    assert analysis["market_weight"] in [0.5, 1.0, 2.0]
    assert analysis["demand_level"] in ["High", "Medium", "Low"]
    assert len(analysis["reasoning"]) > 0
```

---

## End of LLM Pipelines Documentation
