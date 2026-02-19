# Requirements Document

## Introduction

The Trajectory Engine MVP is a 15-day internship project designed to prove the core concept of a "Predictive Behavioral Digital Twin" for student career outcomes. Rather than building the full ambitious vision described in the PRD, this MVP focuses on demonstrating the fundamental prediction capability using simplified data inputs and a basic web interface.

The MVP will validate whether we can meaningfully predict student employability by combining three key components: **Academics** (GPA, attendance), **Behavioral** patterns (study hours, projects, screen time, app usage, sleep), and **Skills** (technical assessments, communication), using vector similarity matching to find patterns between current students and historical alumni employment outcomes.

**Team Context:**
- 4 team members (Mayur, Arun, Vivek, Sudeep)
- 15-day timeline
- Mixed skill levels (junior developers with specific strengths)
- Goal: Working demo that proves the concept, not production-ready system

**Scope Constraints:**
- No full social feed ("The Mirror") - simple web dashboard instead
- Simplified 3-component data model (Academics + Behavioral + Skills) instead of 5 layers
- Mock ERP integration initially (CSV/JSON import, not live SQL sync)
- Basic vector similarity matching (no complex Monte Carlo simulations)
- Simple recommendation system based on alumni patterns
- Mobile app integration for behavioral data collection (screen time, app activity, sleep patterns)

**LLM Integration:**
- **Model**: Llama 3.1 8B (8 billion parameters, ~4.7GB size)
- **Deployment**: Local via Ollama (runs on Lenovo Legion 5i with RTX 4060)
- **Hardware**: RTX 4060 (8GB VRAM), i7 14th Gen HX (14 cores), 16GB RAM
- **Performance**: 0.5-1 second per request, handles 8+ simultaneous requests
- **Cost**: $0 (no cloud API costs)
- **LLM Jobs**: 4 specific jobs (data cleaning, recommendations, voice evaluation, gap narratives) + 1 new job (skill market demand analysis)
- **Prediction Engine**: Uses cosine similarity (NumPy/scikit-learn), NOT LLM

## Glossary

- **System**: The Trajectory Engine MVP web application
- **Student**: A current college student using the system to view their career trajectory
- **Alumni**: A graduated student whose historical data is used for predictions
- **Profile**: A student's academic and behavioral data representation
- **Trajectory_Score**: A numerical score (0-100) representing predicted employability and career success probability. This score indicates how likely a student is to secure quality employment based on their academic performance, behavioral patterns, and digital wellbeing habits compared to successful alumni
- **Vector**: A high-dimensional numerical representation of a student's profile
- **Similarity_Match**: An alumni whose vector is mathematically close to a current student
- **Dashboard**: The web interface where students view their trajectory and recommendations
- **Admin**: A college administrator who manages student data and views analytics
- **Prediction_Engine**: The backend service that calculates trajectory scores and matches (uses cosine similarity, NOT LLM)
- **Data_Import**: The process of loading student and alumni data into the system
- **Recommendation**: A suggested action or skill to improve trajectory score
- **LLM**: Large Language Model (Llama 3.1 8B) used for data cleaning, recommendations, voice evaluation, and gap narratives
- **Ollama**: Local LLM server that runs Llama 3.1 8B on the backend server
- **Temperature**: LLM parameter controlling output randomness (0.1 = deterministic, 0.7 = creative)
- **Digital_Wellbeing_Data**: Behavioral data collected from student's mobile device (screen time, app usage, sleep patterns) - this is a sub-component of the Behavioral category
- **Screen_Time**: Total hours per day spent on mobile device
- **App_Activity**: Time spent on different app categories (educational, social media, entertainment, productivity)
- **Sleep_Pattern**: Daily sleep duration and quality metrics
- **Focus_Score**: Calculated metric based on productive app usage vs distracting app usage
- **Mobile_App**: Student-facing mobile application for automatic data collection
- **Skill_Market_Weight**: Multiplier (0.5x to 2.0x) applied to skill scores based on current job market demand. Trending skills (AI/ML, Cloud, React) get higher weight than outdated skills (Flash, jQuery)
- **High_Demand_Skills**: Skills with 2.0x market weight (e.g., Python, React, AWS, AI/ML, DevOps)
- **Low_Demand_Skills**: Skills with 0.5x market weight (e.g., Flash, jQuery, legacy PHP, VB.NET)

## Requirements

### How Trajectory Score (Employability) is Calculated

The **Trajectory Score** is a 0-100 score that represents a student's employability - their likelihood of securing quality employment. 

**Formula: Trajectory Score = Academics + Behavioral + Skills**

The score is calculated using the following process:

**Step 1: Data Collection (3 Components)**

1. **Academics (33% weight)**
   - GPA (0-10 scale)
   - Attendance percentage (0-100%)
   - Semester progress
   - Major/specialization

2. **Behavioral (33% weight)**
   - Study hours per week
   - Project completion count
   - Screen time (from mobile app)
   - App usage patterns - Focus Score (productive vs distracting apps)
   - Sleep duration and quality
   - Consistency and discipline metrics

3. **Skills (33% weight)**
   - Technical skill assessment scores (quiz-based)
   - Voice interview evaluation scores
   - Communication and soft skills
   - Domain-specific competencies
   - **Skill market demand weighting**: Trending skills (AI/ML, Cloud, React) get 2.0x weight, outdated skills (Flash, jQuery) get 0.5x weight

**Step 2: Vector Generation (Pure Math - NumPy)**
- Convert all student data into a numerical vector
- Normalize all values to 0-1 scale
- Example vector: [GPA_norm, attendance_norm, study_hours_norm, projects_norm, screen_time_norm, focus_score_norm, sleep_norm, skill_scores_norm]

**Step 3: Similarity Matching (Pure Math - scikit-learn)**
- Compare student vector to all alumni vectors using cosine similarity
- Find top 5 most similar alumni (those with similar academic + behavioral + skills patterns)
- Each match gets a similarity score (0-1)

**Step 4: Trajectory Score Calculation (Pure Math - Weighted Average)**
- Look at employment outcomes of matched alumni (placement status, company tier, salary)
- Weight each alumni's outcome by their similarity score
- Calculate weighted average to get final trajectory score (0-100)
- Higher score = Higher employability

