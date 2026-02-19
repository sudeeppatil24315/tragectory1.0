"""
Trajectory Engine - LLM Training Data Preparation
Converts student CSV data into LLM training format (JSONL)
"""

import csv
import json
import math
from typing import Dict, List, Any

def normalize_standard(value: float, min_val: float, max_val: float) -> float:
    """Higher is better normalization"""
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)

def normalize_inverse(value: float, min_val: float, max_val: float) -> float:
    """Lower is better normalization (inverted)"""
    if max_val == min_val:
        return 0.5
    return 1 - ((value - min_val) / (max_val - min_val))

def sigmoid_transform(x: float, midpoint: float = 0.5, steepness: float = 10) -> float:
    """Non-linear sigmoid transformation"""
    return 1 / (1 + math.exp(-steepness * (x - midpoint)))

def calculate_grit_score(data: Dict) -> float:
    """Calculate grit from behavioral patterns"""
    # Factors: consistency, problem solving, projects, study hours
    consistency = float(data.get('Consistency Level (1–5)', 3)) / 5.0
    problem_solving = float(data.get('Problem Solving Ability (1–5)', 3)) / 5.0
    projects = min(float(data.get('Number of Projects Completed', 0)) / 10.0, 1.0)
    study_hours = min(float(data.get('Study hours per day', 0)) / 8.0, 1.0)
    
    # Weighted grit score
    grit = (0.3 * consistency + 0.3 * problem_solving + 0.2 * projects + 0.2 * study_hours)
    return grit

def parse_student_data(csv_file: str) -> List[Dict[str, Any]]:
    """Parse CSV and extract structured student data"""
    students = []
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f) 
        for row in reader:
            student = {
                'name': row['Full Name'],
                'email': row['Email Address'],
                'major': row['Major / Branch'],
                'semester': int(row['Current Semester']),
                'college': row['College Name'],
                
                # Academic metrics
                'gpa': float(row['Current GPA (0–10)']),
                'gpa_trend': row['GPA Trend Over Last Semesters'],
                'attendance': float(row['Average Attendance Percentage']),
                'internal_marks': float(row['Average Internal Marks (0–100)']),
                'backlogs': int(row['Number of Backlogs']),
                
                # Skills
                'programming_languages': row['Programming Languages Select all that apply)'],
                'strongest_skill': row['Strongest Technical Skill'],
                'problem_solving': int(row['Problem Solving Ability (1–5)']),
                'communication': int(row['Communication Skill (1–5)']),
                'teamwork': int(row['Teamwork Ability (1–5)']),
                
                # Projects & Experience
                'projects_count': int(row['Number of Projects Completed']),
                'project_types': row['Project Types (Select all that apply)'],
                'deployed_project': row['Have you deployed a project?'],
                'internship': row['Internship experience?'],
                'internship_months': row['Internship duration in months'] if row['Internship duration in months'] else '0',
                
                # Behavioral patterns
                'study_hours': float(row['Study hours per day']),
                'practice_hours': float(row['Technical Knowledge practice hours per day']),
                'screen_time': float(row['Average daily screen time (hours)']) if row['Average daily screen time (hours)'] else 6.0,
                'social_media_time': float(row['Daily social media time (hours)']) if row['Daily social media time (hours)'] else 2.0,
                'learning_time': float(row['Daily learning app/video time (hours)']) if row['Daily learning app/video time (hours)'] else 2.0,
                'entertainment_time': float(row['Daily entertainment time (hours)']) if row['Daily entertainment time (hours)'] else 2.0,
                'sleep_hours': float(row['Average sleep hours']) if row['Average sleep hours'] else 7.0,
                'sleep_schedule': row['Sleep schedule'] if row['Sleep schedule'] else 'Irregular',
                'phone_while_studying': row['Do you use phone while studying?'],
                'distraction_level': int(row['Distraction level while studying (1–5)']),
                
                # Mental & Career
                'consistency': int(row['Consistency Level (1–5)']),
                'mental_exhaustion': row['Mental exhaustion often?'],
                'career_clarity': int(row['Career clarity level (1–5)']),
                'career_path_chosen': row['Have you chosen a career path?'],
                'placement_prep': row['Daily placement preparation?'],
                'interview_fear': int(row['Interview fear level (1–5)']),
                'confidence': int(row['Confidence level (1–5)']),
                
                # Placement
                'placement_status': row['Placement status '],
                'placement_attempts': row['Number of placement attempts'],
                
                # Self-assessment
                'strength': row['Biggest strength'],
                'weakness': row['Biggest weakness'],
                'habit_to_improve': row['One habit you want to improve'],
                'blockers': row['What holds you back the most']
            }
            students.append(student)
    
    return students

