# Trajectory Engine - Complete Architecture Flow Diagram

**Version:** 1.0  
**Date:** February 17, 2026  
**Purpose:** Visual hierarchy and workflow of entire system

---

## Table of Contents

1. [System Overview](#1-system-overview)
2. [Frontend Architecture](#2-frontend-architecture)
3. [Backend Architecture](#3-backend-architecture)
4. [Database Architecture](#4-database-architecture)
5. [Mobile App Architecture](#5-mobile-app-architecture)
6. [Data Flow Diagrams](#6-data-flow-diagrams)
7. [LLM Integration Flow](#7-llm-integration-flow)
8. [Complete Request Flow](#8-complete-request-flow)

---

## 1. System Overview

### 1.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERFACES                              │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │   Web Browser    │  │   Web Browser    │  │  Mobile Device   │ │
│  │  (Student View)  │  │  (Admin View)    │  │  (React Native)  │ │
│  │                  │  │                  │  │                  │ │
│  │  React + TS      │  │  React + TS      │  │  Data Collection │ │
│  │  Redux Toolkit   │  │  Redux Toolkit   │  │  Background Sync │ │
│  │  Material-UI     │  │  Material-UI     │  │  SQLite Local    │ │
│  └────────┬─────────┘  └────────┬─────────┘  └────────┬─────────┘ │
│           │                     │                      │            │
│           └─────────────────────┴──────────────────────┘            │
│                                 │                                   │
└─────────────────────────────────┼───────────────────────────────────┘
                                  │
                                  │ HTTPS/REST API
                                  │
┌─────────────────────────────────▼───────────────────────────────────┐
│                         BACKEND LAYER                                │
├─────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Application                        │  │
│  │                                                               │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐            │  │
│  │  │  Student   │  │   Admin    │  │   Mobile   │            │  │
│  │  │  Endpoints │  │  Endpoints │  │  Endpoints │            │  │
│  │  └─────┬──────┘  └─────┬──────┘  └─────┬──────┘            │  │
│  │        │               │               │                   │  │
│  │        └───────────────┴───────────────┘                   │  │
│  │                        │                                   │  │
│  │  ┌─────────────────────▼────────────────────────────┐     │  │
│  │  │           Service Layer                          │     │  │
│  │  │                                                   │     │  │
│  │  │  • Data Cleaning (LLM Job #1)                    │     │  │
│  │  │  • Recommendation Engine (LLM Job #2)            │     │  │
│  │  │  • Voice Evaluation (LLM Job #3)                 │     │  │
│  │  │  • Gap Analysis (LLM Job #4)                     │     │  │
│  │  │  • Skill Demand Analysis (LLM Job #5)            │     │  │
│  │  │  • Vector Engine (NumPy)                         │     │  │
│  │  │  • Prediction Engine (scikit-learn)              │     │  │
│  │  │  • Behavioral Analysis (Pandas)                  │     │  │
│  │  └──────────┬────────────────────┬──────────────────┘     │  │
│  │             │                    │                        │  │
│  └─────────────┼────────────────────┼────────────────────────┘  │
│                │                    │                           │
└────────────────┼────────────────────┼───────────────────────────┘
                 │                    │
                 │                    │ Local API
                 │                    │ (localhost:11434)
                 │                    │
                 │         ┌──────────▼──────────┐
                 │         │   Ollama Server     │
                 │         │  (Llama 3.1 8B)     │
                 │         │                     │
                 │         │  RTX 4060 GPU       │
                 │         │  8GB VRAM           │
                 │         │  i7 14th Gen HX     │
                 │         └─────────────────────┘
                 │
┌────────────────▼─────────────────────────────────────────────────────┐
│                         DATA LAYER                                    │
├──────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │   PostgreSQL     │  │     Qdrant       │  │      Redis       │  │
│  │   (Primary DB)   │  │  (Vector DB)     │  │     (Cache)      │  │
│  │                  │  │                  │  │                  │  │
│  │  • Students      │  │  • Student       │  │  • Session       │  │
│  │  • Alumni        │  │    Vectors       │  │    Tokens        │  │
│  │  • Recommendations│  │  • Alumni        │  │  • LLM Cache     │  │
│  │  • Digital       │  │    Vectors       │  │  • API Cache     │  │
│  │    Wellbeing     │  │  • Similarity    │  │                  │  │
│  │  • Users         │  │    Search        │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                       │
└───────────────────────────────────────────────────────────────────────┘
```

---

## 2. Frontend Architecture

### 2.1 React Application Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                    React Application (Port 3000)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    App.tsx (Root)                       │    │
│  │                                                         │    │
│  │  • React Router Setup                                  │    │
│  │  • Redux Provider                                      │    │
│  │  • Theme Provider (MUI)                                │    │
│  │  • Auth Context                                        │    │
│  └────────────┬───────────────────────────────────────────┘    │
│               │                                                 │
│               ├─────────────────┬───────────────────────────┐   │
│               │                 │                           │   │
│  ┌────────────▼──────┐  ┌──────▼────────┐  ┌─────────────▼──┐ │
│  │  Student Routes   │  │  Admin Routes │  │  Auth Routes   │ │
│  │  /dashboard       │  │  /admin       │  │  /login        │ │
│  │  /profile         │  │  /admin/...   │  │  /register     │ │
│  └────────┬──────────┘  └──────┬────────┘  └────────────────┘ │
│           │                    │                                │
│           │                    │                                │
│  ┌────────▼────────────────────▼──────────────────────────┐    │
│  │              Redux Store (State Management)             │    │
│  │                                                         │    │
│  │  ┌──────────────┐  ┌──────────────┐  ┌─────────────┐  │    │
│  │  │ studentSlice │  │  adminSlice  │  │  authSlice  │  │    │
│  │  │              │  │              │  │             │  │    │
│  │  │ • profile    │  │ • students   │  │ • user      │  │    │
│  │  │ • trajectory │  │ • analytics  │  │ • token     │  │    │
│  │  │ • recommendations│ • filters  │  │ • isAuth    │  │    │
│  │  │ • progress   │  │ • stats      │  │             │  │    │
│  │  └──────────────┘  └──────────────┘  └─────────────┘  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Component Hierarchy                      │  │
│  │                                                           │  │
│  │  Pages/                                                   │  │
│  │  ├── StudentDashboard.tsx                                │  │
│  │  │   ├── TrajectoryScoreCard                             │  │
│  │  │   ├── ComponentBreakdown                              │  │
│  │  │   ├── DigitalWellbeingMetrics                         │  │
│  │  │   ├── Recommendations                                 │  │
│  │  │   ├── SimilarAlumni                                   │  │
│  │  │   ├── GapAnalysis                                     │  │
│  │  │   └── ProgressTracking                                │  │
│  │  │                                                        │  │
│  │  ├── AdminDashboard.tsx                                  │  │
│  │  │   ├── OverviewStats                                   │  │
│  │  │   ├── ScoreDistribution                               │  │
│  │  │   ├── StudentList                                     │  │
│  │  │   ├── BehavioralAnalytics                             │  │
│  │  │   ├── RecommendationsAnalytics                        │  │
│  │  │   └── BulkOperations                                  │  │
│  │  │                                                        │  │
│  │  └── Common Components/                                  │  │
│  │      ├── ScoreCard                                       │  │
│  │      ├── ProgressBar                                     │  │
│  │      ├── TrendChart                                      │  │
│  │      └── LoadingState                                    │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  API Service Layer                        │  │
│  │                                                           │  │
│  │  services/                                                │  │
│  │  ├── api.ts (Axios instance with interceptors)           │  │
│  │  ├── studentService.ts                                   │  │
│  │  │   ├── getDashboard()                                  │  │
│  │  │   ├── generateRecommendations()                       │  │
│  │  │   ├── completeRecommendation()                        │  │
│  │  │   └── getTrajectoryHistory()                          │  │
│  │  │                                                        │  │
│  │  ├── adminService.ts                                     │  │
│  │  │   ├── getOverview()                                   │  │
│  │  │   ├── getStudents()                                   │  │
│  │  │   ├── importCSV()                                     │  │
│  │  │   └── exportCSV()                                     │  │
│  │  │                                                        │  │
│  │  └── authService.ts                                      │  │
│  │      ├── login()                                         │  │
│  │      ├── register()                                      │  │
│  │      └── logout()                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 3. Backend Architecture

### 3.1 FastAPI Application Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                  FastAPI Application (Port 8000)                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    main.py (Entry Point)                │    │
│  │                                                         │    │
│  │  • CORS Middleware                                     │    │
│  │  • Authentication Middleware                           │    │
│  │  • Error Handling                                      │    │
│  │  • Router Registration                                 │    │
│  └────────────┬───────────────────────────────────────────┘    │
│               │                                                 │
│               ├─────────────────┬───────────────────────────┐   │
│               │                 │                           │   │
│  ┌────────────▼──────┐  ┌──────▼────────┐  ┌─────────────▼──┐ │
│  │  Student Router   │  │  Admin Router │  │  Mobile Router │ │
│  │  /api/students    │  │  /api/admin   │  │  /api/mobile   │ │
│  └────────┬──────────┘  └──────┬────────┘  └────────┬───────┘ │
│           │                    │                     │          │
│           │                    │                     │          │
│  ┌────────▼────────────────────▼─────────────────────▼──────┐  │
│  │                    Service Layer                          │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │           LLM Services (Ollama Integration)         │ │  │
│  │  │                                                     │ │  │
│  │  │  1. data_cleaning.py                               │ │  │
│  │  │     • Clean CSV data                               │ │  │
│  │  │     • Normalize values                             │ │  │
│  │  │     • Fix typos                                    │ │  │
│  │  │     • Temperature: 0.1                             │ │  │
│  │  │                                                     │ │  │
│  │  │  2. recommendation_engine.py                       │ │  │
│  │  │     • Generate personalized recommendations        │ │  │
│  │  │     • Prioritize by impact                         │ │  │
│  │  │     • Include alumni stories                       │ │  │
│  │  │     • Temperature: 0.7                             │ │  │
│  │  │                                                     │ │  │
│  │  │  3. voice_evaluation.py                            │ │  │
│  │  │     • Evaluate voice responses                     │ │  │
│  │  │     • Score technical accuracy                     │ │  │
│  │  │     • Score communication                          │ │  │
│  │  │     • Temperature: 0.3                             │ │  │
│  │  │                                                     │ │  │
│  │  │  4. gap_analysis.py                                │ │  │
│  │  │     • Generate gap narratives                      │ │  │
│  │  │     • Explain impact                               │ │  │
│  │  │     • Provide targets                              │ │  │
│  │  │     • Temperature: 0.7                             │ │  │
│  │  │                                                     │ │  │
│  │  │  5. skill_demand_analysis.py                       │ │  │
│  │  │     • Analyze skill market demand                  │ │  │
│  │  │     • Assign weight (0.5x, 1.0x, 2.0x)            │ │  │
│  │  │     • Provide reasoning                            │ │  │
│  │  │     • Temperature: 0.2                             │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  │                                                           │  │
│  │  ┌─────────────────────────────────────────────────────┐ │  │
│  │  │        Math/ML Services (No LLM)                    │ │  │
│  │  │                                                     │ │  │
│  │  │  6. vector_engine.py                               │ │  │
│  │  │     • Generate student vectors (NumPy)             │ │  │
│  │  │     • Normalize features                           │ │  │
│  │  │     • Store in Qdrant                              │ │  │
│  │  │                                                     │ │  │
│  │  │  7. prediction_engine.py                           │ │  │
│  │  │     • Calculate trajectory score                   │ │  │
│  │  │     • Cosine similarity (scikit-learn)             │ │  │
│  │  │     • Weighted averaging                           │ │  │
│  │  │                                                     │ │  │
│  │  │  8. behavioral_analysis.py                         │ │  │
│  │  │     • Analyze digital wellbeing patterns           │ │  │
│  │  │     • Calculate correlations (Pandas)              │ │  │
│  │  │     • Identify trends                              │ │  │
│  │  └─────────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Database Layer                         │  │
│  │                                                           │  │
│  │  models/                                                  │  │
│  │  ├── student.py (SQLAlchemy ORM)                         │  │
│  │  ├── alumni.py                                           │  │
│  │  ├── recommendation.py                                   │  │
│  │  ├── digital_wellbeing.py                                │  │
│  │  └── user.py                                             │  │
│  │                                                           │  │
│  │  schemas/                                                 │  │
│  │  ├── student.py (Pydantic validation)                    │  │
│  │  ├── alumni.py                                           │  │
│  │  ├── recommendation.py                                   │  │
│  │  └── digital_wellbeing.py                                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 4. Database Architecture

### 4.1 Database Schema & Relationships

```
┌─────────────────────────────────────────────────────────────────┐
│                      PostgreSQL Database                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    students (Main Table)                │    │
│  │                                                         │    │
│  │  PK: id (UUID)                                         │    │
│  │  • name, email, age, gender                            │    │
│  │  • major, semester, college                            │    │
│  │  • gpa, gpa_trend, attendance                          │    │
│  │  • internal_marks, backlogs                            │    │
│  │  • study_hours, practice_hours                         │    │
│  │  • screen_time, social_media_time                      │    │
│  │  • sleep_hours, sleep_schedule                         │    │
│  │  • distraction_level, consistency_level                │    │
│  │  • programming_languages[], other_skills[]             │    │
│  │  • problem_solving, communication, teamwork            │    │
│  │  • projects, deployed, internship                      │    │
│  │  • trajectory_score, academic_score                    │    │
│  │  • behavioral_score, skills_score, grit_score          │    │
│  │  • created_at, updated_at, last_active                 │    │
│  │  • mobile_synced, last_sync_at                         │    │
│  └────────────┬───────────────────────────────────────────┘    │
│               │                                                 │
│               │ 1:N                                             │
│               │                                                 │
│  ┌────────────▼───────────────────────────────────────────┐    │
│  │              recommendations                            │    │
│  │                                                         │    │
│  │  PK: id (UUID)                                         │    │
│  │  FK: student_id → students(id)                         │    │
│  │  • title, description                                  │    │
│  │  • category (Academic/Behavioral/Skills)               │    │
│  │  • impact (High/Medium/Low)                            │    │
│  │  • estimated_points                                    │    │
│  │  • timeline, action_steps[]                            │    │
│  │  • alumni_story                                        │    │
│  │  • completed, completed_at                             │    │
│  │  • generated_at, llm_model                             │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │           digital_wellbeing (Time Series)               │    │
│  │                                                         │    │
│  │  PK: id (UUID)                                         │    │
│  │  FK: student_id → students(id)                         │    │
│  │  • date                                                │    │
│  │  • total_screen_time                                   │    │
│  │  • screen_time_by_hour[24]                             │    │
│  │  • app_usage[] (JSON array)                            │    │
│  │  • focus_score                                         │    │
│  │  • educational_time, social_media_time                 │    │
│  │  • entertainment_time, productivity_time               │    │
│  │  • sleep_duration, bedtime, wake_time                  │    │
│  │  • synced_at, device_type                              │    │
│  │                                                         │    │
│  │  INDEX: (student_id, date)                             │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    alumni                               │    │
│  │                                                         │    │
│  │  PK: id (UUID)                                         │    │
│  │  • name (anonymized), graduation_year                  │    │
│  │  • major, college                                      │    │
│  │  • gpa, attendance, backlogs                           │    │
│  │  • study_hours, projects, internship                   │    │
│  │  • programming_languages[], problem_solving            │    │
│  │  • communication                                       │    │
│  │  • placement_status (Placed/Not Placed)                │    │
│  │  • company_tier (Tier1/Tier2/Tier3)                    │    │
│  │  • company_name (anonymized), role                     │    │
│  │  • salary_range, role_to_major_match                   │    │
│  │  • trajectory_score, academic_score                    │    │
│  │  • behavioral_score, skills_score                      │    │
│  │  • created_at, updated_at                              │    │
│  │                                                         │    │
│  │  INDEX: (major, trajectory_score)                      │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    users (Auth)                         │    │
│  │                                                         │    │
│  │  PK: id (UUID)                                         │    │
│  │  • email (unique), password_hash                       │    │
│  │  • role (student/admin)                                │    │
│  │  • student_id → students(id) (nullable)                │    │
│  │  • created_at, last_login                              │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                  achievements                           │    │
│  │                                                         │    │
│  │  PK: id (UUID)                                         │    │
│  │  FK: student_id → students(id)                         │    │
│  │  • achievement_type                                    │    │
│  │  • name, description, icon                             │    │
│  │  • unlocked_at                                         │    │
│  │  • progress (0-1)                                      │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Qdrant Vector Database                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              students_collection                        │    │
│  │                                                         │    │
│  │  • vector: [15-20 dimensions]                          │    │
│  │    - Academic features (normalized)                    │    │
│  │    - Behavioral features (normalized)                  │    │
│  │    - Skills features (normalized)                      │    │
│  │                                                         │    │
│  │  • payload:                                            │    │
│  │    - student_id (UUID)                                 │    │
│  │    - name, major, semester                             │    │
│  │    - gpa, attendance                                   │    │
│  │    - trajectory_score                                  │    │
│  │                                                         │    │
│  │  • distance_metric: Cosine                             │    │
│  │  • index: HNSW (fast approximate search)               │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │               alumni_collection                         │    │
│  │                                                         │    │
│  │  • vector: [15-20 dimensions]                          │    │
│  │    - Academic features (historical)                    │    │
│  │    - Behavioral features (historical)                  │    │
│  │    - Skills features (historical)                      │    │
│  │                                                         │    │
│  │  • payload:                                            │    │
│  │    - alumni_id (UUID)                                  │    │
│  │    - name (anonymized), major                          │    │
│  │    - graduation_year                                   │    │
│  │    - company_tier, salary_range                        │    │
│  │    - placement_status                                  │    │
│  │    - trajectory_score                                  │    │
│  │                                                         │    │
│  │  • distance_metric: Cosine                             │    │
│  │  • index: HNSW                                         │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         Redis Cache                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  • session:user:{user_id} → Session data (JWT tokens)           │
│  • llm:cache:{prompt_hash} → LLM response (30 days TTL)         │
│  • api:cache:{endpoint}:{params} → API response (5 min TTL)     │
│  • student:dashboard:{student_id} → Dashboard data (1 hour TTL) │
│  • admin:stats → Admin stats (5 min TTL)                        │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 5. Mobile App Architecture

### 5.1 React Native Application Structure

```
┌─────────────────────────────────────────────────────────────────┐
│              React Native Mobile App (Android/iOS)               │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │                    App.tsx (Root)                       │    │
│  │                                                         │    │
│  │  • Navigation Container                                │    │
│  │  • Redux Provider                                      │    │
│  │  • Background Service Setup                            │    │
│  └────────────┬───────────────────────────────────────────┘    │
│               │                                                 │
│               ├─────────────────┬───────────────────────────┐   │
│               │                 │                           │   │
│  ┌────────────▼──────┐  ┌──────▼────────┐  ┌─────────────▼──┐ │
│  │  Home Screen      │  │ Insights Screen│  │ Settings Screen│ │
│  │  (Dashboard)      │  │ (Analytics)    │  │ (Permissions)  │ │
│  └────────┬──────────┘  └──────┬────────┘  └────────────────┘ │
│           │                    │                                │
│           │                    │                                │
│  ┌────────▼────────────────────▼──────────────────────────┐    │
│  │              Background Services                        │    │
│  │                                                         │    │
│  │  ┌─────────────────────────────────────────────────┐   │    │
│  │  │  1. Screen Time Tracker                         │   │    │
│  │  │     • Monitor screen on/off events              │   │    │
│  │  │     • Track total daily screen time             │   │    │
│  │  │     • Categorize by time of day                 │   │    │
│  │  │     • Store in local SQLite                     │   │    │
│  │  └─────────────────────────────────────────────────┘   │    │
│  │                                                         │    │
│  │  ┌─────────────────────────────────────────────────┐   │    │
│  │  │  2. App Usage Monitor                           │   │    │
│  │  │     • Track foreground app changes              │   │    │
│  │  │     • Categorize apps (Educational/Social/etc)  │   │    │
│  │  │     • Calculate time per app                    │   │    │
│  │  │     • Calculate Focus Score                     │   │    │
│  │  │     • Store in local SQLite                     │   │    │
│  │  └─────────────────────────────────────────────────┘   │    │
│  │                                                         │    │
│  │  ┌─────────────────────────────────────────────────┐   │    │
│  │  │  3. Sleep Detector                              │   │    │
│  │  │     • Monitor screen off at night               │   │    │
│  │  │     • Detect bedtime and wake time              │   │    │
│  │  │     • Calculate sleep duration                  │   │    │
│  │  │     • Track sleep consistency                   │   │    │
│  │  │     • Store in local SQLite                     │   │    │
│  │  └─────────────────────────────────────────────────┘   │    │
│  │                                                         │    │
│  │  ┌─────────────────────────────────────────────────┐   │    │
│  │  │  4. Data Sync Service                           │   │    │
│  │  │     • Run daily at 2 AM                         │   │    │
│  │  │     • Aggregate last 24 hours data              │   │    │
│  │  │     • Encrypt data                              │   │    │
│  │  │     • POST to /api/mobile/sync                  │   │    │
│  │  │     • Delete synced data (keep 7 days local)    │   │    │
│  │  │     • Retry on failure (exponential backoff)    │   │    │
│  │  └─────────────────────────────────────────────────┘   │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Local Storage (SQLite)                   │  │
│  │                                                           │  │
│  │  Tables:                                                  │  │
│  │  ├── screen_time_events                                  │  │
│  │  │   • timestamp, event_type (on/off), duration          │  │
│  │  │                                                        │  │
│  │  ├── app_usage_events                                    │  │
│  │  │   • timestamp, app_name, category, duration           │  │
│  │  │                                                        │  │
│  │  ├── sleep_events                                        │  │
│  │  │   • date, bedtime, wake_time, duration                │  │
│  │  │                                                        │  │
│  │  └── sync_queue                                          │  │
│  │      • date, data (JSON), synced (boolean)               │  │
│  │                                                           │  │
│  │  Retention: 30 days (auto-delete older data)             │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Permissions Required                     │  │
│  │                                                           │  │
│  │  Android:                                                 │  │
│  │  • PACKAGE_USAGE_STATS (App usage tracking)              │  │
│  │  • SYSTEM_ALERT_WINDOW (Overlay detection)               │  │
│  │  • WAKE_LOCK (Background service)                        │  │
│  │  • INTERNET (Data sync)                                  │  │
│  │                                                           │  │
│  │  iOS:                                                     │  │
│  │  • Screen Time API access                                │  │
│  │  • Background App Refresh                                │  │
│  │  • Network access                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

---

## 6. Data Flow Diagrams

### 6.1 Student Dashboard Load Flow

```
┌──────────┐                                                    
│ Student  │                                                    
│ Browser  │                                                    
└────┬─────┘                                                    
     │                                                          
     │ 1. GET /dashboard                                        
     │                                                          
     ▼                                                          
┌─────────────────┐                                            
│  React App      │                                            
│  (Frontend)     │                                            
└────┬────────────┘                                            
     │                                                          
     │ 2. API Call: GET /api/students/:id/dashboard            
     │                                                          
     ▼                                                          
┌─────────────────────────────────────────────────────────┐    
│  FastAPI Backend                                        │    
│                                                         │    
│  ┌──────────────────────────────────────────────────┐  │    
│  │  Student Router                                  │  │    
│  │  /api/students/:id/dashboard                     │  │    
│  └────┬─────────────────────────────────────────────┘  │    
│       │                                                 │    
│       │ 3. Check Redis Cache                            │    
│       │                                                 │    
│       ▼                                                 │    
│  ┌──────────────┐                                      │    
│  │ Redis Cache  │  Cache Hit? → Return cached data     │    
│  └──────┬───────┘                                      │    
│         │ Cache Miss                                    │    
│         │                                               │    
│         │ 4. Fetch from PostgreSQL                     │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  PostgreSQL                                  │     │    
│  │  • Get student profile                       │     │    
│  │  • Get recommendations                       │     │    
│  │  • Get digital wellbeing (last 7 days)       │     │    
│  │  • Get achievements                          │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 5. Query Qdrant for similar alumni           │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Qdrant Vector DB                            │     │    
│  │  • Search with student vector                │     │    
│  │  • Return top 5 similar alumni               │     │    
│  │  • Cosine similarity scores                  │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 6. Calculate trajectory score                │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Prediction Engine (Pure Math)               │     │    
│  │  • Weighted average of alumni outcomes       │     │    
│  │  • Calculate confidence interval             │     │    
│  │  • Determine placement likelihood            │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 7. Calculate gap analysis                    │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Gap Analysis Service                        │     │    
│  │  • Compare student vs alumni averages        │     │    
│  │  • Identify gaps (NumPy)                     │     │    
│  │  • Call LLM for narratives                   │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 8. Call Ollama for gap narratives            │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Ollama Server (LLM Job #4)                  │     │    
│  │  • Generate engaging narratives              │     │    
│  │  • Explain why gaps matter                   │     │    
│  │  • Include impact data                       │     │    
│  │  • Temperature: 0.7                          │     │    
│  │  • Response time: 0.5-1s                     │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 9. Aggregate all data                        │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Response Builder                            │     │    
│  │  • Combine all data into JSON                │     │    
│  │  • Cache in Redis (1 hour TTL)               │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
└─────────┼───────────────────────────────────────────────┘    
          │                                                    
          │ 10. Return JSON response                          
          │                                                    
          ▼                                                    
┌─────────────────┐                                            
│  React App      │                                            
│  (Frontend)     │                                            
│                 │                                            
│  11. Update Redux Store                                     
│  12. Render Components:                                     
│      • TrajectoryScoreCard                                  
│      • ComponentBreakdown                                   
│      • DigitalWellbeingMetrics                              
│      • Recommendations                                      
│      • SimilarAlumni                                        
│      • GapAnalysis                                          
│      • ProgressTracking                                     
└─────────────────┘                                            

Total Time: 1-2 seconds (with LLM calls)
Cache Hit Time: <100ms
```

---

### 6.2 Recommendation Generation Flow

```
┌──────────┐                                                    
│ Student  │                                                    
│ Browser  │                                                    
└────┬─────┘                                                    
     │                                                          
     │ 1. Click "Regenerate Recommendations"                    
     │                                                          
     ▼                                                          
┌─────────────────┐                                            
│  React App      │                                            
└────┬────────────┘                                            
     │                                                          
     │ 2. POST /api/students/:id/recommendations/generate      
     │                                                          
     ▼                                                          
┌─────────────────────────────────────────────────────────┐    
│  FastAPI Backend                                        │    
│                                                         │    
│  ┌──────────────────────────────────────────────────┐  │    
│  │  Student Router                                  │  │    
│  └────┬─────────────────────────────────────────────┘  │    
│       │                                                 │    
│       │ 3. Gather context data                          │    
│       ▼                                                 │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Context Builder                             │     │    
│  │  • Student profile (PostgreSQL)              │     │    
│  │  • Component scores                          │     │    
│  │  • Gap analysis                              │     │    
│  │  • Digital wellbeing data                    │     │    
│  │  • Similar alumni success stories            │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 4. Build LLM prompt                           │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Recommendation Engine (LLM Job #2)          │     │    
│  │                                              │     │    
│  │  Prompt Template:                            │     │    
│  │  "Generate 3-5 personalized recommendations  │     │    
│  │   for student with:                          │     │    
│  │   - GPA: 8.6, Attendance: 90%                │     │    
│  │   - Behavioral score: 0.48 (low)             │     │    
│  │   - Skills score: 0.73                       │     │    
│  │   - Screen time: 6h/day (high)               │     │    
│  │   - Problem-solving: 2/5 (low)               │     │    
│  │                                              │     │    
│  │   Similar alumni who improved these areas    │     │    
│  │   got Tier 1 placements.                     │     │    
│  │                                              │     │    
│  │   Provide:                                   │     │    
│  │   1. Title                                   │     │    
│  │   2. Description with specific actions       │     │    
│  │   3. Impact (High/Medium/Low)                │     │    
│  │   4. Estimated points improvement            │     │    
│  │   5. Realistic timeline                      │     │    
│  │   6. Alumni success story reference"         │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 5. Call Ollama API                            │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Ollama Server                               │     │    
│  │  POST http://localhost:11434/api/generate    │     │    
│  │                                              │     │    
│  │  Request:                                    │     │    
│  │  {                                           │     │    
│  │    "model": "llama3.1:8b",                   │     │    
│  │    "prompt": "...",                          │     │    
│  │    "temperature": 0.7,                       │     │    
│  │    "max_tokens": 800                         │     │    
│  │  }                                           │     │    
│  │                                              │     │    
│  │  GPU Processing:                             │     │    
│  │  • RTX 4060 (8GB VRAM)                       │     │    
│  │  • 25-67 tokens/second                       │     │    
│  │  • Response time: 1-2 seconds                │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 6. Parse LLM response                         │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Response Parser                             │     │    
│  │  • Extract recommendations (JSON)            │     │    
│  │  • Validate structure                        │     │    
│  │  • Assign IDs                                │     │    
│  │  • Add metadata (generated_at, llm_model)    │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 7. Save to database                           │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  PostgreSQL                                  │     │    
│  │  INSERT INTO recommendations                 │     │    
│  │  • student_id, title, description            │     │    
│  │  • category, impact, estimated_points        │     │    
│  │  • timeline, action_steps, alumni_story      │     │    
│  │  • generated_at, llm_model                   │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 8. Invalidate cache                           │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Redis Cache                                 │     │    
│  │  DELETE student:dashboard:{student_id}       │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
└─────────┼───────────────────────────────────────────────┘    
          │                                                    
          │ 9. Return recommendations                         
          │                                                    
          ▼                                                    
┌─────────────────┐                                            
│  React App      │                                            
│  10. Update UI with new recommendations                     
│  11. Show success notification                              
└─────────────────┘                                            

Total Time: 2-3 seconds (LLM processing)
```

---

### 6.3 Mobile App Data Sync Flow

```
┌──────────────┐                                                
│ Mobile App   │                                                
│ (Background) │                                                
└──────┬───────┘                                                
       │                                                        
       │ 1. Daily at 2 AM (or manual sync)                     
       │                                                        
       ▼                                                        
┌──────────────────────────────────────────────────────┐       
│  Data Sync Service                                   │       
│                                                      │       
│  ┌────────────────────────────────────────────────┐ │       
│  │  1. Aggregate Last 24 Hours Data               │ │       
│  │                                                │ │       
│  │  Query SQLite:                                 │ │       
│  │  • screen_time_events (last 24h)              │ │       
│  │  • app_usage_events (last 24h)                │ │       
│  │  • sleep_events (last night)                  │ │       
│  │                                                │ │       
│  │  Calculate:                                    │ │       
│  │  • Total screen time                          │ │       
│  │  • Screen time by hour [24 values]            │ │       
│  │  • App usage by category                      │ │       
│  │  • Focus score                                │ │       
│  │  • Sleep duration                             │ │       
│  └────────┬───────────────────────────────────────┘ │       
│           │                                          │       
│           │ 2. Build sync payload                    │       
│           ▼                                          │       
│  ┌────────────────────────────────────────────────┐ │       
│  │  Payload Builder                               │ │       
│  │                                                │ │       
│  │  {                                             │ │       
│  │    "studentId": "uuid",                        │ │       
│  │    "data": [                                   │ │       
│  │      {                                         │ │       
│  │        "date": "2026-02-17",                   │ │       
│  │        "screenTime": 6.2,                      │ │       
│  │        "screenTimeByHour": [0,0,0,...],        │ │       
│  │        "appUsage": [                           │ │       
│  │          {                                     │ │       
│  │            "appName": "Instagram",             │ │       
│  │            "category": "Social",               │ │       
│  │            "duration": 120                     │ │       
│  │          },                                    │ │       
│  │          ...                                   │ │       
│  │        ],                                      │ │       
│  │        "focusScore": 0.65,                     │ │       
│  │        "educationalTime": 2.0,                 │ │       
│  │        "socialMediaTime": 3.0,                 │ │       
│  │        "entertainmentTime": 2.5,               │ │       
│  │        "productivityTime": 0.7,                │ │       
│  │        "sleepDuration": 7.8,                   │ │       
│  │        "bedtime": "2026-02-16T23:30:00Z",      │ │       
│  │        "wakeTime": "2026-02-17T07:18:00Z"      │ │       
│  │      }                                         │ │       
│  │    ]                                           │ │       
│  │  }                                             │ │       
│  └────────┬───────────────────────────────────────┘ │       
│           │                                          │       
│           │ 3. Encrypt data (AES-256)                │       
│           │                                          │       
│           │ 4. Check WiFi connection                 │       
│           │                                          │       
│           │ 5. POST to backend                       │       
│           ▼                                          │       
└───────────┼──────────────────────────────────────────┘       
            │                                                   
            │ POST /api/mobile/sync                            
            │                                                   
            ▼                                                   
┌─────────────────────────────────────────────────────────┐    
│  FastAPI Backend                                        │    
│                                                         │    
│  ┌──────────────────────────────────────────────────┐  │    
│  │  Mobile Router                                   │  │    
│  │  /api/mobile/sync                                │  │    
│  └────┬─────────────────────────────────────────────┘  │    
│       │                                                 │    
│       │ 6. Validate payload                             │    
│       │ 7. Decrypt data                                 │    
│       │                                                 │    
│       │ 8. Process each day's data                      │    
│       ▼                                                 │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Behavioral Analysis Service                 │     │    
│  │                                              │     │    
│  │  For each date:                              │     │    
│  │  • Validate data ranges                      │     │    
│  │  • Calculate additional metrics              │     │    
│  │  • Detect anomalies                          │     │    
│  │  • Flag concerning patterns                  │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 9. Save to PostgreSQL                         │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  PostgreSQL                                  │     │    
│  │  INSERT INTO digital_wellbeing               │     │    
│  │  • student_id, date                          │     │    
│  │  • total_screen_time                         │     │    
│  │  • screen_time_by_hour                       │     │    
│  │  • app_usage (JSON)                          │     │    
│  │  • focus_score                               │     │    
│  │  • educational_time, social_media_time       │     │    
│  │  • entertainment_time, productivity_time     │     │    
│  │  • sleep_duration, bedtime, wake_time        │     │    
│  │  • synced_at, device_type                    │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 10. Update student profile                    │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  PostgreSQL                                  │     │    
│  │  UPDATE students                             │     │    
│  │  SET mobile_synced = true,                   │     │    
│  │      last_sync_at = NOW()                    │     │    
│  │  WHERE id = student_id                       │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 11. Invalidate cache                          │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Redis Cache                                 │     │    
│  │  DELETE student:dashboard:{student_id}       │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 12. Check if recalculation needed            │    
│         │     (if behavioral score changed >5%)        │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Prediction Engine                           │     │    
│  │  • Recalculate behavioral score              │     │    
│  │  • Recalculate trajectory score              │     │    
│  │  • Update vector in Qdrant                   │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
└─────────┼───────────────────────────────────────────────┘    
          │                                                    
          │ 13. Return sync confirmation                      
          │                                                    
          ▼                                                    
┌──────────────┐                                               
│ Mobile App   │                                               
│              │                                               
│ 14. Mark data as synced in SQLite                           
│ 15. Delete synced data older than 7 days                    
│ 16. Update last sync timestamp                              
│ 17. Show sync success notification                          
└──────────────┘                                               

Total Time: 5-10 seconds (depending on data size)
Retry on Failure: Exponential backoff (1h, 2h, 4h)
```

---

### 6.4 CSV Import & Data Cleaning Flow (Admin)

```
┌──────────┐                                                    
│  Admin   │                                                    
│ Browser  │                                                    
└────┬─────┘                                                    
     │                                                          
     │ 1. Upload CSV file (students or alumni)                  
     │                                                          
     ▼                                                          
┌─────────────────┐                                            
│  React App      │                                            
└────┬────────────┘                                            
     │                                                          
     │ 2. POST /api/admin/import/students (FormData)           
     │                                                          
     ▼                                                          
┌─────────────────────────────────────────────────────────┐    
│  FastAPI Backend                                        │    
│                                                         │    
│  ┌──────────────────────────────────────────────────┐  │    
│  │  Admin Router                                    │  │    
│  │  /api/admin/import/students                      │  │    
│  └────┬─────────────────────────────────────────────┘  │    
│       │                                                 │    
│       │ 3. Parse CSV file                               │    
│       ▼                                                 │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  CSV Parser                                  │     │    
│  │  • Read CSV with pandas                      │     │    
│  │  • Validate headers                          │     │    
│  │  • Convert to list of dicts                  │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 4. Process each row with LLM                  │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Data Cleaning Service (LLM Job #1)          │     │    
│  │                                              │     │    
│  │  For each row:                               │     │    
│  │                                              │     │    
│  │  Raw Data:                                   │     │    
│  │  {                                           │     │    
│  │    "name": "jhon doe",                       │     │    
│  │    "major": "comp sci",                      │     │    
│  │    "gpa": "85%",                             │     │    
│  │    "languages": "pyton, javaScript, reactjs" │     │    
│  │  }                                           │     │    
│  │                                              │     │    
│  │  LLM Prompt:                                 │     │    
│  │  "Clean and standardize this student data:   │     │    
│  │   - Fix typos in names                       │     │    
│  │   - Normalize major names                    │     │    
│  │   - Convert GPA to 10.0 scale                │     │    
│  │   - Standardize skill names                  │     │    
│  │   Return valid JSON"                         │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 5. Call Ollama API                            │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Ollama Server                               │     │    
│  │  POST http://localhost:11434/api/generate    │     │    
│  │                                              │     │    
│  │  Request:                                    │     │    
│  │  {                                           │     │    
│  │    "model": "llama3.1:8b",                   │     │    
│  │    "prompt": "...",                          │     │    
│  │    "temperature": 0.1,  // Low for consistency│    │    
│  │    "max_tokens": 500                         │     │    
│  │  }                                           │     │    
│  │                                              │     │    
│  │  Response time: 0.5-1 second per row         │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 6. Parse cleaned data                         │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Response Parser                             │     │    
│  │                                              │     │    
│  │  Cleaned Data:                               │     │    
│  │  {                                           │     │    
│  │    "name": "John Doe",                       │     │    
│  │    "major": "Computer Science",              │     │    
│  │    "gpa": 8.5,                               │     │    
│  │    "languages": ["Python", "JavaScript",     │     │    
│  │                  "React"]                    │     │    
│  │  }                                           │     │    
│  │                                              │     │    
│  │  • Validate cleaned data                     │     │    
│  │  • Track quality score                       │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 7. Generate vector                            │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Vector Engine                               │     │    
│  │  • Normalize all features                    │     │    
│  │  • Create vector [15-20 dimensions]          │     │    
│  │  • Calculate component scores                │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 8. Save to PostgreSQL                         │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  PostgreSQL                                  │     │    
│  │  INSERT INTO students                        │     │    
│  │  • All cleaned fields                        │     │    
│  │  • Component scores                          │     │    
│  │  • Trajectory score                          │     │    
│  │  • created_at, updated_at                    │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 9. Save vector to Qdrant                      │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Qdrant Vector DB                            │     │    
│  │  INSERT INTO students_collection             │     │    
│  │  • vector: [normalized features]             │     │    
│  │  • payload: {student_id, name, major, ...}   │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
│         │ 10. Aggregate results                         │    
│         ▼                                               │    
│  ┌──────────────────────────────────────────────┐     │    
│  │  Import Summary Builder                      │     │    
│  │                                              │     │    
│  │  {                                           │     │    
│  │    "totalRows": 156,                         │     │    
│  │    "successfulImports": 152,                 │     │    
│  │    "failedImports": 4,                       │     │    
│  │    "errors": [                               │     │    
│  │      {                                       │     │    
│  │        "row": 23,                            │     │    
│  │        "error": "Invalid GPA value"          │     │    
│  │      }                                       │     │    
│  │    ],                                        │     │    
│  │    "processingTime": "2m 34s",               │     │    
│  │    "averageQualityScore": 0.92               │     │    
│  │  }                                           │     │    
│  └──────┬───────────────────────────────────────┘     │    
│         │                                               │    
└─────────┼───────────────────────────────────────────────┘    
          │                                                    
          │ 11. Return import summary                         
          │                                                    
          ▼                                                    
┌─────────────────┐                                            
│  React App      │                                            
│  12. Display import results                                 
│  13. Show success/error notifications                       
│  14. Refresh student list                                   
└─────────────────┘                                            

Total Time: 1-2 minutes for 156 students
LLM Processing: 0.5-1s per row
Parallel Processing: 8 rows simultaneously
```

---

## 7. LLM Integration Flow

### 7.1 All 5 LLM Jobs Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Ollama Server (Local)                         │
│                  http://localhost:11434                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐    │
│  │              Llama 3.1 8B Model                         │    │
│  │                                                         │    │
│  │  • Model Size: ~4.7GB                                  │    │
│  │  • Parameters: 8 billion                               │    │
│  │  • GPU: RTX 4060 (8GB VRAM)                            │    │
│  │  • CPU: i7 14th Gen HX (14 cores)                      │    │
│  │  • RAM: 16GB                                           │    │
│  │                                                         │    │
│  │  Performance:                                          │    │
│  │  • Tokens/second: 25-67                                │    │
│  │  • Response time: 0.5-2 seconds                        │    │
│  │  • Concurrent requests: 8+                             │    │
│  │  • GPU utilization: 100%                               │    │
│  └────────────────────────────────────────────────────────┘    │
│                                                                  │
└──────────────────────────────┬───────────────────────────────────┘
                               │
                               │ Local API Calls
                               │
┌──────────────────────────────▼───────────────────────────────────┐
│                    FastAPI Backend                                │
│                  LLM Service Layer                                │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  LLM Job #1: Data Cleaning                              │    │
│  │  File: services/data_cleaning.py                        │    │
│  │                                                          │    │
│  │  Purpose: Clean and standardize CSV/ERP data            │    │
│  │  Temperature: 0.1 (deterministic)                       │    │
│  │  Max Tokens: 500                                        │    │
│  │  Processing Time: 0.5-1s per record                     │    │
│  │                                                          │    │
│  │  Input:                                                  │    │
│  │  • Raw CSV row with typos, inconsistent formats         │    │
│  │                                                          │    │
│  │  Output:                                                 │    │
│  │  • Cleaned JSON with standardized values                │    │
│  │  • Quality score (0-1)                                   │    │
│  │                                                          │    │
│  │  Example:                                                │    │
│  │  "jhon doe, comp sci, 85%" → "John Doe, Computer        │    │
│  │  Science, 8.5"                                           │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  LLM Job #2: Recommendation Generation                  │    │
│  │  File: services/recommendation_engine.py                │    │
│  │                                                          │    │
│  │  Purpose: Generate personalized recommendations         │    │
│  │  Temperature: 0.7 (creative)                            │    │
│  │  Max Tokens: 800                                        │    │
│  │  Processing Time: 1-2s per student                      │    │
│  │                                                          │    │
│  │  Input:                                                  │    │
│  │  • Student profile (GPA, scores, gaps)                  │    │
│  │  • Similar alumni success stories                       │    │
│  │  • Digital wellbeing data                               │    │
│  │                                                          │    │
│  │  Output:                                                 │    │
│  │  • 3-5 recommendations with:                            │    │
│  │    - Title, description                                 │    │
│  │    - Impact (High/Medium/Low)                           │    │
│  │    - Estimated points improvement                       │    │
│  │    - Timeline, action steps                             │    │
│  │    - Alumni success story                               │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  LLM Job #3: Voice Assessment Evaluation                │    │
│  │  File: services/voice_evaluation.py                     │    │
│  │                                                          │    │
│  │  Purpose: Score voice interview responses               │    │
│  │  Temperature: 0.3 (consistent scoring)                  │    │
│  │  Max Tokens: 400                                        │    │
│  │  Processing Time: 1-2s per evaluation                   │    │
│  │                                                          │    │
│  │  Input:                                                  │    │
│  │  • Question asked                                       │    │
│  │  • Student's voice response (transcript)                │    │
│  │  • Expected answer key points                           │    │
│  │                                                          │    │
│  │  Output:                                                 │    │
│  │  • Technical accuracy score (0-10)                      │    │
│  │  • Communication clarity score (0-10)                   │    │
│  │  • Depth of understanding score (0-10)                  │    │
│  │  • Completeness score (0-10)                            │    │
│  │  • Detailed feedback                                    │    │
│  │  • Strengths and areas for improvement                  │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  LLM Job #4: Gap Analysis Narratives                    │    │
│  │  File: services/gap_analysis.py                         │    │
│  │                                                          │    │
│  │  Purpose: Generate engaging gap explanations            │    │
│  │  Temperature: 0.7 (engaging narratives)                 │    │
│  │  Max Tokens: 600                                        │    │
│  │  Processing Time: 0.5-1s per narrative                  │    │
│  │                                                          │    │
│  │  Input:                                                  │    │
│  │  • Gap metric (e.g., problem-solving: 2/5 vs 4.2/5)    │    │
│  │  • Student value, alumni average                        │    │
│  │  • Impact level (High/Medium/Low)                       │    │
│  │  • Historical placement data                            │    │
│  │                                                          │    │
│  │  Output:                                                 │    │
│  │  • Engaging narrative explaining why gap matters        │    │
│  │  • Real-world impact data (salary, placement rates)     │    │
│  │  • Specific numeric target                              │    │
│  │  • Realistic timeline                                   │    │
│  │  • Motivational tone                                    │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐    │
│  │  LLM Job #5: Skill Market Demand Analysis               │    │
│  │  File: services/skill_demand_analysis.py                │    │
│  │                                                          │    │
│  │  Purpose: Analyze skill market demand & assign weights  │    │
│  │  Temperature: 0.2 (data-driven, consistent)             │    │
│  │  Max Tokens: 300                                        │    │
│  │  Processing Time: 0.5-1s per skill                      │    │
│  │  Cache: 30 days (avoid repeated calls)                  │    │
│  │                                                          │    │
│  │  Input:                                                  │    │
│  │  • Skill name (e.g., "Python", "jQuery")                │    │
│  │  • Student's major                                      │    │
│  │  • Current year (2026)                                  │    │
│  │  • Recent alumni placement data                         │    │
│  │                                                          │    │
│  │  Output:                                                 │    │
│  │  • Market weight: 0.5x, 1.0x, or 2.0x                   │    │
│  │  • Reasoning (job market trends, salary data)           │    │
│  │  • Demand indicator (🔥 High, ⚡ Medium, ❄️ Low)        │    │
│  │  • Recommendation (if low demand skill)                 │    │
│  │                                                          │    │
│  │  Example:                                                │    │
│  │  Python → 2.0x (High demand in AI/ML, 78% of jobs)     │    │
│  │  jQuery → 0.5x (Declining, replaced by React/Vue)      │    │
│  └─────────────────────────────────────────────────────────┘    │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### 7.2 LLM Request/Response Flow

```
┌──────────────┐                                                
│  Service     │                                                
│  (Python)    │                                                
└──────┬───────┘                                                
       │                                                        
       │ 1. Build prompt with context                           
       │                                                        
       ▼                                                        
┌──────────────────────────────────────────────────────┐       
│  LLM Service Helper                                  │       
│                                                      │       
│  def call_llm(prompt, temperature, max_tokens):      │       
│      payload = {                                     │       
│          "model": "llama3.1:8b",                     │       
│          "prompt": prompt,                           │       
│          "temperature": temperature,                 │       
│          "max_tokens": max_tokens,                   │       
│          "stream": False                             │       
│      }                                               │       
│                                                      │       
│      # Check Redis cache first                       │       
│      cache_key = hash(prompt)                        │       
│      cached = redis.get(f"llm:cache:{cache_key}")   │       
│      if cached:                                      │       
│          return json.loads(cached)                   │       
│                                                      │       
│      # Call Ollama API                               │       
│      response = requests.post(                       │       
│          "http://localhost:11434/api/generate",      │       
│          json=payload,                               │       
│          timeout=10                                  │       
│      )                                               │       
│                                                      │       
│      # Cache response (30 days)                      │       
│      redis.setex(                                    │       
│          f"llm:cache:{cache_key}",                   │       
│          2592000,  # 30 days                         │       
│          response.text                               │       
│      )                                               │       
│                                                      │       
│      return response.json()                          │       
└──────┬───────────────────────────────────────────────┘       
       │                                                        
       │ 2. POST to Ollama                                      
       │                                                        
       ▼                                                        
┌──────────────────────────────────────────────────────┐       
│  Ollama Server                                       │       
│  http://localhost:11434/api/generate                 │       
│                                                      │       
│  1. Load model into GPU memory (if not loaded)       │       
│  2. Tokenize prompt                                  │       
│  3. Run inference on RTX 4060                        │       
│  4. Generate tokens (25-67 tokens/second)            │       
│  5. Detokenize response                              │       
│  6. Return JSON                                      │       
│                                                      │       
│  Response:                                           │       
│  {                                                   │       
│    "model": "llama3.1:8b",                           │       
│    "created_at": "2026-02-17T10:30:00Z",             │       
│    "response": "Generated text...",                  │       
│    "done": true,                                     │       
│    "context": [...],                                 │       
│    "total_duration": 1234567890,                     │       
│    "load_duration": 123456,                          │       
│    "prompt_eval_count": 50,                          │       
│    "prompt_eval_duration": 234567,                   │       
│    "eval_count": 100,                                │       
│    "eval_duration": 987654                           │       
│  }                                                   │       
└──────┬───────────────────────────────────────────────┘       
       │                                                        
       │ 3. Return response                                     
       │                                                        
       ▼                                                        
┌──────────────────────────────────────────────────────┐       
│  Service (Python)                                    │       
│                                                      │       
│  4. Parse response                                   │       
│  5. Validate output                                  │       
│  6. Return to caller                                 │       
└──────────────────────────────────────────────────────┘       

Performance Metrics:
• Cache Hit: <10ms
• Cache Miss: 0.5-2s (depending on job)
• GPU Utilization: 100% during inference
• Memory Usage: ~5GB VRAM
• Concurrent Requests: 8+ (ThreadPoolExecutor)
```

---

## 8. Complete Request Flow

### 8.1 End-to-End: Student Views Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          COMPLETE REQUEST FLOW                               │
│                    Student Dashboard Load (First Time)                       │
└─────────────────────────────────────────────────────────────────────────────┘

TIME: 0ms
┌──────────────┐
│   Student    │  1. Opens browser, navigates to /dashboard
│   Browser    │
└──────┬───────┘
       │
       │ HTTP GET https://trajectory-app.com/dashboard
       │
TIME: 50ms
       ▼
┌──────────────────────────────────────────────────────────────┐
│  React App (Frontend)                                        │
│  • Load React bundle (~500KB gzipped)                        │
│  • Initialize Redux store                                    │
│  • Check authentication (JWT token in localStorage)          │
│  • Render StudentDashboard component                         │
│  • Show loading skeletons                                    │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ 2. API Call: GET /api/students/abc123/dashboard
       │    Headers: Authorization: Bearer <jwt_token>
       │
TIME: 100ms
       ▼
┌──────────────────────────────────────────────────────────────┐
│  FastAPI Backend                                             │
│  • Validate JWT token                                        │
│  • Extract student_id from token                             │
│  • Route to student_router.get_dashboard()                   │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ 3. Check Redis cache
       │    Key: student:dashboard:abc123
       │
TIME: 110ms
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Redis Cache                                                 │
│  • CACHE MISS (first time load)                              │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ 4. Fetch student profile
       │    Query: SELECT * FROM students WHERE id = 'abc123'
       │
TIME: 150ms
       ▼
┌──────────────────────────────────────────────────────────────┐
│  PostgreSQL                                                  │
│  • Return student profile (GPA, attendance, scores, etc.)    │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ 5. Fetch recommendations
       │    Query: SELECT * FROM recommendations 
       │           WHERE student_id = 'abc123' 
       │           ORDER BY generated_at DESC LIMIT 5
       │
TIME: 180ms
       ▼
┌──────────────────────────────────────────────────────────────┐
│  PostgreSQL                                                  │
│  • Return 5 most recent recommendations                      │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ 6. Fetch digital wellbeing data (last 7 days)
       │    Query: SELECT * FROM digital_wellbeing 
       │           WHERE student_id = 'abc123' 
       │           AND date >= NOW() - INTERVAL '7 days'
       │
TIME: 210ms
       ▼
┌──────────────────────────────────────────────────────────────┐
│  PostgreSQL                                                  │
│  • Return 7 days of wellbeing data                           │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ 7. Generate student vector
       │    • Normalize all features (NumPy)
       │    • Create 15-dimensional vector
       │
TIME: 230ms
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Vector Engine (NumPy)                                       │
│  • vector = [0.86, 0.90, 0.48, 0.73, ...]                    │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ 8. Search for similar alumni
       │    POST /collections/alumni_collection/points/search
       │    Body: { vector: [...], limit: 5 }
       │
TIME: 280ms
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Qdrant Vector DB                                            │
│  • HNSW index search (cosine similarity)                     │
│  • Return top 5 similar alumni with scores                   │
│  • [Alumni A: 0.92, Alumni B: 0.88, Alumni C: 0.85, ...]     │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ 9. Fetch alumni details
       │    Query: SELECT * FROM alumni 
       │           WHERE id IN ('alum1', 'alum2', 'alum3')
       │
TIME: 310ms
       ▼
┌──────────────────────────────────────────────────────────────┐
│  PostgreSQL                                                  │
│  • Return alumni profiles (placement, salary, etc.)          │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ 10. Calculate trajectory score
       │     • Weighted average of alumni outcomes
       │     • Weight by similarity scores
       │
TIME: 330ms
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Prediction Engine (Pure Math)                               │
│  • trajectory = (0.92×95 + 0.88×90 + 0.85×65 + ...) / sum    │
│  • trajectory_score = 0.73 (73/100)                          │
│  • confidence_interval = [0.68, 0.78]                        │
│  • placement_likelihood = [65%, 75%]                         │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ 11. Calculate gap analysis
       │     • Compare student vs alumni averages (NumPy)
       │     • Identify top 5 gaps
       │
TIME: 360ms
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Gap Analysis Service                                        │
│  • Gaps: [                                                   │
│      {metric: "problem_solving", gap: -2.2, impact: "High"}, │
│      {metric: "screen_time", gap: +1.2, impact: "Medium"},   │
│      ...                                                     │
│    ]                                                         │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ 12. Generate gap narratives (LLM Job #4)
       │     • Call Ollama for each gap
       │     • Parallel processing (ThreadPoolExecutor)
       │
TIME: 400ms
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Ollama Server (LLM Job #4)                                  │
│  • Process 5 gaps in parallel                                │
│  • Temperature: 0.7                                          │
│  • Generate engaging narratives                              │
│  • Response time: 0.5-1s per narrative                       │
└──────┬───────────────────────────────────────────────────────┘
       │
TIME: 1400ms (1.4 seconds)
       │
       │ 13. Aggregate all data
       │     • Combine profile, scores, recommendations,
       │       wellbeing, alumni, gaps, narratives
       │
       ▼
┌──────────────────────────────────────────────────────────────┐
│  Response Builder                                            │
│  • Build complete JSON response                              │
│  • Cache in Redis (1 hour TTL)                               │
│    Key: student:dashboard:abc123                             │
└──────┬───────────────────────────────────────────────────────┘
       │
       │ 14. Return JSON response (~50KB)
       │
TIME: 1450ms (1.45 seconds)
       ▼
┌──────────────────────────────────────────────────────────────┐
│  React App (Frontend)                                        │
│  • Receive JSON response                                     │
│  • Update Redux store                                        │
│  • Render all components:                                    │
│    - TrajectoryScoreCard (73/100, Good)                      │
│    - ComponentBreakdown (Academic: 90, Behavioral: 48, ...)  │
│    - DigitalWellbeingMetrics (Screen: 6.2h, Focus: 0.65)     │
│    - Recommendations (5 items with LLM-generated text)        │
│    - SimilarAlumni (Top 3 matches with 92%, 88%, 85%)        │
│    - GapAnalysis (5 gaps with LLM narratives)                │
│    - ProgressTracking (30-day chart, achievements)           │
│  • Hide loading skeletons                                    │
│  • Show success notification                                 │
└──────┬───────────────────────────────────────────────────────┘
       │
TIME: 1500ms (1.5 seconds)
       ▼
┌──────────────┐
│   Student    │  Dashboard fully loaded and interactive
│   Browser    │  • All data visible
└──────────────┘  • Charts rendered
                  • Recommendations displayed
                  • Ready for user interaction

═══════════════════════════════════════════════════════════════

PERFORMANCE SUMMARY:
• Total Time: 1.5 seconds (first load)
• Cache Hit Time: <100ms (subsequent loads)
• Database Queries: 4 (PostgreSQL)
• Vector Search: 1 (Qdrant) - 50ms
• LLM Calls: 5 (gap narratives) - 1 second total
• Response Size: ~50KB JSON

BREAKDOWN:
• Frontend Load: 50ms
• Auth & Routing: 50ms
• Database Queries: 110ms
• Vector Search: 70ms
• Math Calculations: 50ms
• LLM Processing: 1000ms (parallel)
• Response Building: 50ms
• Frontend Rendering: 50ms

OPTIMIZATION OPPORTUNITIES:
• Cache hit reduces time to <100ms
• Preload LLM narratives in background
• Use WebSocket for real-time updates
• Lazy load non-critical components
```

---

## 9. Summary

### 9.1 Key Architecture Decisions

**1. Separation of Concerns:**
- Frontend: React (UI/UX)
- Backend: FastAPI (Business Logic)
- Database: PostgreSQL (Relational Data)
- Vector DB: Qdrant (Similarity Search)
- Cache: Redis (Performance)
- LLM: Ollama (AI Features)
- Mobile: React Native (Data Collection)

**2. LLM Integration:**
- Local deployment (zero cloud costs)
- 5 specific jobs (not general-purpose)
- Caching to avoid repeated calls
- Parallel processing for performance
- Fallback mechanisms for reliability

**3. Data Flow:**
- Mobile app → Backend → PostgreSQL (behavioral data)
- Backend → Qdrant (vector search)
- Backend → Ollama (LLM processing)
- Backend → Redis (caching)
- Backend → Frontend (JSON API)

**4. Performance Optimization:**
- Redis caching (1 hour TTL for dashboards)
- Qdrant HNSW index (fast similarity search)
- Parallel LLM processing (ThreadPoolExecutor)
- Mobile app background sync (daily at 2 AM)
- Frontend lazy loading (code splitting)

**5. Scalability:**
- Horizontal scaling: Add more FastAPI instances
- Database: PostgreSQL read replicas
- Vector DB: Qdrant clustering
- LLM: Multiple Ollama instances
- Cache: Redis Cluster

---

**Document Version:** 1.0  
**Last Updated:** February 17, 2026  
**Status:** Complete ✅

**Total Pages:** 20+  
**Total Diagrams:** 15+  
**Coverage:** 100% of system architecture