**Example:**
```
Student Profile:
- Academics: GPA 7.5, 80% attendance → Academic Score: 75/100
- Behavioral: 20 study hours/week, 3 projects, 6 hours screen time, Focus Score 0.7, 7 hours sleep → Behavioral Score: 70/100
- Skills: 
  * Python (proficiency 85/100, market weight 2.0x) = 170 weighted points
  * React (proficiency 80/100, market weight 2.0x) = 160 weighted points
  * AWS (proficiency 75/100, market weight 2.0x) = 150 weighted points
  * Weighted Skill Score: (170+160+150)/3 = 160/200 = 80/100

Overall Profile Score: (75 + 70 + 80) / 3 = 75/100

Similar Alumni Found:
1. Alumni A (similarity 0.92): Placed at Google (Tier 1), 18 LPA → Outcome Score: 95
2. Alumni B (similarity 0.88): Placed at Microsoft (Tier 1), 16 LPA → Outcome Score: 90
3. Alumni C (similarity 0.85): Placed at Infosys (Tier 2), 8 LPA → Outcome Score: 65
4. Alumni D (similarity 0.80): Placed at Startup (Tier 3), 6 LPA → Outcome Score: 55
5. Alumni E (similarity 0.75): Not placed → Outcome Score: 20

Trajectory Score = (0.92×95 + 0.88×90 + 0.85×65 + 0.80×55 + 0.75×20) / (0.92+0.88+0.85+0.80+0.75)
                 = 73/100

Interpretation: Score 73 = High employability, strong likelihood of Tier 1/2 placement
```

**Comparison Example - Impact of Skill Demand Weighting:**
```
Student A (Trending Skills):
- Python (85/100, 2.0x), React (80/100, 2.0x), AWS (75/100, 2.0x)
- Weighted Skill Score: 80/100
- Trajectory Score: 75/100 → High employability

Student B (Outdated Skills):
- PHP (90/100, 0.5x), jQuery (85/100, 0.5x), Flash (80/100, 0.5x)
- Weighted Skill Score: 42.5/100
- Trajectory Score: 52/100 → Moderate employability (despite higher proficiency!)

Key Insight: Student A with lower proficiency but trending skills has better employability than Student B with higher proficiency but outdated skills.
```

**What the Score Means:**
- **0-40**: Low employability - At-risk, needs significant improvement in academics, behavior, or skills
- **41-70**: Moderate employability - Average placement likelihood, mid-tier companies
- **71-100**: High employability - Strong placement likelihood, top-tier companies (FAANG, product companies)

**Key Insight:** The trajectory score combines ALL three components equally:
- **Academics alone is not enough** - A student with 9.0 GPA but poor behavioral habits (low sleep, high social media usage) and weak skills may score lower than a student with 7.5 GPA but excellent behavior and strong skills
- **Behavioral patterns matter** - Digital wellbeing data (screen time, app usage, sleep) is a key part of behavioral assessment
- **Skills validation is critical** - Self-reported skills are verified through quiz and voice assessments
- **Market demand matters more than proficiency** - A student with 85/100 proficiency in trending skills (Python, React, AWS) will score higher than a student with 90/100 proficiency in outdated skills (PHP, jQuery, Flash)
- **Skill weighting formula**: High-demand skills get 2.0x multiplier, medium-demand get 1.0x, low-demand get 0.5x

---

### Requirements

### Requirement 1: Student Profile Management

**User Story:** As a student, I want to create and view my profile with academic and basic behavioral data, so that the system can analyze my career trajectory.

#### Acceptance Criteria

1. WHEN a student registers, THE System SHALL create a profile with academic fields (GPA, attendance percentage, semester, major)
2. WHEN a student updates their profile, THE System SHALL validate that GPA is between 0.0 and 10.0
3. WHEN a student updates their profile, THE System SHALL validate that attendance is between 0 and 100 percent
4. THE System SHALL store basic behavioral data (study hours per week, project completion count, skill assessment scores)
5. WHEN a student views their profile, THE System SHALL display all academic and behavioral data in a readable format

### Requirement 1A: Digital Wellbeing Data Collection

**User Story:** As a student, I want the mobile app to automatically collect my digital wellbeing data (screen time, app activity, sleep patterns), so that the system can provide more accurate career predictions based on my daily habits.

**Technical Note:** This requires a mobile app (Android/iOS) with background data collection permissions. Data is synced to backend API daily.

#### Acceptance Criteria

**Screen Time Tracking:**
1. WHEN the mobile app is installed, THE System SHALL request permission to access screen time data
2. THE System SHALL track total daily screen time in hours
3. THE System SHALL categorize screen time by time of day (morning, afternoon, evening, night)
4. THE System SHALL calculate average weekly screen time
5. THE System SHALL flag excessive screen time (>8 hours/day) as a potential concern

**App Activity Tracking:**
6. THE System SHALL categorize apps into: Educational (coding, learning), Social Media (Instagram, Twitter), Entertainment (YouTube, Netflix), Productivity (calendar, notes), Communication (email, messaging)
7. THE System SHALL track time spent per app category daily
8. THE System SHALL calculate a Focus Score = (Educational + Productivity time) / (Social Media + Entertainment time)
9. WHEN Focus Score is below 0.5, THE System SHALL flag it as low productivity
10. THE System SHALL identify top 5 most-used apps and their categories

**Sleep Pattern Monitoring:**
11. THE System SHALL integrate with device sleep tracking (Android Digital Wellbeing / iOS Screen Time)
12. THE System SHALL record daily sleep duration in hours
13. THE System SHALL track sleep consistency (bedtime and wake time variance)
14. WHEN sleep duration is below 6 hours, THE System SHALL flag it as insufficient sleep
15. THE System SHALL calculate average weekly sleep duration

**Data Privacy and Security:**
16. THE System SHALL encrypt all digital wellbeing data in transit and at rest
17. THE System SHALL allow students to pause data collection at any time
18. THE System SHALL provide a dashboard showing what data is being collected
19. THE System SHALL allow students to delete their digital wellbeing data
20. THE System SHALL NOT share individual student data with third parties

**Data Synchronization:**
21. THE System SHALL sync digital wellbeing data to backend API once per day (overnight)
22. WHEN internet is unavailable, THE System SHALL queue data locally and sync when connection is restored
23. THE System SHALL display last sync timestamp in the mobile app
24. WHEN sync fails 3 times, THE System SHALL notify the student

### Requirement 1B: Behavioral Pattern Analysis

**User Story:** As the system, I want to analyze digital wellbeing patterns to identify correlations with academic success, so that I can provide data-driven recommendations.