def calculate_trajectory_components(student: Dict) -> Dict[str, float]:
    """Calculate normalized trajectory components using optimal formulas"""
    
    # === ACADEMIC COMPONENT (25% for CS major) ===
    gpa_norm = normalize_standard(student['gpa'], 0, 10)
    gpa_sigmoid = sigmoid_transform(gpa_norm, midpoint=0.7, steepness=8)
    
    attendance_norm = normalize_standard(student['attendance'], 0, 100)
    internal_norm = normalize_standard(student['internal_marks'], 0, 100)
    backlogs_norm = normalize_inverse(student['backlogs'], 0, 5)
    
    academic_score = (0.5 * gpa_sigmoid + 0.25 * attendance_norm + 
                     0.15 * internal_norm + 0.1 * backlogs_norm)
    
    # === BEHAVIORAL COMPONENT (35% for CS major) ===
    study_norm = normalize_standard(student['study_hours'], 0, 8)
    practice_norm = normalize_standard(student['practice_hours'], 0, 6)
    
    # Inverse normalization for negative behaviors
    screen_time_norm = normalize_inverse(student['screen_time'], 0, 12)
    social_media_norm = normalize_inverse(student['social_media_time'], 0, 6)
    distraction_norm = normalize_inverse(student['distraction_level'], 1, 5)
    
    # Sleep quality (7-8 hours is optimal)
    sleep_optimal = 1 - abs(student['sleep_hours'] - 7.5) / 7.5
    
    # Grit calculation
    grit_score = calculate_grit_score(student)
    
    behavioral_score = (0.2 * study_norm + 0.15 * practice_norm + 
                       0.15 * screen_time_norm + 0.1 * social_media_norm +
                       0.15 * distraction_norm + 0.1 * sleep_optimal + 
                       0.15 * grit_score)
    
    # === SKILLS COMPONENT (40% for CS major) ===
    # Count programming languages
    lang_count = len([l for l in student['programming_languages'].split(',') if l.strip()])
    lang_norm = min(lang_count / 8.0, 1.0)  # 8+ languages = max score
    
    problem_solving_norm = normalize_standard(student['problem_solving'], 1, 5)
    communication_norm = normalize_standard(student['communication'], 1, 5)
    teamwork_norm = normalize_standard(student['teamwork'], 1, 5)
    
    # Projects with deployment bonus
    projects_norm = min(student['projects_count'] / 10.0, 1.0)
    deployment_bonus = 0.2 if student['deployed_project'] == 'Yes' else 0
    
    # Internship experience
    internship_bonus = 0.15 if student['internship'] == 'Yes' else 0
    
    # Career readiness
    career_clarity_norm = normalize_standard(student['career_clarity'], 1, 5)
    confidence_norm = normalize_standard(student['confidence'], 1, 5)
    interview_fear_norm = normalize_inverse(student['interview_fear'], 1, 5)
    
    skills_score = (0.15 * lang_norm + 0.15 * problem_solving_norm +
                   0.1 * communication_norm + 0.1 * teamwork_norm +
                   0.15 * projects_norm + deployment_bonus + internship_bonus +
                   0.1 * career_clarity_norm + 0.1 * confidence_norm +
                   0.05 * interview_fear_norm)
    
    return {
        'academic': academic_score,
        'behavioral': behavioral_score,
        'skills': skills_score,
        'grit': grit_score,
        'gpa_sigmoid': gpa_sigmoid,
        'study_hours_norm': study_norm,
        'screen_time_norm': screen_time_norm,
        'projects_norm': projects_norm
    }

def calculate_trajectory_score(components: Dict[str, float], major: str = "Computer Science") -> float:
    """Calculate final trajectory score with major-specific weights"""
    
    # Major-specific weights (CS: behavior-heavy, skills-heavy)
    if major == "Computer Science":
        weights = {'academic': 0.25, 'behavioral': 0.35, 'skills': 0.40}
    else:
        weights = {'academic': 0.33, 'behavioral': 0.33, 'skills': 0.34}
    
    trajectory = (weights['academic'] * components['academic'] +
                 weights['behavioral'] * components['behavioral'] +
                 weights['skills'] * components['skills'])
    
    return trajectory

