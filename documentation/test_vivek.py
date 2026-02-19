"""Test Vivek's profile"""
from integration_example import TrajectoryEngineLLM

llm = TrajectoryEngineLLM(model_name="trajectory-engine:latest-enhanced")

vivek_data = {
    'name': 'Vivek Desai',
    'major': 'Computer Science',
    'semester': 7,
    'gpa': 7.5,
    'gpa_trend': 'Increasing',
    'attendance': 80,
    'backlogs': 0,
    'programming_languages': 'Python, Java, JavaScript, SQL, HTML/CSS, Machine Learning, Cloud Computing',
    'strongest_skill': 'Python',
    'projects_count': 5,
    'project_types': 'Personal, Internship, Real-world',
    'deployed_project': 'Yes',
    'internship': 'No',
    'internship_months': 3,
    'problem_solving': 4,
    'communication': 4,
    'study_hours': 3,
    'practice_hours': 2,
    'screen_time': 6,
    'social_media_time': 2,
    'sleep_hours': 7,
    'sleep_schedule': 'Irregular',
    'distraction_level': 2,
    'consistency': 4,
    'career_clarity': 3,
    'confidence': 3,
    'interview_fear': 3,
    'placement_prep': 'No',
    'strength': 'Selfconfidence, Technical skills',
    'weakness': 'overthinking, Money',
    'habit_to_improve': 'reading, Learning',
    'blockers': 'Mobile over consumption'
}

print("=" * 80)
print("VIVEK DESAI - TRAJECTORY ANALYSIS")
print("=" * 80)
print("\n📊 Analyzing...\n")

analysis = llm.analyze_student(vivek_data)

print(f"🎯 Trajectory Score: {analysis.get('trajectory_score', 'N/A')}")
print(f"📈 Placement Likelihood: {analysis.get('placement_likelihood', 'N/A')}")
print()
print(f"📚 Academic: {analysis.get('academic_score', 'N/A')}")
print(f"🧠 Behavioral: {analysis.get('behavioral_score', 'N/A')}")
print(f"💻 Skills: {analysis.get('skills_score', 'N/A')}")
print()

if analysis.get('strengths'):
    print("✅ Key Strengths:")
    for s in analysis['strengths']:
        print(f"  - {s}")
    print()

if analysis.get('improvements'):
    print("⚠️ Areas for Improvement:")
    for i in analysis['improvements']:
        print(f"  - {i}")
    print()

if analysis.get('recommendations'):
    print("💡 Recommendations:")
    for i, r in enumerate(analysis['recommendations'], 1):
        print(f"  {i}. {r}")
    print()

print("=" * 80)
print("FULL RESPONSE:")
print("=" * 80)
print(analysis.get('raw_response', ''))