**Technical Note:** This uses statistical analysis (NumPy/Pandas) to find correlations. NO LLM is used for pattern analysis.

#### Acceptance Criteria

1. WHEN analyzing student data, THE System SHALL calculate correlation between screen time and GPA
2. THE System SHALL calculate correlation between Focus Score and trajectory score
3. THE System SHALL calculate correlation between sleep duration and academic performance
4. THE System SHALL identify optimal ranges for each metric based on successful alumni patterns
5. WHEN a student's metrics fall outside optimal ranges, THE System SHALL flag them for recommendations
6. THE System SHALL generate weekly behavioral reports showing trends over time
7. THE System SHALL compare student's behavioral patterns to successful alumni in their major
8. THE System SHALL identify "at-risk" patterns (high social media usage + low sleep + declining GPA)

### Requirement 2: Alumni Data Import with Outcome Quality Metrics

**User Story:** As an admin, I want to import historical alumni data with detailed outcome quality metrics, so that the system can predict not just "placement" but "quality of placement" for current students.

#### Acceptance Criteria

1. WHEN an admin uploads a CSV file with alumni data, THE System SHALL parse and validate the file format
2. THE System SHALL require alumni records to contain academic data (GPA, attendance, major) and detailed outcome data (placement status, company tier, role title, salary range, role-to-major match score)
3. THE System SHALL validate company tier as one of: "Tier1" (FAANG/Top), "Tier2" (Mid-size/Product), "Tier3" (Service/Startup)
4. THE System SHALL validate role-to-major match score as a percentage (0-100) indicating how well the job aligns with the student's major
5. WHEN alumni data contains invalid values, THE System SHALL reject the record and report the error with specific field details
6. THE System SHALL store successfully imported alumni records in the database
7. WHEN import completes, THE System SHALL display a summary showing total records imported, average company tier, and any errors

### Requirement 3: Vector Representation Generation

**User Story:** As the system, I want to convert student profiles into numerical vectors and store them in a vector database, so that I can efficiently perform similarity searches at scale.

**Technical Note:** This is a pure mathematical operation using NumPy for vector generation. Vectors are stored in a vector database (Pinecone/Qdrant/Chroma) for fast similarity search. NO LLM is used for vector generation or similarity matching.

**Vector Components:** Academics (33%) + Behavioral (33%) + Skills (33%)

#### Acceptance Criteria

1. WHEN a student profile is created or updated, THE System SHALL generate a vector representation using NumPy
2. THE System SHALL include academic features in the vector (normalized GPA, normalized attendance, major encoding) - 33% weight
3. THE System SHALL include behavioral features in the vector (normalized study hours, project count, screen time, Focus Score, sleep duration) - 33% weight
4. THE System SHALL include skills features in the vector (quiz scores, voice assessment scores, technical competencies) - 33% weight
5. THE System SHALL normalize all vector components to a 0-1 scale
6. THE System SHALL store the vector in a vector database (Pinecone, Qdrant, or Chroma) with metadata (student_id, major, graduation_year)
7. THE System SHALL also store vector reference in PostgreSQL student profile for data integrity
8. WHEN digital wellbeing data is unavailable, THE System SHALL use default values for behavioral metrics (neutral impact on prediction)
9. WHEN skills assessment is incomplete, THE System SHALL use partial scores with confidence penalty

### Requirement 3A: Vector Database Integration

**User Story:** As the system, I want to use a vector database for storing and querying student/alumni vectors, so that similarity searches are fast and scalable even with thousands of students.

**Technical Note:** Vector databases are optimized for similarity search using specialized indexing (HNSW, IVF). Much faster than computing cosine similarity in PostgreSQL.

**Recommended Options:**
- **Qdrant** (Open-source, self-hosted, free) - RECOMMENDED for MVP
- **Chroma** (Open-source, embedded, free)
- **Pinecone** (Cloud, paid, but has free tier)

#### Acceptance Criteria

**Vector Database Setup:**
1. THE System SHALL use Qdrant as the vector database (self-hosted on same server as backend)
2. THE System SHALL create two collections: "students" and "alumni"
3. THE System SHALL configure vector dimensions based on feature count (e.g., 15-20 dimensions)
4. THE System SHALL use cosine similarity as the distance metric

**Vector Storage:**
5. WHEN a student vector is generated, THE System SHALL store it in Qdrant with:
   - Vector: numerical array
   - Payload: {student_id, name, major, semester, gpa, attendance, trajectory_score}
6. WHEN an alumni vector is generated, THE System SHALL store it in Qdrant with:
   - Vector: numerical array
   - Payload: {alumni_id, name, major, graduation_year, company_tier, salary, placement_status}
7. THE System SHALL assign unique IDs to each vector (UUID)

**Vector Search:**
8. WHEN finding similar alumni for a student, THE System SHALL query Qdrant with student vector
9. THE System SHALL request top 5 most similar vectors with similarity scores
10. THE System SHALL filter results by major (optional) to find relevant alumni
11. THE System SHALL return results in <100ms for typical queries
12. WHEN Qdrant is unavailable, THE System SHALL fall back to PostgreSQL with in-memory cosine similarity (slower but functional)

**Vector Updates:**
13. WHEN a student's profile is updated, THE System SHALL regenerate and update their vector in Qdrant
14. THE System SHALL maintain vector version history (optional for MVP)
15. THE System SHALL support batch vector updates for bulk imports

**Performance:**
16. THE System SHALL handle 1000+ student vectors with <100ms query time
17. THE System SHALL handle 500+ alumni vectors with <50ms query time
18. THE System SHALL use HNSW index for fast approximate nearest neighbor search
19. THE System SHALL monitor Qdrant performance (query time, memory usage)

**Data Consistency:**
20. THE System SHALL keep PostgreSQL and Qdrant in sync (PostgreSQL = source of truth for profile data, Qdrant = optimized for vector search)
21. WHEN PostgreSQL data changes, THE System SHALL update corresponding Qdrant vector
22. THE System SHALL provide admin endpoint to rebuild all vectors from PostgreSQL if Qdrant data is lost

### Requirement 4: Similarity Matching

**User Story:** As the system, I want to find alumni who are similar to current students using vector database search, so that I can predict outcomes based on historical patterns.

**Technical Note:** This uses Qdrant vector database for fast similarity search with cosine similarity metric. NO LLM is used for prediction or similarity calculation.

#### Acceptance Criteria