def generate_training_prompt(student: Dict, components: Dict, trajectory: float) -> str:
    """Generate training prompt for LLM"""
    
    prompt = f"""Analyze this student profile and predict their employability trajectory:

**Student Profile:**
- Name: {student['name']}
- Major: {student['major']} (Semester {student['semester']})
- GPA: {student['gpa']}/10 ({student['gpa_trend']})
- Attendance: {student['attendance']}%
- Backlogs: {student['backlogs']}

**Skills & Experience:**
- Programming: {student['programming_languages']}
- Strongest: {student['strongest_skill']}
- Projects: {student['projects_count']} ({student['project_types']})
- Deployed: {student['deployed_project']}
- Internship: {student['internship']} ({student['internship_months']} months)
- Problem Solving: {student['problem_solving']}/5
- Communication: {student['communication']}/5

**Behavioral Patterns:**
- Study: {student['study_hours']}h/day, Practice: {student['practice_hours']}h/day
- Screen Time: {student['screen_time']}h/day (Social: {student['social_media_time']}h)
- Sleep: {student['sleep_hours']}h ({student['sleep_schedule']})
- Distraction Level: {student['distraction_level']}/5
- Consistency: {student['consistency']}/5

**Mental & Career:**
- Career Clarity: {student['career_clarity']}/5
- Confidence: {student['confidence']}/5
- Interview Fear: {student['interview_fear']}/5
- Placement Prep: {student['placement_prep']}

**Self-Assessment:**
- Strength: {student['strength']}
- Weakness: {student['weakness']}
- Wants to improve: {student['habit_to_improve']}
- Blockers: {student['blockers']}

Provide a comprehensive employability analysis."""

    return prompt

def generate_training_response(student: Dict, components: Dict, trajectory: float) -> str:
    """Generate expected LLM response for training"""
    
    # Determine trajectory category
    if trajectory >= 0.80:
        category = "Excellent"
        placement_likelihood = "Very High (85-95%)"
    elif trajectory >= 0.70:
        category = "Strong"
        placement_likelihood = "High (70-85%)"
    elif trajectory >= 0.60:
        category = "Good"
        placement_likelihood = "Moderate (55-70%)"
    elif trajectory >= 0.50:
        category = "Fair"
        placement_likelihood = "Below Average (40-55%)"
    else:
        category = "Needs Improvement"
        placement_likelihood = "Low (25-40%)"
    
    response = f"""**TRAJECTORY ANALYSIS**

**Overall Score: {trajectory:.2f}/1.00 ({category})**

**Component Breakdown:**
- Academic Performance: {components['academic']:.2f}/1.00 ({components['academic']*100:.0f}%)
- Behavioral Patterns: {components['behavioral']:.2f}/1.00 ({components['behavioral']*100:.0f}%)
- Skills & Experience: {components['skills']:.2f}/1.00 ({components['skills']*100:.0f}%)
- Grit Score: {components['grit']:.2f}/1.00

**Weighted Contribution (CS Major: 25% Academic, 35% Behavioral, 40% Skills):**
- Academic: {components['academic'] * 0.25:.3f}
- Behavioral: {components['behavioral'] * 0.35:.3f}
- Skills: {components['skills'] * 0.40:.3f}

**Placement Likelihood: {placement_likelihood}**

**Key Strengths:**
"""
    
    # Identify top 3 strengths
    strengths = []
    if components['academic'] >= 0.75:
        strengths.append(f"- Strong academic foundation (GPA: {student['gpa']}/10)")
    if components['grit'] >= 0.70:
        strengths.append(f"- High grit and consistency (Score: {components['grit']:.2f})")
    if student['projects_count'] >= 4:
        strengths.append(f"- Extensive project experience ({student['projects_count']} projects)")
    if student['internship'] == 'Yes':
        strengths.append(f"- Real-world internship experience")
    if components['study_hours_norm'] >= 0.60:
        strengths.append(f"- Dedicated study routine ({student['study_hours']}h/day)")
    
    response += '\n'.join(strengths[:3]) + "\n\n**Areas for Improvement:**\n"
    
    # Identify top 3 gaps
    gaps = []
    if components['screen_time_norm'] < 0.50:
        gaps.append(f"- High screen time ({student['screen_time']}h/day) - reduce by 2-3 hours")
    if student['distraction_level'] >= 3:
        gaps.append(f"- Distraction management (Level {student['distraction_level']}/5) - implement focus techniques")
    if student['interview_fear'] >= 4:
        gaps.append(f"- Interview anxiety (Level {student['interview_fear']}/5) - practice mock interviews")
    if student['consistency'] <= 2:
        gaps.append(f"- Low consistency (Level {student['consistency']}/5) - build daily habits")
    if student['career_clarity'] <= 2:
        gaps.append(f"- Career clarity (Level {student['career_clarity']}/5) - explore career paths")
    if components['behavioral'] < 0.60:
        gaps.append(f"- Behavioral patterns need optimization - focus on study habits")
    
    response += '\n'.join(gaps[:3]) + "\n\n**Actionable Recommendations:**\n"
    
    # Generate 3-5 specific recommendations
    recommendations = []
    if student['screen_time'] > 6:
        recommendations.append("1. Reduce screen time to 4-5 hours/day using app blockers")
    if student['study_hours'] < 4:
        recommendations.append(f"2. Increase study hours from {student['study_hours']}h to 5-6h/day")
    if student['projects_count'] < 3:
        recommendations.append("3. Build 2-3 more portfolio projects with deployment")
    if student['placement_prep'] == 'No':
        recommendations.append("4. Start daily placement prep (DSA + system design)")
    if student['communication'] <= 3:
        recommendations.append("5. Join communication workshops or Toastmasters")
    
    response += '\n'.join(recommendations[:5])
    
    response += f"\n\n**30-Day Projection:**\nIf current patterns continue: {trajectory:.2f} → {min(trajectory + 0.05, 1.0):.2f}\n"
    response += f"With recommended improvements: {trajectory:.2f} → {min(trajectory + 0.15, 1.0):.2f}"
    
    return response

