"""
Analyze all students from sudent2.csv using trained LLM
"""

import csv
import json
from integration_example import TrajectoryEngineLLM

def parse_projects(value):
    """Parse project count from various formats"""
    if not value:
        return 0
    # Handle formats like "8 IN COLLEGE AND OVER ALL 18 +"
    if 'OVER ALL' in value.upper():
        parts = value.upper().split('OVER ALL')
        if len(parts) > 1:
            num = ''.join(c for c in parts[1] if c.isdigit())
            return int(num) if num else 0
    # Handle simple numbers
    num = ''.join(c for c in value if c.isdigit())
    return int(num) if num else 0

def parse_hours(value):
    """Parse hours from various formats"""
    if not value:
        return 0
    # Handle formats like "8-10", "2-3", "5 HRS"
    value = str(value).upper().replace('HRS', '').replace('HOURS', '').replace('MINUTES', '').strip()
    if '-' in value:
        parts = value.split('-')
        # Take average
        try:
            num1 = float(''.join(c for c in parts[0] if c.isdigit() or c == '.'))
            num2 = float(''.join(c for c in parts[1] if c.isdigit() or c == '.'))
            return (num1 + num2) / 2
        except:
            return 0
    # Handle simple numbers
    try:
        num = ''.join(c for c in value if c.isdigit() or c == '.')
        return float(num) if num else 0
    except:
        return 0

def parse_csv(filename):
    """Parse CSV and extract student data"""
    students = []
    
    with open(filename, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Extract key fields with defaults for missing values
            student = {
                'name': row['Full Name'],
                'email': row['Email Address'],
                'age': row['Age'],
                'major': row['Major / Branch'],
                'semester': row['Current Semester'],
                'college': row['College Name'],
                'status': row['Are you a Student or Alumni?'],
                'gpa': float(row['Current GPA (0–10)']) if row['Current GPA (0–10)'] else 0,
                'gpa_trend': row['GPA Trend Over Last Semesters'],
                'attendance': float(row['Average Attendance Percentage'].replace('%', '')) if '%' in row['Average Attendance Percentage'] else float(row['Average Attendance Percentage']) if row['Average Attendance Percentage'] else 0,
                'backlogs': int(row['Number of Backlogs']) if row['Number of Backlogs'] else 0,
                'programming_languages': row['Programming Languages Select all that apply)'],
                'strongest_skill': row['Strongest Technical Skill'],
                'problem_solving': int(row['Problem Solving Ability (1–5)']) if row['Problem Solving Ability (1–5)'] else 3,
                'communication': int(row['Communication Skill (1–5)']) if row['Communication Skill (1–5)'] else 3,
                'teamwork': int(row['Teamwork Ability (1–5)']) if row['Teamwork Ability (1–5)'] else 3,
                'consistency': int(row['Consistency Level (1–5)']) if row['Consistency Level (1–5)'] else 3,
                'projects_count': parse_projects(row['Number of Projects Completed']),
                'project_types': row['Project Types (Select all that apply)'],
                'deployed_project': row['Have you deployed a project?'],
                'internship': row['Internship experience?'],
                'internship_months': row['Internship duration in months'],
                'study_hours': parse_hours(row['Study hours per day']),
                'practice_hours': parse_hours(row['Technical Knowledge practice hours per day']),
                'screen_time': parse_hours(row['Average daily screen time (hours)']),
                'social_media_time': parse_hours(row['Daily social media time (hours)']),
                'sleep_hours': parse_hours(row['Average sleep hours']),
                'sleep_schedule': row['Sleep schedule'] if row['Sleep schedule'] else 'Irregular',
                'distraction_level': int(row['Distraction level while studying (1–5)']) if row['Distraction level while studying (1–5)'] else 3,
                'career_clarity': int(row['Career clarity level (1–5)']) if row['Career clarity level (1–5)'] else 3,
                'confidence': int(row['Confidence level (1–5)']) if row['Confidence level (1–5)'] else 3,
                'interview_fear': int(row['Interview fear level (1–5)']) if row['Interview fear level (1–5)'] else 3,
                'placement_prep': row['Daily placement preparation?'],
                'placement_status': row['Placement status '],
                'strength': row['Biggest strength'],
                'weakness': row['Biggest weakness'],
                'habit_to_improve': row['One habit you want to improve'],
                'blockers': row['What holds you back the most']
            }
            students.append(student)
    
    return students

# Initialize LLM
llm = TrajectoryEngineLLM(model_name="trajectory-engine:latest-enhanced")

# Parse CSV
print("📊 Parsing student data from sudent2.csv...")
students = parse_csv('sudent2.csv')
print(f"✅ Found {len(students)} students\n")

# Analyze each student
results = []

for i, student in enumerate(students, 1):
    print("=" * 80)
    print(f"STUDENT {i}/{len(students)}: {student['name']}")
    print("=" * 80)
    print()
    
    # Analyze
    print("📊 Analyzing...")
    analysis = llm.analyze_student(student)
    
    # Display results
    print(f"🎯 Trajectory Score: {analysis.get('trajectory_score', 'N/A')}")
    print(f"📈 Placement Likelihood: {analysis.get('placement_likelihood', 'N/A')}")
    print()
    print(f"📚 Academic: {analysis.get('academic_score', 'N/A')}")
    print(f"🧠 Behavioral: {analysis.get('behavioral_score', 'N/A')}")
    print(f"💻 Skills: {analysis.get('skills_score', 'N/A')}")
    print()
    
    if analysis.get('strengths'):
        print("✅ Key Strengths:")
        for s in analysis['strengths'][:3]:
            print(f"  - {s}")
        print()
    
    if analysis.get('improvements'):
        print("⚠️ Areas for Improvement:")
        for imp in analysis['improvements'][:3]:
            print(f"  - {imp}")
        print()
    
    if analysis.get('recommendations'):
        print("💡 Top Recommendations:")
        for j, rec in enumerate(analysis['recommendations'][:3], 1):
            print(f"  {j}. {rec}")
        print()
    
    # Store result
    results.append({
        'name': student['name'],
        'gpa': student['gpa'],
        'major': student['major'],
        'trajectory_score': analysis.get('trajectory_score'),
        'placement_likelihood': analysis.get('placement_likelihood'),
        'academic': analysis.get('academic_score'),
        'behavioral': analysis.get('behavioral_score'),
        'skills': analysis.get('skills_score'),
        'strengths': analysis.get('strengths', [])[:3],
        'improvements': analysis.get('improvements', [])[:3],
        'recommendations': analysis.get('recommendations', [])[:3]
    })
    
    print()

# Summary
print("=" * 80)
print("SUMMARY - ALL STUDENTS")
print("=" * 80)
print()

# Sort by trajectory score
results_sorted = sorted(results, key=lambda x: x['trajectory_score'] if x['trajectory_score'] else 0, reverse=True)

print(f"{'Rank':<6} {'Name':<25} {'GPA':<6} {'Score':<8} {'Likelihood':<20}")
print("-" * 80)
for rank, r in enumerate(results_sorted, 1):
    score = f"{r['trajectory_score']:.2f}" if r['trajectory_score'] else "N/A"
    likelihood = r['placement_likelihood'][:18] if r['placement_likelihood'] else "N/A"
    print(f"{rank:<6} {r['name']:<25} {r['gpa']:<6.1f} {score:<8} {likelihood:<20}")

print()
print(f"✅ Analysis complete for {len(students)} students!")
print()
print("Detailed results saved to: all_students_analysis.json")

# Save to JSON
with open('all_students_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, indent=2, ensure_ascii=False)