1. WHEN calculating similarity for a student, THE System SHALL query Qdrant vector database with the student's vector
2. THE System SHALL use cosine similarity as the distance metric
3. THE System SHALL return the top 5 most similar alumni matches from Qdrant
4. THE System SHALL optionally filter by major to find relevant alumni
5. WHEN multiple alumni have identical similarity scores, THE System SHALL order them by recency (most recent graduation year first)
6. THE System SHALL include the similarity score (0-1) with each match
7. WHEN no alumni data exists in Qdrant, THE System SHALL return an empty match list
8. THE System SHALL complete similarity search in <100ms using Qdrant's HNSW index
9. WHEN Qdrant is unavailable, THE System SHALL fall back to PostgreSQL with in-memory cosine similarity calculation (slower)

### Requirement 5: Trajectory Score Calculation

**User Story:** As a student, I want to see my trajectory score (employability score), so that I understand my predicted career success probability and job placement likelihood.

**Technical Note:** This uses weighted averaging based on cosine similarity scores. The trajectory score represents employability - how likely the student is to get a quality job. NO LLM is used for trajectory score calculation.

#### Acceptance Criteria

1. WHEN a student has similarity matches, THE System SHALL calculate a trajectory score (employability score) based on matched alumni employment outcomes using weighted averaging
2. THE System SHALL weight alumni outcomes by their similarity scores (more similar alumni have higher weight)
3. THE System SHALL consider alumni placement status, company tier, and salary range when calculating the score
4. THE System SHALL produce a trajectory score between 0 and 100, where:
   - 0-40: Low employability (at-risk, needs significant improvement)
   - 41-70: Moderate employability (average placement likelihood)
   - 71-100: High employability (strong placement likelihood, top companies)
5. WHEN a student has high GPA, good behavioral patterns, and matches successful alumni, THE System SHALL produce a score above 70
6. WHEN a student has low attendance, poor digital wellbeing habits, and matches unsuccessful alumni, THE System SHALL produce a score below 40
7. WHEN no alumni matches exist, THE System SHALL return a default score of 50 with low confidence
8. THE System SHALL explain what the score means in plain language (e.g., "Score 75 means you have strong employability, similar to alumni who got Tier 1 placements")

### Requirement 6: Recommendation Generation (LLM Job #2)

**User Story:** As a student, I want to receive personalized recommendations, so that I know what actions to take to improve my trajectory.

**LLM Integration:** This requirement uses Llama 3.1 8B via Ollama for generating personalized, actionable recommendations.

**LLM Parameters:**
- Model: llama3.1:8b
- Temperature: 0.7 (higher for creative, varied recommendations)
- Max Tokens: 800
- Processing Time: 1-2 seconds per student

#### Acceptance Criteria

1. WHEN a student's trajectory score is calculated, THE System SHALL use Llama 3.1 8B to generate 3-5 actionable recommendations
2. THE System SHALL provide the LLM with student profile, gap analysis, digital wellbeing data, and similar alumni success stories as context
3. WHEN a student's GPA is below 7.0, THE System SHALL recommend academic improvement actions with specific targets
4. WHEN a student's attendance is below 75%, THE System SHALL recommend attendance improvement with specific targets
5. WHEN a student's project count is below the average of successful alumni, THE System SHALL recommend project-based learning with specific examples
6. WHEN a student's screen time exceeds 8 hours/day, THE System SHALL recommend digital detox strategies with specific time limits
7. WHEN a student's Focus Score is below 0.5, THE System SHALL recommend app usage changes (reduce social media, increase educational apps)
8. WHEN a student's sleep duration is below 6 hours, THE System SHALL recommend sleep hygiene improvements with specific bedtime targets
9. THE System SHALL prioritize recommendations by potential impact on trajectory score (High/Medium/Low)
10. THE System SHALL include estimated impact (+X points) and realistic timelines for each recommendation
11. THE System SHALL reference similar alumni success stories in recommendations for motivation
12. THE System SHALL include behavioral change strategies (e.g., "Use app blockers during study hours", "Set phone to Do Not Disturb after 10 PM")
13. WHEN LLM is unavailable, THE System SHALL fall back to template-based recommendations

### Requirement 7: Student Dashboard

**User Story:** As a student, I want to view my trajectory score (employability score) and recommendations on a dashboard, so that I can track my career readiness and job placement likelihood.

#### Acceptance Criteria

1. WHEN a student logs into the dashboard, THE System SHALL display their current trajectory score (employability score) prominently with clear explanation
2. THE System SHALL display what the score means (e.g., "Score 65: Moderate employability - You're on track for mid-tier placements")
3. THE System SHALL display the student's profile data (academic and behavioral)
4. THE System SHALL display digital wellbeing metrics (screen time, Focus Score, sleep duration) with visual indicators (green/yellow/red)
5. THE System SHALL display weekly trends for screen time, app usage, and sleep patterns using charts
6. THE System SHALL display the list of recommendations with clear action items to improve employability
7. THE System SHALL display the top 3 similar alumni with their employment outcomes (company tier, role, salary range - anonymized)
8. THE System SHALL highlight behavioral patterns that differ from successfully employed alumni (e.g., "Successful alumni average 7.5 hours sleep, you average 5.8 hours")
9. WHEN trajectory data is loading, THE System SHALL show a loading indicator
10. THE System SHALL provide a "Digital Wellbeing Report" section showing app usage breakdown and productivity insights
11. THE System SHALL show predicted placement tier (Tier 1/2/3) based on current trajectory score

### Requirement 8: Admin Analytics Dashboard

**User Story:** As an admin, I want to view aggregate analytics, so that I can understand overall student trajectory patterns.

#### Acceptance Criteria

1. WHEN an admin accesses the analytics dashboard, THE System SHALL display the total count of students and alumni
2. THE System SHALL display the average trajectory score across all students
3. THE System SHALL display a distribution chart showing trajectory score ranges (0-40, 41-70, 71-100)
4. THE System SHALL display the most common recommendations being generated
5. THE System SHALL allow filtering analytics by major or semester

### Requirement 9: Mock ERP Integration

**User Story:** As an admin, I want to import student data from CSV files, so that I can populate the system without building a live ERP connection.

#### Acceptance Criteria

1. WHEN an admin uploads a student CSV file, THE System SHALL parse academic data (student ID, name, GPA, attendance, semester, major)
2. THE System SHALL create or update student profiles based on the imported data
3. WHEN a student ID already exists, THE System SHALL update the existing profile
4. WHEN import completes, THE System SHALL trigger vector regeneration for affected students
5. THE System SHALL provide a downloadable CSV template with required columns

