# 15-Day MVP Workflow

## Overview

This document outlines the 15-day sprint plan to build a working Trajectory Engine MVP that proves the core concept: predicting student employability using academics, behavioral patterns, and skills data with vector similarity matching.

**Team:** 4 members (Mayur, Arun, Vivek, Sudeep)  
**Goal:** Working demo with core prediction capability  
**Scope:** Simplified features, mock data, basic UI, local LLM integration

---

## Sprint Breakdown

### Phase 1: Foundation & Setup (Days 1-3)

#### Day 1: Environment Setup & Architecture Planning
**Team Focus:** Everyone

**Morning (4 hours):**
- Set up development environment (Python 3.10+, Node.js, PostgreSQL)
- Install Ollama and download Llama 3.1 8B model
- Test GPU availability (RTX 4060) and verify LLM response time
- Create GitHub repository and set up version control
- Initialize FastAPI backend project structure
- Initialize React frontend project (Vite + React)

**Afternoon (4 hours):**
- Set up PostgreSQL database and create initial schema
- Install Qdrant vector database (Docker or local)
- Test Qdrant connection and basic vector operations
- Create API project structure (routes, services, models)
- Set up CORS and basic middleware
- First team sync: Review architecture diagram

**Deliverables:**
- ✅ Working dev environment for all team members
- ✅ Ollama running with Llama 3.1 8B (test response time <1s)
- ✅ PostgreSQL + Qdrant running locally
- ✅ Basic FastAPI app responding on localhost:8000
- ✅ Basic React app running on localhost:5173

---

#### Day 2: Database Schema & Core Models
**Lead:** Arun (Backend), Support: Mayur

**Morning (4 hours):**
- Design and implement PostgreSQL schema:
  - `users` table (id, email, password_hash, role)
  - `students` table (id, user_id, name, gpa, attendance, semester, major)
  - `alumni` table (id, name, gpa, attendance, major, company_tier, salary, placement_status)
  - `behavioral_data` table (id, student_id, study_hours, project_count, screen_time, focus_score, sleep_duration, date)
  - `skill_assessments` table (id, student_id, quiz_score, voice_score, final_score, date)
  - `vectors` table (id, entity_id, entity_type, vector_id_qdrant, created_at)

**Afternoon (4 hours):**
- Create SQLAlchemy ORM models for all tables
- Implement database connection pooling
- Create Alembic migrations for schema
- Write database utility functions (CRUD operations)
- Test database operations with sample data

**Deliverables:**
- ✅ Complete database schema implemented
- ✅ SQLAlchemy models for all entities
- ✅ Database migrations working
- ✅ Basic CRUD operations tested

---

#### Day 3: Authentication & Basic API Routes
**Lead:** Arun (Backend), Vivek (Frontend)

**Backend (Arun - 6 hours):**
- Implement user registration endpoint (`POST /api/auth/register`)
- Implement login endpoint with JWT tokens (`POST /api/auth/login`)
- Create password hashing utility (bcrypt)
- Implement JWT middleware for protected routes
- Create role-based access control (student vs admin)
- Test authentication flow with Postman

**Frontend (Vivek - 6 hours):**
- Create login page UI
- Create registration page UI
- Implement authentication context (React Context API)
- Create protected route wrapper
- Implement token storage (localStorage)
- Test login/logout flow

**Deliverables:**
- ✅ Working authentication system (register + login)
- ✅ JWT token generation and validation
- ✅ Frontend login/register pages functional
- ✅ Protected routes working

---

### Phase 2: Core Prediction Engine (Days 4-7)

#### Day 4: Vector Generation & Qdrant Integration
**Lead:** Sudeep (AI), Support: Arun

**Morning (4 hours):**
- Implement vector generation service (`vector_engine.py`):
  - Normalize GPA (0-10 → 0-1)
  - Normalize attendance (0-100 → 0-1)
  - Encode major (one-hot or label encoding)
  - Normalize behavioral metrics (study hours, projects, screen time, focus score, sleep)
  - Normalize skill scores (0-100 → 0-1)
  - Combine into single vector (15-20 dimensions)

**Afternoon (4 hours):**
- Integrate Qdrant Python client
- Create Qdrant collections ("students", "alumni")
- Implement vector storage function (store in Qdrant + reference in PostgreSQL)
- Implement vector update function (when profile changes)
- Test vector generation with sample student data

**Deliverables:**
- ✅ Vector generation working (NumPy-based)
- ✅ Qdrant collections created
- ✅ Vectors stored in Qdrant with metadata
- ✅ Vector generation tested with 10+ sample profiles

---

#### Day 5: Similarity Matching & Trajectory Score
**Lead:** Sudeep (AI), Support: Arun

