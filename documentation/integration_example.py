"""
Trajectory Engine - LLM Integration Example
Shows how to use the fine-tuned model in your application
"""

import requests
import json
from typing import Dict, Any

class TrajectoryEngineLLM:
    """Wrapper for Trajectory Engine LLM"""
    
    def __init__(self, model_name: str = "trajectory-engine:latest", 
                 base_url: str = "http://localhost:11434"):
        self.model_name = model_name
        self.base_url = base_url
        self.api_url = f"{base_url}/api/generate"
    
    def analyze_student(self, student_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze student profile and return trajectory prediction
        
        Args:
            student_data: Dictionary containing student information
            
        Returns:
            Dictionary with analysis results
        """
        
        # Format student data into prompt
        prompt = self._format_student_prompt(student_data)
        
        # Call LLM
        response = self._call_llm(prompt)
        
        # Parse response
        analysis = self._parse_response(response)
        
        return analysis
    
    def _format_student_prompt(self, data: Dict[str, Any]) -> str:
        """Format student data into analysis prompt"""
        
        prompt = f"""Analyze this student profile and predict their employability trajectory:

**Student Profile:**
- Name: {data.get('name', 'Unknown')}
- Major: {data.get('major', 'Unknown')} (Semester {data.get('semester', 'N/A')})
- GPA: {data.get('gpa', 'N/A')}/10 ({data.get('gpa_trend', 'Unknown')})
- Attendance: {data.get('attendance', 'N/A')}%
- Backlogs: {data.get('backlogs', 0)}

**Skills & Experience:**
- Programming: {data.get('programming_languages', 'N/A')}
- Strongest: {data.get('strongest_skill', 'N/A')}
- Projects: {data.get('projects_count', 0)} ({data.get('project_types', 'N/A')})
- Deployed: {data.get('deployed_project', 'N/A')}
- Internship: {data.get('internship', 'N/A')} ({data.get('internship_months', 0)} months)
- Problem Solving: {data.get('problem_solving', 'N/A')}/5
- Communication: {data.get('communication', 'N/A')}/5

**Behavioral Patterns:**
- Study: {data.get('study_hours', 'N/A')}h/day, Practice: {data.get('practice_hours', 'N/A')}h/day
- Screen Time: {data.get('screen_time', 'N/A')}h/day (Social: {data.get('social_media_time', 'N/A')}h)
- Sleep: {data.get('sleep_hours', 'N/A')}h ({data.get('sleep_schedule', 'Unknown')})
- Distraction Level: {data.get('distraction_level', 'N/A')}/5
- Consistency: {data.get('consistency', 'N/A')}/5

**Mental & Career:**
- Career Clarity: {data.get('career_clarity', 'N/A')}/5
- Confidence: {data.get('confidence', 'N/A')}/5
- Interview Fear: {data.get('interview_fear', 'N/A')}/5
- Placement Prep: {data.get('placement_prep', 'N/A')}

**Self-Assessment:**
- Strength: {data.get('strength', 'N/A')}
- Weakness: {data.get('weakness', 'N/A')}
- Wants to improve: {data.get('habit_to_improve', 'N/A')}
- Blockers: {data.get('blockers', 'N/A')}

Provide a comprehensive employability analysis."""
        
        return prompt
    
    def _call_llm(self, prompt: str, stream: bool = False) -> str:
        """Call Ollama API"""
        
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": stream,
            "options": {
                "temperature": 0.3,
                "num_ctx": 4096
            }
        }
        
        try:
            response = requests.post(self.api_url, json=payload)
            response.raise_for_status()
            
            if stream:
                # Handle streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        data = json.loads(line)
                        full_response += data.get('response', '')
                return full_response
            else:
                # Handle non-streaming response
                result = response.json()
                return result.get('response', '')
        
        except requests.exceptions.RequestException as e:
            print(f"❌ Error calling LLM: {e}")
            return ""
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """Parse LLM response into structured data"""
        
        # Basic parsing - extract key information
        analysis = {
            'raw_response': response,
            'trajectory_score': None,
            'academic_score': None,
            'behavioral_score': None,
            'skills_score': None,
            'placement_likelihood': None,
            'strengths': [],
            'improvements': [],
            'recommendations': []
        }
        
        # Extract trajectory score
        if "Overall Score:" in response:
            try:
                score_line = [l for l in response.split('\n') if 'Overall Score:' in l][0]
                score_str = score_line.split(':')[1].split('/')[0].strip()
                analysis['trajectory_score'] = float(score_str)
            except:
                pass
        
        # Extract component scores
        for component in ['Academic', 'Behavioral', 'Skills']:
            if f"{component} Performance:" in response or f"{component} Patterns:" in response:
                try:
                    lines = [l for l in response.split('\n') if component in l and '/1.00' in l]
                    if lines:
                        score_str = lines[0].split(':')[1].split('/')[0].strip()
                        analysis[f'{component.lower()}_score'] = float(score_str)
                except:
                    pass
        
        # Extract placement likelihood
        if "Placement Likelihood:" in response:
            try:
                likelihood_line = [l for l in response.split('\n') if 'Placement Likelihood:' in l][0]
                analysis['placement_likelihood'] = likelihood_line.split(':')[1].strip()
            except:
                pass
        
        # Extract strengths (lines starting with "- " under "Key Strengths")
        if "Key Strengths:" in response:
            try:
                strengths_section = response.split("Key Strengths:")[1].split("**")[0]
                analysis['strengths'] = [
                    line.strip('- ').strip() 
                    for line in strengths_section.split('\n') 
                    if line.strip().startswith('-')
                ]
            except:
                pass
        
        # Extract improvements
        if "Areas for Improvement:" in response or "Improvement:" in response:
            try:
                improvements_section = response.split("Improvement:")[1].split("**")[0]
                analysis['improvements'] = [
                    line.strip('- ').strip() 
                    for line in improvements_section.split('\n') 
                    if line.strip().startswith('-')
                ]
            except:
                pass
        
        # Extract recommendations
        if "Actionable Recommendations:" in response or "Recommendations:" in response:
            try:
                recs_section = response.split("Recommendations:")[1].split("**")[0]
                analysis['recommendations'] = [
                    line.strip('0123456789.- ').strip() 
                    for line in recs_section.split('\n') 
                    if line.strip() and any(c.isalpha() for c in line)
                ]
            except:
                pass
        
        return analysis


# Example usage
def example_usage():
    """Example of how to use the TrajectoryEngineLLM"""
    
    print("🚀 Trajectory Engine LLM - Integration Example\n")
    
    # Initialize LLM
    llm = TrajectoryEngineLLM(model_name="trajectory-engine:latest-enhanced")
    
    # Example student data
    student = {
        'name': 'Arun Prakash Pattar',
        'major': 'Computer Science',
        'semester': 7,
        'gpa': 8.6,
        'gpa_trend': 'Stable',
        'attendance': 90,
        'backlogs': 0,
        'programming_languages': 'Python, Java, HTML/CSS, Machine Learning, Data Analysis',
        'strongest_skill': 'Machine learning',
        'projects_count': 5,
        'project_types': 'Academic, Personal',
        'deployed_project': 'Yes',
        'internship': 'Yes',
        'internship_months': 3,
        'problem_solving': 2,
        'communication': 4,
        'study_hours': 3,
        'practice_hours': 1,
        'screen_time': 6,
        'social_media_time': 2,
        'sleep_hours': 8,
        'sleep_schedule': 'Irregular',
        'distraction_level': 3,
        'consistency': 3,
        'career_clarity': 2,
        'confidence': 3,
        'interview_fear': 4,
        'placement_prep': 'Yes',
        'strength': 'good learner',
        'weakness': 'Consistent solving a single problem',
        'habit_to_improve': 'Build up consistency',
        'blockers': 'My laziness, and commitments for other works'
    }
    
    print("📊 Analyzing student profile...\n")
    
    # Analyze student
    analysis = llm.analyze_student(student)
    
    # Display results
    print("=" * 60)
    print("ANALYSIS RESULTS")
    print("=" * 60)
    print()
    
    if analysis['trajectory_score']:
        print(f"🎯 Trajectory Score: {analysis['trajectory_score']:.2f}/1.00")
    
    if analysis['placement_likelihood']:
        print(f"📈 Placement Likelihood: {analysis['placement_likelihood']}")
    
    print()
    
    if analysis['academic_score']:
        print(f"📚 Academic: {analysis['academic_score']:.2f}")
    if analysis['behavioral_score']:
        print(f"🧠 Behavioral: {analysis['behavioral_score']:.2f}")
    if analysis['skills_score']:
        print(f"💻 Skills: {analysis['skills_score']:.2f}")
    
    print()
    
    if analysis['strengths']:
        print("✅ Key Strengths:")
        for strength in analysis['strengths']:
            print(f"  - {strength}")
        print()
    
    if analysis['improvements']:
        print("⚠️ Areas for Improvement:")
        for improvement in analysis['improvements']:
            print(f"  - {improvement}")
        print()
    
    if analysis['recommendations']:
        print("💡 Recommendations:")
        for i, rec in enumerate(analysis['recommendations'], 1):
            print(f"  {i}. {rec}")
        print()
    
    print("=" * 60)
    print("\n📄 Full Response:\n")
    print(analysis['raw_response'])


if __name__ == "__main__":
    example_usage()