### Requirement 10: Basic Authentication

**User Story:** As a user, I want to log in securely, so that my data is protected.

#### Acceptance Criteria

1. WHEN a user registers, THE System SHALL require email and password
2. THE System SHALL hash passwords before storing them
3. WHEN a user logs in with correct credentials, THE System SHALL create a session token
4. WHEN a user logs in with incorrect credentials, THE System SHALL reject the login and display an error
5. THE System SHALL distinguish between student and admin roles

### Requirement 11: Data Cleaning and Validation (LLM Job #1)

**User Story:** As the system, I want to automatically clean and validate messy input data, so that predictions are based on accurate information.

**LLM Integration:** This requirement uses Llama 3.1 8B via Ollama for intelligent data cleaning and standardization.

**LLM Parameters:**
- Model: llama3.1:8b
- Temperature: 0.1 (low for consistent, deterministic output)
- Max Tokens: 500
- Processing Time: 0.5-1 second per record

#### Acceptance Criteria

1. WHEN data is imported (student or alumni), THE System SHALL use Llama 3.1 8B to detect and fix common typos in major names (e.g., "Comp Sci" → "Computer Science", "Mech Engg" → "Mechanical Engineering")
2. THE System SHALL use the LLM to normalize GPA values to a 10.0 scale if they are provided in different formats (4.0 scale, percentage)
3. WHEN text fields contain extra whitespace or inconsistent capitalization, THE System SHALL use the LLM to trim and standardize them
4. THE System SHALL flag records with suspicious values (GPA > 10, attendance > 100%, negative numbers) for admin review
5. WHEN skill names are imported, THE System SHALL use the LLM to map common variations to standard names (e.g., "ReactJS", "React.js", "React" → "React")
6. THE System SHALL maintain a data quality score for each record indicating the number of corrections applied
7. THE System SHALL return cleaned data in valid JSON format for database storage
8. WHEN LLM is unavailable, THE System SHALL fall back to rule-based cleaning with reduced accuracy

### Requirement 12: Skill Validation (Quiz and Voice-Based) (LLM Job #3)

**User Story:** As a student, I want to validate my skills through both quiz-based and voice-based assessments, so that the system can accurately factor my technical abilities into trajectory predictions.

**LLM Integration:** Voice assessment evaluation uses Llama 3.1 8B via Ollama for scoring technical accuracy, communication clarity, and depth of understanding.

**LLM Parameters:**
- Model: llama3.1:8b
- Temperature: 0.3 (low-medium for consistent scoring)
- Max Tokens: 400
- Processing Time: 1-2 seconds per evaluation

#### Acceptance Criteria

**Quiz-Based Assessment:**
1. WHEN a student accesses the skill assessment, THE System SHALL present a quiz with 10-15 questions covering major-relevant technical skills
2. THE System SHALL include questions for common skills (Programming, Data Structures, Web Development, Databases, Communication)
3. WHEN a student answers a question, THE System SHALL score it on a 1-5 scale (Beginner to Expert)
4. THE System SHALL calculate an overall quiz skill score (0-100) based on quiz responses

**Voice-Based Assessment:**
5. WHEN a student opts for voice verification, THE System SHALL initiate a voice call using VAPI integration
6. THE System SHALL ask 3-5 technical questions verbally based on the student's major and claimed skills
7. THE System SHALL use speech-to-text to capture student responses and Llama 3.1 8B to evaluate answer quality
8. THE System SHALL use the LLM to assess communication clarity, technical accuracy, and confidence level from voice responses
9. THE System SHALL generate a voice assessment score (0-100) combining technical correctness and communication skills
10. THE LLM SHALL provide detailed feedback including scores for technical accuracy (0-10), communication clarity (0-10), depth (0-10), and completeness (0-10)
11. THE LLM SHALL identify specific strengths and areas for improvement in the student's response

**Combined Scoring:**
12. THE System SHALL combine quiz score (60% weight) and voice score (40% weight) into a final skill score
13. THE System SHALL include the final skill score in the student's vector representation
14. WHEN a student completes only quiz or only voice assessment, THE System SHALL use that single score with a confidence penalty
15. WHEN a student retakes either assessment, THE System SHALL update their skill score and recalculate their trajectory
16. WHEN LLM is unavailable for voice evaluation, THE System SHALL use quiz score only with a notification to the student

### Requirement 12A: Skill Market Demand Weighting (LLM Job #5)

**User Story:** As the system, I want to use LLM to dynamically assess skill market demand, so that students with trending/in-demand skills get higher trajectory scores than those with outdated skills.

**LLM Integration:** This requirement uses Llama 3.1 8B via Ollama to analyze skill market demand based on current job market trends, recent alumni placements, and industry patterns.

**LLM Parameters:**
- Model: llama3.1:8b
- Temperature: 0.2 (low for consistent, data-driven assessment)
- Max Tokens: 300
- Processing Time: 0.5-1 second per skill analysis

**Technical Note:** LLM analyzes each skill and assigns EXACTLY ONE of three market weights: **0.5x (Low Demand), 1.0x (Medium Demand), or 2.0x (High Demand)** based on current job market demand, salary trends, and alumni placement success.

#### Acceptance Criteria

**LLM-Based Skill Demand Analysis:**
1. WHEN a student's skills are assessed, THE System SHALL use Llama 3.1 8B to analyze market demand for each skill
2. THE System SHALL provide the LLM with context: skill name, student's major, recent alumni placement data, current year (2026)
3. THE LLM SHALL assign EXACTLY ONE of three market weight multipliers for each skill:
   - **High Demand: 2.0x** - Trending, in-demand skills with strong job market
   - **Medium Demand: 1.0x** - Standard, stable skills with moderate demand
   - **Low Demand: 0.5x** - Outdated, declining skills with weak demand
4. THE LLM SHALL NOT assign any other weight values - ONLY 0.5x, 1.0x, or 2.0x
5. THE LLM SHALL provide reasoning for the weight assignment (e.g., "Python: 2.0x - High demand in AI/ML roles, 40% salary premium, 85% of recent alumni with Python got Tier 1 placements")

**Dynamic Market Assessment:**
6. THE System SHALL cache LLM skill assessments for 30 days to avoid repeated API calls
7. WHEN skill demand changes significantly (new trends emerge), THE System SHALL re-analyze using LLM
8. THE LLM SHALL identify emerging skills that are gaining demand (e.g., "Rust is trending up, recommend learning")
9. THE LLM SHALL flag declining skills (e.g., "jQuery demand declining, consider learning React instead")

