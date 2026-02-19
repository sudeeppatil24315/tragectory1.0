"""Test Mayur's profile"""
from integration_example import TrajectoryEngineLLM

llm = TrajectoryEngineLLM(model_name="trajectory-engine:latest-enhanced")

mayur_data = {
    'name': 'Mayur Madiwal',
    'major': 'Computer Science',
    'semester': 7,
    'gpa': 8.1,
    'gpa_trend': 'Stable',
    'attendance': 86,
    'backlogs': 0,
    'programming_languages': 'Python, Java, SQL, HTML/CSS, Machine Learning, Cloud Computing',
    'strongest_skill': 'Python',
    'projects_count': 3,
    'project_types': 'Personal, Internship, Real-world',
    'deployed_project': 'Yes',
    'internship': 'No',
    'internship_months': 3,
    'problem_solving': 4,
    'communication': 4,
    'study_hours': 4,
    'practice_hours': 1,
    'screen_time': 5,
    'social_media_time': 2,
    'sleep_hours': 6,
    'sleep_schedule': 'Irregular',
    'distraction_level': 4,
    'consistency': 4,
    'career_clarity': 3,
    'confidence': 1,
    'interview_fear': 2,
    'placement_prep': 'No',
    'strength': 'Communication, Personality, Problem solving',
    'weakness': 'fear about losing, fear about future actions and future results',
    'habit_to_improve': 'self doubting, judging',
    'blockers': 'Time management, lack of confidence'
}

print("=" * 80)
print("MAYUR MADIWAL - TRAJECTORY ANALYSIS")
print("=" * 80)
print("\n📊 Analyzing...\n")

analysis = llm.analyze_student(mayur_data)

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