**Morning (4 hours):**
- Implement similarity matching service (`prediction_engine.py`):
  - Query Qdrant with student vector
  - Use cosine similarity metric
  - Return top 5 similar alumni with scores
  - Filter by major (optional)
  - Handle edge cases (no alumni data)

**Afternoon (4 hours):**
- Implement trajectory score calculation:
  - Map alumni outcomes to scores (Tier1=90-100, Tier2=60-80, Tier3=40-60, Not placed=0-40)
  - Weight alumni scores by similarity
  - Calculate weighted average
  - Return score (0-100) with confidence interval
- Create prediction API endpoint (`POST /api/predict`)
- Test with various student profiles

**Deliverables:**
- ✅ Similarity matching working (Qdrant-based)
- ✅ Trajectory score calculation implemented
- ✅ API endpoint returning predictions
- ✅ Tested with 5+ different student profiles

---

#### Day 6: Alumni Data Import & CSV Processing
**Lead:** Arun (Backend), Support: Mayur

**Morning (4 hours):**
- Create CSV template for alumni data (Excel format)
- Implement CSV parser (`POST /api/admin/import-alumni`)
- Validate CSV data (GPA range, company tier, required fields)
- Handle errors gracefully (report line numbers)
- Store alumni records in PostgreSQL

**Afternoon (4 hours):**
- Trigger vector generation for imported alumni
- Store alumni vectors in Qdrant
- Create admin endpoint to view import history
- Test with sample alumni CSV (50+ records)
- Create downloadable CSV template endpoint

**Deliverables:**
- ✅ Alumni CSV import working
- ✅ Data validation implemented
- ✅ Alumni vectors generated automatically
- ✅ Sample alumni dataset (50+ records) imported

---

#### Day 7: Student Profile Management
**Lead:** Arun (Backend), Vivek (Frontend)

**Backend (Arun - 4 hours):**
- Create student profile endpoints:
  - `GET /api/student/profile` - Get current student profile
  - `PUT /api/student/profile` - Update profile
  - `POST /api/student/behavioral` - Add behavioral data
  - `POST /api/student/skills` - Submit skill assessment
- Trigger vector regeneration on profile update
- Validate input data (GPA 0-10, attendance 0-100)

**Frontend (Vivek - 4 hours):**
- Create student profile page
- Create profile edit form (GPA, attendance, semester, major)
- Create behavioral data input form (study hours, projects)
- Display current profile data
- Test profile update flow

**Deliverables:**
- ✅ Student profile CRUD operations working
- ✅ Profile page UI functional
- ✅ Vector regeneration on profile update
- ✅ Data validation working

---

### Phase 3: LLM Integration (Days 8-11)

#### Day 8: LLM Job #1 - Data Cleaning
**Lead:** Arun (Backend), Support: Sudeep

**Morning (4 hours):**
- Create Ollama client wrapper (`llm_client.py`)
- Implement connection pooling for LLM requests
- Create prompt template for data cleaning
- Test LLM response time and format

**Afternoon (4 hours):**
- Implement data cleaning service (`data_cleaning.py`):
  - Clean major names (typos, variations)
  - Normalize GPA formats (4.0 scale → 10.0 scale)
  - Standardize skill names
  - Trim whitespace and fix capitalization
- Integrate into CSV import pipeline
- Test with messy sample data

**Deliverables:**
- ✅ Ollama client working (response time <1s)
- ✅ Data cleaning service functional
- ✅ Integrated into alumni import
- ✅ Tested with 20+ messy records

---

#### Day 9: LLM Job #2 - Recommendations
**Lead:** Sudeep (AI), Support: Arun

**Morning (4 hours):**
- Design recommendation prompt template
- Implement recommendation engine (`recommendation_engine.py`):
  - Input: student profile, trajectory score, gap analysis, alumni matches
  - Output: 3-5 actionable recommendations with impact estimates
  - Temperature: 0.7 (creative)
- Create API endpoint (`POST /api/recommendations`)

**Afternoon (4 hours):**
- Test recommendations with various student profiles
- Refine prompts for better quality
- Add fallback template-based recommendations
- Handle LLM timeout/errors gracefully
- Test with 10+ different student scenarios

**Deliverables:**
- ✅ Recommendation generation working
- ✅ Quality recommendations (specific, actionable)
- ✅ API endpoint functional
- ✅ Fallback mechanism tested

---

#### Day 10: LLM Job #3 - Voice Evaluation (Simplified)
**Lead:** Sudeep (AI), Support: Arun

**Morning (4 hours):**
- Simplify voice evaluation for MVP (text-based simulation)
- Create prompt template for evaluating technical answers
- Implement voice evaluation service (`voice_evaluation.py`):
  - Input: question, student answer (text)
  - Output: scores (technical accuracy, clarity, depth, completeness)
  - Temperature: 0.3 (consistent scoring)