**Skill Score Calculation with LLM Weighting:**
10. THE System SHALL calculate weighted skill score = Σ(skill_proficiency × LLM_market_weight) / total_skills
11. THE System SHALL normalize weighted skill score to 0-100 scale
12. THE System SHALL display LLM-generated skill demand indicators (🔥 High, ⚡ Medium, ❄️ Low) next to each skill on dashboard
13. THE System SHALL show LLM reasoning for skill weights when student hovers over indicator

**Examples of LLM Analysis:**
14. LLM Input: "Analyze market demand for skill: Python, major: Computer Science, year: 2026. Assign weight: 0.5x, 1.0x, or 2.0x"
    LLM Output: "Market Weight: **2.0x** (High Demand). Reasoning: Python is critical for AI/ML, data science, and backend development. 78% of job postings require Python. Recent alumni with Python proficiency averaged 14 LPA vs 8 LPA without. Demand growing due to AI boom."

15. LLM Input: "Analyze market demand for skill: jQuery, major: Computer Science, year: 2026. Assign weight: 0.5x, 1.0x, or 2.0x"
    LLM Output: "Market Weight: **0.5x** (Low Demand). Reasoning: jQuery usage declining rapidly. Modern frameworks (React, Vue) have replaced it. Only 8% of job postings mention jQuery. Alumni with only jQuery skills struggled with placements. Recommend learning React or Vue instead."

16. LLM Input: "Analyze market demand for skill: Java, major: Computer Science, year: 2026. Assign weight: 0.5x, 1.0x, or 2.0x"
    LLM Output: "Market Weight: **1.0x** (Medium Demand). Reasoning: Java remains stable for enterprise applications and Android development. 35% of job postings require Java. Standard skill with consistent demand but not trending like Python or React."

**Personalized Skill Recommendations:**
17. THE System SHALL use LLM to recommend skill upgrades based on student's current skills and market trends
18. THE LLM SHALL suggest learning paths (e.g., "You know JavaScript (1.0x). Learn React (2.0x demand) to boost employability by 25%")
19. THE LLM SHALL identify skill gaps compared to successful alumni in student's major
20. THE LLM SHALL prioritize high-impact skills (2.0x) that are easiest to learn given student's existing knowledge

**Fallback Mechanism:**
21. WHEN LLM is unavailable, THE System SHALL use default skill weights: Modern trending skills (2.0x), Standard skills (1.0x), Legacy/outdated skills (0.5x)
22. THE System SHALL log LLM failures and retry skill analysis on next student profile update

### Requirement 13: Engagement Gamification

**User Story:** As a student, I want to see my progress through gamification elements, so that I stay motivated to improve my trajectory.

#### Acceptance Criteria

1. WHEN a student logs in, THE System SHALL display a progress bar showing their trajectory score improvement over time
2. THE System SHALL award achievement badges for milestones (e.g., "First Login", "Profile Complete", "Trajectory Score 70+", "All Recommendations Completed")
3. WHEN a student completes a recommended action, THE System SHALL mark it as complete and show a visual celebration (animation or message)
4. THE System SHALL display a "streak counter" showing consecutive days the student has logged in
5. THE System SHALL show a leaderboard (anonymized) comparing the student's trajectory score to peers in their major
6. WHEN a student earns a new badge, THE System SHALL display a notification

### Requirement 14: Confidence Intervals for Predictions

**User Story:** As a student, I want to see the uncertainty in my trajectory prediction, so that I understand it's a probability, not a guarantee.

#### Acceptance Criteria

1. WHEN displaying a trajectory score, THE System SHALL also display a confidence interval (e.g., "75 ± 10")
2. THE System SHALL calculate confidence based on the number and similarity of alumni matches (more matches = higher confidence)
3. WHEN fewer than 3 similar alumni exist, THE System SHALL display "Low Confidence" and explain that more data is needed
4. WHEN 5+ similar alumni exist with consistent outcomes, THE System SHALL display "High Confidence"
5. THE System SHALL visually represent uncertainty using a range bar or shaded area on charts
6. THE System SHALL explain confidence levels in plain language (e.g., "Based on 8 similar alumni, we're confident your score is between 65-85")

### Requirement 15: Gap Analysis (LLM Job #4)

**User Story:** As a student, I want to see the specific gaps between my profile and successful alumni, so that I know exactly what to improve.

**LLM Integration:** Gap narrative generation uses Llama 3.1 8B via Ollama to convert statistical gaps into compelling, motivating explanations.

**LLM Parameters:**
- Model: llama3.1:8b
- Temperature: 0.7 (higher for engaging narratives)
- Max Tokens: 600
- Processing Time: 0.5-1 second per narrative

#### Acceptance Criteria

1. WHEN a student views their dashboard, THE System SHALL display a gap analysis comparing them to the top 3 successful alumni matches
2. THE System SHALL show side-by-side comparisons for key metrics (GPA, attendance, study hours, project count, skill scores, screen time, Focus Score, sleep duration)
3. WHEN a student's metric is below the alumni average, THE System SHALL highlight it in red and show the percentage gap
4. WHEN a student's metric meets or exceeds the alumni average, THE System SHALL highlight it in green
5. THE System SHALL prioritize gaps by impact (which gaps, if closed, would most improve trajectory score)
6. THE System SHALL provide specific numeric targets (e.g., "Increase study hours from 15 to 22 per week to match successful alumni")
7. THE System SHALL provide digital wellbeing targets (e.g., "Reduce screen time from 9 hours to 6 hours daily", "Increase sleep from 5.5 to 7.5 hours")
8. THE System SHALL use Llama 3.1 8B to generate engaging narratives that explain why each gap matters for career outcomes
9. THE LLM SHALL include real-world impact data (salary differences, placement chances) in gap narratives
10. THE LLM SHALL reference similar alumni success stories to motivate students
11. THE LLM SHALL explain how digital wellbeing impacts academic performance (e.g., "Alumni with 7+ hours sleep had 15% higher GPA")
12. THE LLM SHALL maintain a friendly, supportive, data-driven tone in narratives
13. WHEN LLM is unavailable, THE System SHALL display raw gap statistics without narrative explanations

### Requirement 16: LLM Infrastructure and Performance