def create_training_jsonl(students: List[Dict], output_file: str = "training_data.jsonl"):
    """Create JSONL training file for LLM fine-tuning"""
    
    training_examples = []
    
    for student in students:
        # Calculate trajectory
        components = calculate_trajectory_components(student)
        trajectory = calculate_trajectory_score(components, student['major'])
        
        # Generate prompt and response
        prompt = generate_training_prompt(student, components, trajectory)
        response = generate_training_response(student, components, trajectory)
        
        # Create training example
        example = {
            "messages": [
                {"role": "system", "content": "You are an expert career counselor and data scientist specializing in student employability prediction. You analyze student profiles using the Trajectory Engine methodology and provide actionable insights."},
                {"role": "user", "content": prompt},
                {"role": "assistant", "content": response}
            ]
        }
        
        training_examples.append(example)
    
    # Write to JSONL
    with open(output_file, 'w', encoding='utf-8') as f:
        for example in training_examples:
            f.write(json.dumps(example, ensure_ascii=False) + '\n')
    
    print(f"✅ Created {len(training_examples)} training examples in {output_file}")
    return training_examples

def create_summary_report(students: List[Dict], output_file: str = "training_data_summary.md"):
    """Create human-readable summary of training data"""
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Trajectory Engine - Training Data Summary\n\n")
        f.write(f"**Total Students:** {len(students)}\n\n")
        
        for i, student in enumerate(students, 1):
            components = calculate_trajectory_components(student)
            trajectory = calculate_trajectory_score(components, student['major'])
            
            f.write(f"## Student {i}: {student['name']}\n\n")
            f.write(f"**Trajectory Score:** {trajectory:.3f}/1.00 ({trajectory*100:.1f}%)\n\n")
            f.write(f"**Components:**\n")
            f.write(f"- Academic: {components['academic']:.3f}\n")
            f.write(f"- Behavioral: {components['behavioral']:.3f}\n")
            f.write(f"- Skills: {components['skills']:.3f}\n")
            f.write(f"- Grit: {components['grit']:.3f}\n\n")
            f.write(f"**Key Metrics:**\n")
            f.write(f"- GPA: {student['gpa']}/10\n")
            f.write(f"- Projects: {student['projects_count']}\n")
            f.write(f"- Study Hours: {student['study_hours']}h/day\n")
            f.write(f"- Screen Time: {student['screen_time']}h/day\n")
            f.write(f"- Consistency: {student['consistency']}/5\n\n")
            f.write("---\n\n")
    
    print(f"✅ Created summary report: {output_file}")

if __name__ == "__main__":
    print("🚀 Trajectory Engine - LLM Training Data Preparation\n")
    
    # Parse student data
    print("📊 Parsing student data...")
    students = parse_student_data("student data.csv")
    print(f"✅ Loaded {len(students)} students\n")
    
    # Create training data
    print("🔧 Generating training examples...")
    training_examples = create_training_jsonl(students)
    
    # Create summary
    print("📝 Creating summary report...")
    create_summary_report(students)
    
    print("\n✅ Training data preparation complete!")
    print("\nNext steps:")
    print("1. Review training_data.jsonl")
    print("2. Review training_data_summary.md")
    print("3. Run fine-tuning with: python train_llm.py")
