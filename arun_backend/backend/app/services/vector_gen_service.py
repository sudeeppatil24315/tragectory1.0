from sqlalchemy.orm import Session
from app.models import Student, StudentSubjectScore, BehavioralMetric, VectorProfile, DigitalWellbeingDaily, StudentActivity
from app.services.vector_db import upsert_student_vector
import json
from sentence_transformers import SentenceTransformer

# Load model once at module level to avoid reloading
print("Loading Embedding Model for Vector Generation...")
embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_and_store_student_vector(db: Session, student_id: int):
    """
    1. Pull data from Students, Subjects, and Behavioral Metrics
    2. Create a profile summary string
    3. Generate vector and store in ChromaDB AND PostgreSQL
    4. Sync with SQL VectorProfile table
    """
    # 1. Pull Student Data
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        return {"error": "Student not found"}

    # 2. Pull Subjects Data
    subjects = db.query(StudentSubjectScore).filter(StudentSubjectScore.student_id == student_id).all()
    subject_info = ", ".join([f"{s.subject_name}: {s.marks}" for s in subjects])

    # 3. Pull Behavioral Data
    behavior = db.query(BehavioralMetric).filter(BehavioralMetric.student_id == student_id).first()
    behavior_text = ""
    if behavior:
        behavior_text = f"Study hours/week: {behavior.study_hours_per_week}, Projects: {behavior.project_count}, Skill Score: {behavior.skill_score}"

    # 4. Construct Profile Summary
    # This string is what the AI "reads" to find similarities
    profile_summary = (
        f"Student Profile of {student.name}. "
        f"Background: {student.age} year old {student.gender}, studying {student.major} at {student.college_name}. "
        f"Academic Status: Semester {student.semester}, GPA {student.gpa} ({student.gpa_trend}), Attendance {student.attendance}%. "
        f"Backlogs: {student.backlogs}. Placement Status: {student.placement_status}. "
        f"Skills: Programming languages: {student.programming_languages}. Strongest skill: {student.strongest_skill}. "
        f"Strengths/Weaknesses: {student.biggest_strength} / {student.biggest_weakness}. "
        f"Career: Clarity {student.career_clarity}/5, Path: {student.chosen_career_path}, Confidence {student.confidence_level}/5. "
        f"Placement Performance: Relevance {student.role_relevance}%, Attempts {student.placement_attempts}, Months to hire: {student.months_to_get_placed}. "
    )
    
    if behavior:
        profile_summary += (
            f"Habits: Studies {behavior.study_hours_per_week} hrs/week. Lab regular: {behavior.attend_lab_regularly}. "
            f"Assignments on time: {behavior.submit_assignments_on_time}. Follows schedule: {behavior.follow_study_schedule}. "
            f"Projects: {behavior.project_count} ({behavior.project_types}). Deployed: {behavior.deployed_project}. "
            f"Internships: {behavior.internship_exp} ({behavior.internship_duration} months). "
            f"Self-Assessment (1-5): Problem Solving: {behavior.problem_solving}, Communication: {behavior.communication}, Teamwork: {behavior.teamwork}, Consistency: {behavior.consistency}."
        )

    wellbeing = db.query(DigitalWellbeingDaily).filter(DigitalWellbeingDaily.student_id == student_id).order_by(DigitalWellbeingDaily.date.desc()).first()
    if wellbeing:
        profile_summary += (
            f" Wellbeing: Screen time {wellbeing.total_screen_time} hrs, Social {wellbeing.social_time} hrs. "
            f"Phone while studying: {wellbeing.use_phone_while_studying}. Distraction: {wellbeing.distraction_level}/5. "
            f"Mental exhaustion: {wellbeing.mental_exhaustion}. Sleep: {wellbeing.sleep_hours} hrs ({wellbeing.sleep_schedule})."
        )
    
    # === NEW: PLANNING & TIME MANAGEMENT DATA ===
    # This makes the vector smarter about student's organizational skills
    activities = db.query(StudentActivity).filter(StudentActivity.student_id == student_id).all()
    
    if activities:
        # Calculate planning metrics
        total_activities = len(activities)
        completed_activities = len([a for a in activities if a.is_completed])
        completion_rate = (completed_activities / total_activities * 100) if total_activities > 0 else 0
        
        # Calculate study time from activities
        study_activities = [a for a in activities if a.category == "study" and a.duration_minutes]
        total_study_minutes = sum([a.duration_minutes for a in study_activities])
        avg_study_hours_per_day = (total_study_minutes / 60 / 7) if total_study_minutes > 0 else 0
        
        # Count different activity types
        schedule_count = len([a for a in activities if a.activity_type == "schedule"])
        todo_count = len([a for a in activities if a.activity_type == "todo"])
        plan_count = len([a for a in activities if a.activity_type == "plan"])
        
        # High priority tasks
        high_priority_tasks = len([a for a in activities if a.priority == 1])
        high_priority_completed = len([a for a in activities if a.priority == 1 and a.is_completed])
        
        profile_summary += (
            f" Planning Behavior: Task completion rate {completion_rate:.1f}%. "
            f"Total activities tracked: {total_activities} ({schedule_count} scheduled, {todo_count} todos, {plan_count} planned). "
            f"Average study time: {avg_study_hours_per_day:.1f} hrs/day. "
            f"High-priority task completion: {high_priority_completed}/{high_priority_tasks}. "
        )
        
        # Determine planning consistency
        if completion_rate > 70:
            planning_quality = "Excellent planner - consistently completes tasks"
        elif completion_rate > 50:
            planning_quality = "Good planner - completes most tasks"
        elif completion_rate > 30:
            planning_quality = "Inconsistent - struggles with follow-through"
        else:
            planning_quality = "Poor planning - rarely completes planned tasks"
        
        profile_summary += f"Planning quality: {planning_quality}. "
    
    # NEW: Generate the Vector explicitly here
    vector_list = embedding_model.encode(profile_summary).tolist()

    # 5. Store in ChromaDB (Vector DB)
    # Note: Chroma usually generates its own vector if we pass text, but here we can stick to the text
    # so Chroma can re-embed if needed, or we can look into passing the generated vector.
    # For now, let's just let Chroma do its thing (it uses the same model locally) or pass it if upsert supports it.
    # To keep it simple and consistent: we just pass text to Chroma as before.
    # The redundancy is fine for this demo.
    metadata = {
        "name": student.name,
        "major": student.major,
        "gpa": student.gpa
    }
    upsert_student_vector(student_id, profile_summary, metadata)

    # 6. Store/Update in SQL VectorProfile for record keeping
    vector_profile = db.query(VectorProfile).filter(VectorProfile.student_id == student_id).first()
    if not vector_profile:
        vector_profile = VectorProfile(
            student_id=student_id,
            vector_id=f"student_{student_id}",
            profile_summary=profile_summary,
            embedding_vector=vector_list  # <--- NEW: Storing the vector in Postgres!
        )
        db.add(vector_profile)
    else:
        vector_profile.profile_summary = profile_summary
        vector_profile.vector_id = f"student_{student_id}"
        vector_profile.embedding_vector = vector_list # <--- Update vector
    
    db.commit()

    return {
        "status": "success",
        "student_id": student_id,
        "profile_used": profile_summary,
        "vector_preview": vector_list[:5] # Return preview in API response too
    }