**Afternoon (4 hours):**
- Create API endpoint (`POST /api/evaluate-answer`)
- Test with sample Q&A pairs
- Integrate scores into skill assessment
- Update student skill score calculation
- Note: Full VAPI integration deferred to 90-day plan

**Deliverables:**
- ✅ Text-based answer evaluation working
- ✅ Scoring consistent and reasonable
- ✅ Integrated into skill assessment flow
- ✅ Tested with 10+ Q&A pairs

---

#### Day 11: LLM Job #4 & #5 - Gap Narratives & Skill Demand
**Lead:** Sudeep (AI), Support: Arun

**Morning (4 hours):**
- Implement gap analysis calculation (pure math):
  - Compare student metrics to top 3 alumni matches
  - Calculate percentage gaps for each metric
  - Prioritize gaps by impact
- Implement gap narrative generation (`gap_analysis.py`):
  - Input: student profile, alumni averages, gaps
  - Output: engaging narrative explaining gaps
  - Temperature: 0.7 (engaging)

**Afternoon (4 hours):**
- Implement skill market demand analysis (`skill_demand.py`):
  - Input: skill name, major, year
  - Output: market weight (0.5x, 1.0x, 2.0x) + reasoning
  - Temperature: 0.2 (data-driven)
  - Cache results for 30 days
- Create API endpoints for both services
- Test with various skills and student profiles

**Deliverables:**
- ✅ Gap analysis calculation working
- ✅ Gap narratives generated
- ✅ Skill demand analysis functional
- ✅ Both integrated into prediction flow

---

### Phase 4: Frontend Dashboard (Days 12-13)

#### Day 12: Student Dashboard UI
**Lead:** Vivek (Frontend), Support: Mayur

**Morning (4 hours):**
- Create dashboard layout (sidebar + main content)
- Implement trajectory score display (large number + gauge chart)
- Display score interpretation (Low/Moderate/High employability)
- Show confidence interval
- Add loading states

**Afternoon (4 hours):**
- Display student profile data (academic + behavioral)
- Show top 3 similar alumni (anonymized)
- Display recommendations list (with impact badges)
- Add gap analysis section (side-by-side comparison)
- Style with Tailwind CSS or Material-UI

**Deliverables:**
- ✅ Dashboard UI complete
- ✅ Trajectory score displayed prominently
- ✅ Recommendations visible
- ✅ Gap analysis shown
- ✅ Responsive design

---

#### Day 13: Admin Dashboard & Analytics
**Lead:** Vivek (Frontend), Support: Arun

**Morning (4 hours):**
- Create admin dashboard layout
- Display aggregate statistics:
  - Total students and alumni count
  - Average trajectory score
  - Score distribution chart (0-40, 41-70, 71-100)
- Add CSV upload interface for alumni import
- Show import history and errors

**Afternoon (4 hours):**
- Add filtering by major and semester
- Display most common recommendations
- Create alumni data table (view imported records)
- Add CSV template download button
- Test admin workflows

**Deliverables:**
- ✅ Admin dashboard functional
- ✅ Analytics displayed
- ✅ CSV import UI working
- ✅ Filtering and data tables functional

---

### Phase 5: Testing & Demo Prep (Days 14-15)

#### Day 14: Integration Testing & Bug Fixes
**Team Focus:** Everyone

**Morning (4 hours):**
- End-to-end testing:
  - Student registration → profile creation → prediction → recommendations
  - Admin login → CSV import → view analytics
- Test all LLM jobs with various inputs
- Test edge cases (no alumni data, incomplete profiles)
- Fix critical bugs

**Afternoon (4 hours):**
- Performance testing:
  - Test with 100+ student profiles
  - Measure LLM response times
  - Test Qdrant query performance
- Optimize slow queries
- Add error handling and user-friendly messages
- Test on different browsers

**Deliverables:**
- ✅ All critical bugs fixed
- ✅ End-to-end flows working
- ✅ Performance acceptable (<2s for predictions)
- ✅ Error handling robust

---

#### Day 15: Demo Preparation & Documentation
**Team Focus:** Everyone

**Morning (4 hours):**
- Create demo dataset:
  - 50+ alumni records (varied outcomes)
  - 10+ student profiles (different scenarios)
- Prepare demo script (user stories to showcase)
- Create presentation slides (problem, solution, demo, results)
- Record demo video (backup)

**Afternoon (4 hours):**
- Write README.md (setup instructions, architecture)
- Document API endpoints (Postman collection or Swagger)
- Create user guide (how to use the system)
- Final team rehearsal
- Deploy to local demo environment