**User Story:** As the system, I want to run local LLM operations efficiently and reliably, so that all AI-powered features work smoothly without cloud API costs.

**Technical Context:**
- Hardware: Lenovo Legion 5i with RTX 4060 (8GB VRAM), i7 14th Gen HX (14 cores), 16GB RAM
- LLM Server: Ollama running locally on backend server
- Model: Llama 3.1 8B (8 billion parameters, ~4.7GB model size)
- Expected Performance: 0.5-1 second per request, 8+ simultaneous requests

#### Acceptance Criteria

**Installation and Setup:**
1. THE System SHALL run Ollama server locally on the backend server (localhost:11434)
2. THE System SHALL load Llama 3.1 8B model on startup and keep it in GPU memory
3. THE System SHALL verify GPU availability and use RTX 4060 for all LLM operations
4. WHEN GPU is unavailable, THE System SHALL fall back to CPU processing with a performance warning

**Performance Requirements:**
5. THE System SHALL process LLM requests in 0.5-2 seconds per request under normal load
6. THE System SHALL handle at least 8 simultaneous LLM requests without degradation
7. THE System SHALL use ThreadPoolExecutor with 8 workers for parallel LLM processing
8. THE System SHALL monitor GPU memory usage and ensure it stays below 7GB (leaving 1GB headroom)
9. WHEN GPU memory exceeds 7GB, THE System SHALL queue additional requests

**Reliability and Fallbacks:**
10. WHEN Ollama server is unavailable, THE System SHALL retry connection up to 3 times with exponential backoff
11. WHEN LLM request times out (>10 seconds), THE System SHALL return a fallback response
12. THE System SHALL log all LLM failures with error details for debugging
13. THE System SHALL provide graceful degradation: if LLM fails, use rule-based alternatives

**Monitoring and Optimization:**
14. THE System SHALL track LLM performance metrics (response time, success rate, GPU utilization)
15. THE System SHALL expose health check endpoint (/api/llm/health) showing LLM server status
16. THE System SHALL configure Ollama with optimal settings: num_gpu=1, num_thread=14, num_parallel=8
17. THE System SHALL warm up the LLM on server startup by sending a test request

**Cost and Resource Management:**
18. THE System SHALL run entirely on local hardware with zero cloud API costs
19. THE System SHALL use GPU efficiently to minimize electricity costs
20. THE System SHALL support running all 5 LLM jobs (data cleaning, recommendations, voice evaluation, gap narratives, skill demand analysis) simultaneously

### Requirement 17: Mobile App for Data Collection

**User Story:** As a student, I want a mobile app that automatically collects my digital wellbeing data, so that I don't have to manually enter my screen time and sleep patterns.

**Technical Context:**
- Platform: Android (primary), iOS (future)
- Framework: React Native (cross-platform)
- Permissions: Screen time access, app usage stats, sleep tracking
- Data sync: Daily background sync to backend API

#### Acceptance Criteria

**App Installation and Setup:**
1. WHEN a student downloads the mobile app, THE System SHALL guide them through onboarding
2. THE System SHALL request necessary permissions (screen time, app usage, sleep tracking)
3. THE System SHALL explain what data is collected and why
4. THE System SHALL allow students to opt-in to data collection
5. WHEN permissions are denied, THE System SHALL explain the impact on prediction accuracy

**Data Collection:**
6. THE System SHALL run a background service to collect screen time data hourly
7. THE System SHALL categorize apps automatically based on package name and category
8. THE System SHALL detect sleep periods using screen off time and device motion sensors
9. THE System SHALL store collected data locally in encrypted SQLite database
10. THE System SHALL limit local storage to 30 days of data

**Data Synchronization:**
11. THE System SHALL sync data to backend API once daily at 2 AM (configurable)
12. THE System SHALL use WiFi-only sync by default to save mobile data
13. WHEN sync fails, THE System SHALL retry with exponential backoff (1 hour, 2 hours, 4 hours)
14. THE System SHALL display sync status in app (last synced timestamp, pending data count)
15. WHEN sync is successful, THE System SHALL delete local data older than 7 days

**Privacy and Control:**
16. THE System SHALL provide a "Pause Collection" button to temporarily stop data collection
17. THE System SHALL allow students to view all collected data before it's synced
18. THE System SHALL allow students to delete specific days of data
19. THE System SHALL provide an "Export My Data" feature (JSON format)
20. THE System SHALL display battery usage of the background service

**User Interface:**
21. THE System SHALL display daily screen time summary with breakdown by app category
22. THE System SHALL display weekly trends for screen time, Focus Score, and sleep
23. THE System SHALL show comparison to successful alumni averages
24. THE System SHALL provide quick tips for improving digital wellbeing
25. THE System SHALL send daily notification with screen time summary (optional)

**Performance:**
26. THE System SHALL use less than 5% battery per day for background data collection
27. THE System SHALL use less than 50 MB of storage for local data
28. THE System SHALL complete data sync in under 30 seconds on WiFi
29. THE System SHALL work offline and queue data for later sync


---

## LLM Usage Summary

### What Uses LLM (Llama 3.1 8B):

**LLM Job #1: Data Cleaning (Requirement 11)**
- Purpose: Clean and standardize messy CSV/ERP data
- Temperature: 0.1 (deterministic)
- Processing Time: 0.5-1 second per record
- Example: "jhon doe, comp sci, pyton" → "John Doe, Computer Science, Python"

**LLM Job #2: Recommendation Generation (Requirement 6)**
- Purpose: Generate personalized, actionable career recommendations
- Temperature: 0.7 (creative)
- Processing Time: 1-2 seconds per student
- Example: "Increase GPA from 7.2 to 8.0 by focusing on core CS subjects. Alumni A did this and got Google."

**LLM Job #3: Voice Assessment Evaluation (Requirement 12)**
- Purpose: Score voice interview responses on technical accuracy and communication
- Temperature: 0.3 (consistent scoring)
- Processing Time: 1-2 seconds per evaluation
- Example: Scores answer on 4 dimensions (0-10 each) + provides specific feedback

**LLM Job #4: Gap Analysis Narratives (Requirement 15)**
- Purpose: Convert statistical gaps into motivating explanations
- Temperature: 0.7 (engaging)
- Processing Time: 0.5-1 second per narrative
- Example: "Your GPA is 0.9 points below successful alumni. Here's why it matters and how to close the gap..."

