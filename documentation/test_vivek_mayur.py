"""
Test Vivek and Mayur's profiles with the trained LLM
"""

from integration_example import TrajectoryEngineLLM

# Initialize LLM
llm = TrajectoryEngineLLM(model_name="trajectory-engine:latest-enhanced")

# Vivek Desai's data
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

# Mayur Madiwal's data
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
print("VIVEK DESAI - TRAJECTORY ANALYSIS")
print("=" * 80)
print()

vivek_analysis = llm.analyze_student(vivek_data)

print(f"🎯 Trajectory Score: {vivek_analysis.get('trajectory_score', 'N/A')}")
print(f"📈 Placement Likelihood: {vivek_analysis.get('placement_likelihood', 'N/A')}")
print()
print(f"📚 Academic: {vivek_analysis.get('academic_score', 'N/A')}")
print(f"🧠 Behavioral: {vivek_analysis.get('behavioral_score', 'N/A')}")
print(f"💻 Skills: {vivek_analysis.get('skills_score', 'N/A')}")
print()

if vivek_analysis.get('strengths'):
    print("✅ Key Strengths:")
    for strength in vivek_analysis['strengths']:
        print(f"  - {strength}")
    print()

if vivek_analysis.get('improvements'):
    print("⚠️ Areas for Improvement:")
    for improvement in vivek_analysis['improvements']:
        print(f"  - {improvement}")
    print()

if vivek_analysis.get('recommendations'):
    print("💡 Recommendations:")
    for i, rec in enumerate(vivek_analysis['recommendations'], 1):
        print(f"  {i}. {rec}")
    print()

print("=" * 80)
print("FULL RESPONSE:")
print("=" * 80)
print(vivek_analysis.get('raw_response', ''))
print()
print()

print("=" * 80)
print("MAYUR MADIWAL - TRAJECTORY ANALYSIS")
print("=" * 80)
print()

mayur_analysis = llm.analyze_student(mayur_data)

print(f"🎯 Trajectory Score: {mayur_analysis.get('trajectory_score', 'N/A')}")
print(f"📈 Placement Likelihood: {mayur_analysis.get('placement_likelihood', 'N/A')}")
print()
print(f"📚 Academic: {mayur_analysis.get('academic_score', 'N/A')}")
print(f"🧠 Behavioral: {mayur_analysis.get('behavioral_score', 'N/A')}")
print(f"💻 Skills: {mayur_analysis.get('skills_score', 'N/A')}")
print()

if mayur_analysis.get('strengths'):
    print("✅ Key Strengths:")
    for strength in mayur_analysis['strengths']:
        print(f"  - {strength}")
    print()

if mayur_analysis.get('improvements'):
    print("⚠️ Areas for Improvement:")
    for improvement in mayur_analysis['improvements']:
        print(f"  - {improvement}")
    print()

if mayur_analysis.get('recommendations'):
    print("💡 Recommendations:")
    for i, rec in enumerate(mayur_analysis['recommendations'], 1):
        print(f"  {i}. {rec}")
    print()

print("=" * 80)
print("FULL RESPONSE:")
print("=" * 80)
print(mayur_analysis.get('raw_response', ''))