**Deliverables:**
- ✅ Demo-ready system with sample data
- ✅ Presentation prepared
- ✅ Documentation complete
- ✅ Team ready for demo

---

## MVP Scope Summary

### ✅ Included in 15-Day MVP:

1. **Core Prediction Engine:**
   - Vector generation (NumPy)
   - Similarity matching (Qdrant)
   - Trajectory score calculation
   - Confidence intervals

2. **LLM Integration (5 Jobs):**
   - Data cleaning
   - Recommendations
   - Voice evaluation (text-based)
   - Gap narratives
   - Skill market demand analysis

3. **Data Management:**
   - Alumni CSV import
   - Student profile management
   - Basic behavioral data input (manual)

4. **User Interface:**
   - Student dashboard (trajectory score, recommendations, gap analysis)
   - Admin dashboard (analytics, CSV import)
   - Authentication (login/register)

5. **Infrastructure:**
   - Local Ollama + Llama 3.1 8B
   - PostgreSQL database
   - Qdrant vector database
   - FastAPI backend
   - React frontend

### ❌ Deferred to 90-Day Plan:

1. **Mobile App:**
   - React Native app
   - Automatic digital wellbeing data collection
   - Background sync

2. **Advanced Features:**
   - Real-time ERP integration
   - Full VAPI voice call integration
   - Gamification (badges, streaks, leaderboards)
   - Weekly behavioral reports
   - Advanced analytics

3. **Production Features:**
   - Deployment (cloud hosting)
   - CI/CD pipeline
   - Monitoring and logging
   - Security hardening
   - Load testing

---

## Daily Standup Format

**Time:** 9:00 AM (15 minutes)

**Each team member shares:**
1. What I completed yesterday
2. What I'm working on today
3. Any blockers or help needed

**Project Lead (Mayur) tracks:**
- Overall progress vs timeline
- Risk items
- Dependencies between team members

---

## Success Criteria for MVP Demo

**Must Have:**
1. ✅ Student can register, create profile, and see trajectory score
2. ✅ Trajectory score is calculated using vector similarity (not random)
3. ✅ Recommendations are generated by LLM and displayed
4. ✅ Admin can import alumni CSV and see analytics
5. ✅ All 5 LLM jobs working (data cleaning, recommendations, voice eval, gap narratives, skill demand)
6. ✅ System runs entirely on local hardware (no cloud APIs)

**Nice to Have:**
1. ✅ Gap analysis with visual comparison
2. ✅ Skill demand indicators (🔥 High, ⚡ Medium, ❄️ Low)
3. ✅ Confidence intervals displayed
4. ✅ Responsive UI design

**Demo Flow:**
1. Show admin importing alumni data (CSV upload)
2. Show student registration and profile creation
3. Show trajectory score calculation (explain the math)
4. Show LLM-generated recommendations
5. Show gap analysis and skill demand weighting
6. Show admin analytics dashboard
7. Explain cost savings ($0 vs cloud APIs)

---

## Risk Mitigation

**Risk 1: LLM performance issues**
- Mitigation: Test Ollama on Day 1, optimize prompts, implement fallbacks

**Risk 2: Team member unavailable**
- Mitigation: Cross-train on critical components, document code daily

**Risk 3: Qdrant integration complexity**
- Mitigation: Start with simple in-memory vectors, migrate to Qdrant by Day 5

**Risk 4: Scope creep**
- Mitigation: Strict "MVP only" rule, defer all non-essential features

**Risk 5: Integration issues**
- Mitigation: Daily integration testing, clear API contracts

---

## Team Roles & Responsibilities

**Mayur (Project Lead):**
- Overall coordination and timeline management
- Demo preparation and presentation
- Quality assurance and testing
- Documentation review

**Arun (Backend + Data):**
- Database schema and models
- API endpoints (auth, profiles, import)
- LLM client integration
- Data cleaning service

**Vivek (Frontend):**
- React UI components
- Dashboard layouts
- API integration
- Responsive design

**Sudeep (AI/ML):**
- Vector generation and similarity matching
- LLM prompt engineering (4 jobs)
- Prediction engine logic
- Performance optimization

---

## Tech Stack

**Backend:**
- Python 3.10+
- FastAPI
- SQLAlchemy (ORM)
- PostgreSQL
- Qdrant (vector DB)
- Ollama + Llama 3.1 8B
- NumPy, scikit-learn

**Frontend:**
- React 18
- Vite
- Tailwind CSS or Material-UI
- Axios (API calls)
- React Router

**Infrastructure:**
- Local development (Lenovo Legion 5i)
- Git + GitHub
- Postman (API testing)

---

## End of 15-Day MVP Workflow