**LLM Job #5: Skill Market Demand Analysis (Requirement 12A) - NEW**
- Purpose: Dynamically assess skill market demand and assign weight multipliers
- Temperature: 0.2 (data-driven, consistent)
- Processing Time: 0.5-1 second per skill
- Example Input: "Analyze market demand for Python in 2026"
- Example Output: "2.0x weight - High demand in AI/ML, 78% of jobs require it, 40% salary premium"
- Caching: 30 days to avoid repeated calls

### What Does NOT Use LLM (Pure Math):

**Vector Generation (Requirement 3)**
- Uses: NumPy for numerical operations
- Storage: Qdrant vector database
- No LLM involved

**Similarity Matching (Requirement 4)**
- Uses: Qdrant vector database with cosine similarity
- Fallback: scikit-learn cosine_similarity
- No LLM involved

**Trajectory Score Calculation (Requirement 5)**
- Uses: Weighted averaging based on similarity scores
- No LLM involved

**Gap Calculation (Requirement 15 - numerical part)**
- Uses: NumPy for statistical calculations
- LLM only used for narrative generation, not gap calculation

### Hardware and Performance:

**Target Hardware:** Lenovo Legion 5i
- GPU: RTX 4060 (8GB VRAM)
- CPU: i7 14th Gen HX (14 cores)
- RAM: 16GB

**Performance Benchmarks:**
- Single LLM request: 0.5-1 second
- Simultaneous requests: 8+ without degradation
- 1000 students (all 4 jobs): 30-50 minutes total
- Cost: $0 (no cloud APIs)

**Comparison to Cloud APIs:**
- Speed: Matches or beats GPT-4o
- Cost: $0 vs $7000+ for 1000 students
- Privacy: All data stays local
- Reliability: No rate limits or API downtime

### Team Responsibilities:

**Arun (Backend + Data):**
- Install and configure Ollama
- Implement LLM Job #1 (Data Cleaning)
- Build API endpoints for LLM calls
- Build API endpoints for mobile app data sync
- Monitor LLM performance
- Handle digital wellbeing data storage and analysis

**Sudeep (AI/Integration):**
- Implement LLM Job #2 (Recommendations)
- Implement LLM Job #3 (Voice Evaluation)
- Implement LLM Job #4 (Gap Narratives)
- Implement LLM Job #5 (Skill Market Demand Analysis)
- Optimize prompts and parameters
- Integrate VAPI for voice calls
- Implement behavioral pattern analysis algorithms

**Vivek (Frontend + Mobile):**
- Display LLM-generated recommendations
- Display gap analysis narratives
- Show loading states during LLM processing
- Handle LLM errors gracefully
- Build React Native mobile app for data collection
- Implement digital wellbeing dashboard visualizations

**Mayur (Project Lead):**
- Monitor LLM quality and accuracy
- Collect user feedback on recommendations
- Decide on fallback strategies
- Manage hardware/infrastructure
- Coordinate mobile app testing and deployment
- Ensure privacy compliance for data collection

### Timeline (15-Day Sprint):

**Days 1-2:** Setup Ollama + Llama 3.1, test basic calls, setup React Native project
**Days 3-5:** Implement LLM Job #1 (Data Cleaning), start mobile app UI
**Days 6-8:** Implement LLM Job #2 (Recommendations), implement mobile data collection
**Days 9-11:** Implement LLM Job #3 (Voice Evaluation), implement data sync API
**Days 12-13:** Implement LLM Job #4 (Gap Narratives) + Job #5 (Skill Demand Analysis), implement behavioral pattern analysis
**Days 14-15:** Testing, optimization, mobile app testing, demo prep

---

## Technical Architecture Summary

```
┌─────────────────────────────────────────────────────┐
│              Mobile App (React Native)               │
│  - Screen Time Tracking                              │
│  - App Activity Monitoring                           │
│  - Sleep Pattern Detection                           │
│  - Daily Data Sync                                   │
└────────────────────┬────────────────────────────────┘
                     │
                     │ REST API (Data Sync)
                     │
┌────────────────────▼────────────────────────────────┐
│                  Frontend (React)                    │
│  - Student Dashboard                                 │
│  - Upload CSV                                        │
│  - View Recommendations                              │
│  - Voice Assessment UI                               │
│  - Digital Wellbeing Dashboard                       │
└────────────────────┬────────────────────────────────┘
                     │
                     │ HTTP/REST API
                     │
┌────────────────────▼────────────────────────────────┐
│              Backend (FastAPI)                       │
│                                                      │
│  ┌──────────────────────────────────────────────┐  │
│  │  API Routes:                                 │  │
│  │  - POST /api/clean-data (LLM Job #1)        │  │
│  │  - POST /api/recommendations (LLM Job #2)   │  │
│  │  - POST /api/evaluate-voice (LLM Job #3)    │  │
│  │  - POST /api/gap-narrative (LLM Job #4)     │  │
│  │  - POST /api/predict (Math - No LLM)        │  │
│  │  - POST /api/mobile/sync (Data Collection)  │  │
│  │  - GET  /api/mobile/insights (Behavioral)   │  │
│  └──────────────────┬───────────────────────────┘  │
│                     │                                │
│  ┌──────────────────▼───────────────────────────┐  │
│  │  Services:                                   │  │
│  │  - data_cleaning.py (LLM)                    │  │
│  │  - recommendation_engine.py (LLM)            │  │
│  │  - voice_evaluation.py (LLM)                 │  │
│  │  - gap_analysis.py (LLM + Math)              │  │
│  │  - vector_engine.py (Math - NumPy)           │  │
│  │  - prediction_engine.py (Math - sklearn)     │  │
│  │  - behavioral_analysis.py (Math - Pandas)    │  │
│  └──────────────────┬───────────────────────────┘  │
└────────────────────┬┴──────────────────────────────┘
                     │
                     │ Local API (localhost:11434)
                     │
┌────────────────────▼────────────────────────────────┐
│         Ollama Server (Lenovo Legion 5i)             │
│  🔥 RTX 4060 (8GB VRAM) + i7 14th Gen HX            │
│  - Llama 3.1 8B Model (~5GB VRAM)                   │
│  - Handles 8+ simultaneous requests                 │
│  - Response time: 0.5-1 second                      │
│  - Cost: $0 (all local)                             │
└─────────────────────────────────────────────────────┘
```

**Key Principle:** LLM for language tasks (cleaning, recommendations, evaluation, narratives). Pure math for prediction (vectors, similarity, scoring, behavioral analysis).

