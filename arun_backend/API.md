# API Documentation

This document lists all the available API endpoints in the backend.

## Base URL
`http://localhost:8000`

## 📚 Students
Manage student profiles and academic data.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/students` | Create a new student profile with GPA and Attendance validation. |
| **POST** | `/list` | Retrieve all students. |
| **POST** | `/subjects` | Add multiple subject scores for a specific student. |
| **POST** | `/full-profile` | Get student basic info, cumulative GPA, attendance, and all subject scores. |
| **POST** | `/debug-fetch` | Raw debug endpoint to see what exactly is in the DB. |

## 📊 Analytics
AI-driven analysis and trajectory scoring.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/analytics/fetch-trajectory` | Get trajectory score for a student. |
| **POST** | `/analytics/fetch-recommendations` | Get personalized recommendations. |
| **POST** | `/analytics/fetch-gap-analysis` | Get gap analysis against alumni data. |
| **POST** | `/analytics/generate-vector` | Trigger the creation and storage of a student's semantic vector profile. |

## 📈 Metrics
Track behavioral and wellbeing metrics.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/metrics/fetch-behavioral` | Get behavioral metrics (study hours, project count, etc.). |
| **POST** | `/metrics/fetch-wellbeing` | Get daily digital wellbeing data. |
| **POST** | `/metrics/wellbeing/sync` | Sync new wellbeing data. |
| **POST** | `/metrics/fetch-skills` | Get skill assessment scores. |
| **POST** | `/metrics/logs/add` | Add a new daily activity log. |
| **POST** | `/metrics/logs/fetch` | Fetch all activity logs for a specific student. |

## 🎮 Gamification
Badges and achievements.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/gamification/fetch-badges` | Get all available badges. |
| **POST** | `/gamification/fetch-student-badges` | Get badges earned by a student. |

## 👥 Community
Social features, memes, and reels.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/community/upload` | Upload a meme or reel. |
| **GET** | `/community/feed` | Retrieve the latest memes and reels. |
| **POST** | `/community/{post_id}/like` | Increment the like count for a post. |

## 📅 Activities
Schedule, To-Do, and Planner.

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/activities/` | Create a new activity (schedule/todo/plan). |
| **POST** | `/activities/fetch` | Get activities with optional filters. |
| **PATCH** | `/activities/{activity_id}` | Modify an activity (e.g., mark as complete). |
| **DELETE** | `/activities/{activity_id}` | Remove an activity. |
| **POST** | `/activities/schedule/today` | Quick endpoint to get today's schedule. |
| **POST** | `/activities/todos/pending` | Quick endpoint to get all incomplete todos. |

---
*Generated automatically based on backend routes.*
