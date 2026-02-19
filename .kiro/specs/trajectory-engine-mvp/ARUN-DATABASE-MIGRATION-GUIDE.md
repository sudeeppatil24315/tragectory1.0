# Database Migration Guide for Arun

**Date:** February 18, 2026  
**Purpose:** Update PostgreSQL database to match spec requirements  
**Status:** Models updated, database migration needed

---

## Summary of Changes

I've updated `arun_backend/backend/app/models.py` with the following changes:

### ✅ **ADDED** - New Tables

1. **Alumni Table** (NEW - Critical for predictions)
   - Stores graduated student data with employment outcomes
   - Fields: name, major, graduation_year, gpa, attendance, placement_status, company_tier, role_title, salary_range, role_to_major_match_score, vector_id
   - Enums: PlacementStatusEnum, CompanyTierEnum
   - Constraints: GPA 0-10, attendance 0-100, role_to_major_match_score 0-100

2. **Skill Table** (NEW - Critical for skill assessments)
   - Individual skill tracking with market demand weighting
   - Fields: student_id, skill_name, proficiency_score, quiz_score, voice_score, market_weight, market_weight_reasoning
   - Constraints: All scores 0-100, market_weight in (0.5, 1.0, 2.0)
   - Unique constraint: (student_id, skill_name)

### 🔄 **UPDATED** - Modified Tables

3. **Student Table**
   - Added CheckConstraints: GPA 0-10, attendance 0-100
   - Added updated_at timestamp
   - Changed gpa and attendance to Numeric type for precision
   - All existing fields preserved

4. **DigitalWellbeingDaily → DigitalWellbeingData**
   - Renamed table to match spec
   - Added CheckConstraints: focus_score >= 0, sleep_duration 0-24
   - Added UniqueConstraint: (student_id, date)
   - Changed numeric fields to Numeric type
   - Added sleep_quality enum

5. **TrajectoryScore Table**
   - Added: confidence (0-1), margin_of_error, trend (enum), velocity, predicted_tier (enum), num_similar_alumni
   - Changed score to Numeric with CheckConstraint 0-100
   - Removed: confidence_level (string) - replaced with confidence (float)

6. **Recommendation Table**
   - Renamed fields: content → description, impact_level → impact (enum), estimated_score_gain → estimated_points, generated_at → created_at
   - Added: title field
   - Changed impact to enum (High, Medium, Low)
   - Added index on completed field

---

## What You Need to Do in PostgreSQL

### Step 1: Backup Your Database

```bash
# Create a backup before making any changes
pg_dump -U postgres -d trajectory > trajectory_backup_$(date +%Y%m%d).sql
```

### Step 2: Create New Tables

Run these SQL commands in your PostgreSQL database:

```sql
-- 1. Create Alumni Table
CREATE TABLE alumni (
    id SERIAL PRIMARY KEY,
    name VARCHAR NOT NULL,
    major VARCHAR NOT NULL,
    graduation_year INTEGER NOT NULL,
    gpa NUMERIC(3, 2) NOT NULL CHECK (gpa >= 0 AND gpa <= 10),
    attendance NUMERIC(5, 2) NOT NULL CHECK (attendance >= 0 AND attendance <= 100),
    study_hours_per_week NUMERIC(4, 1),
    project_count INTEGER,
    placement_status VARCHAR NOT NULL CHECK (placement_status IN ('Placed', 'Not Placed')),
    company_tier VARCHAR CHECK (company_tier IN ('Tier1', 'Tier2', 'Tier3')),
    role_title VARCHAR,
    salary_range VARCHAR,
    role_to_major_match_score NUMERIC(5, 2) CHECK (role_to_major_match_score >= 0 AND role_to_major_match_score <= 100),
    vector_id VARCHAR,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_alumni_major ON alumni(major);
CREATE INDEX idx_alumni_graduation_year ON alumni(graduation_year);

-- 2. Create Skills Table
CREATE TABLE skills (
    id SERIAL PRIMARY KEY,
    student_id INTEGER NOT NULL REFERENCES students(id),
    skill_name VARCHAR NOT NULL,
    proficiency_score NUMERIC(5, 2) NOT NULL CHECK (proficiency_score >= 0 AND proficiency_score <= 100),
    quiz_score NUMERIC(5, 2) CHECK (quiz_score >= 0 AND quiz_score <= 100),
    voice_score NUMERIC(5, 2) CHECK (voice_score >= 0 AND voice_score <= 100),
    market_weight NUMERIC(3, 2) DEFAULT 1.0 CHECK (market_weight IN (0.5, 1.0, 2.0)),
    market_weight_reasoning TEXT,
    last_assessed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT uq_student_skill UNIQUE (student_id, skill_name)
);

CREATE INDEX idx_skills_student ON skills(student_id);
CREATE INDEX idx_skills_name ON skills(skill_name);
```

### Step 3: Update Existing Tables

```sql
-- 3. Update Students Table
ALTER TABLE students 
    ADD CONSTRAINT chk_gpa CHECK (gpa >= 0 AND gpa <= 10),
    ADD CONSTRAINT chk_attendance CHECK (attendance >= 0 AND attendance <= 100),
    ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;

-- Change gpa and attendance to NUMERIC for precision
ALTER TABLE students 
    ALTER COLUMN gpa TYPE NUMERIC(3, 2),
    ALTER COLUMN attendance TYPE NUMERIC(5, 2);

-- 4. Rename DigitalWellbeingDaily to DigitalWellbeingData
ALTER TABLE digital_wellbeing_daily RENAME TO digital_wellbeing_data;

-- Add constraints to digital_wellbeing_data
ALTER TABLE digital_wellbeing_data
    ADD CONSTRAINT chk_focus_score CHECK (focus_score >= 0),
    ADD CONSTRAINT chk_sleep_duration CHECK (sleep_duration_hours >= 0 AND sleep_duration_hours <= 24),
    ADD CONSTRAINT uq_student_date UNIQUE (student_id, date);

-- Change numeric fields to NUMERIC type
ALTER TABLE digital_wellbeing_data
    ALTER COLUMN screen_time_hours TYPE NUMERIC(4, 2),
    ALTER COLUMN educational_app_hours TYPE NUMERIC(4, 2),
    ALTER COLUMN social_media_hours TYPE NUMERIC(4, 2),
    ALTER COLUMN entertainment_hours TYPE NUMERIC(4, 2),
    ALTER COLUMN productivity_hours TYPE NUMERIC(4, 2),
    ALTER COLUMN focus_score TYPE NUMERIC(3, 2),
    ALTER COLUMN sleep_duration_hours TYPE NUMERIC(3, 1);

-- 5. Update TrajectoryScore Table
ALTER TABLE trajectory_scores
    ADD COLUMN confidence NUMERIC(3, 2) CHECK (confidence >= 0 AND confidence <= 1),
    ADD COLUMN margin_of_error NUMERIC(4, 2),
    ADD COLUMN trend VARCHAR CHECK (trend IN ('improving', 'declining', 'stable')),
    ADD COLUMN velocity NUMERIC(5, 2),
    ADD COLUMN predicted_tier VARCHAR CHECK (predicted_tier IN ('Tier1', 'Tier2', 'Tier3')),
    ADD COLUMN num_similar_alumni INTEGER;

-- Change score to NUMERIC with constraint
ALTER TABLE trajectory_scores
    ALTER COLUMN score TYPE NUMERIC(5, 2),
    ADD CONSTRAINT chk_score CHECK (score >= 0 AND score <= 100);

-- Drop old confidence_level column (after migrating data if needed)
-- ALTER TABLE trajectory_scores DROP COLUMN confidence_level;

-- 6. Update Recommendations Table
ALTER TABLE recommendations
    ADD COLUMN title VARCHAR,
    ADD COLUMN description TEXT,
    ADD COLUMN impact VARCHAR CHECK (impact IN ('High', 'Medium', 'Low')),
    ADD COLUMN estimated_points NUMERIC(4, 1),
    ADD COLUMN timeline VARCHAR;

-- Migrate data from old columns to new columns
UPDATE recommendations SET 
    description = content,
    impact = impact_level,
    estimated_points = estimated_score_gain,
    title = SUBSTRING(content, 1, 100);  -- Use first 100 chars as title

-- Drop old columns (after verifying migration)
-- ALTER TABLE recommendations DROP COLUMN content;
-- ALTER TABLE recommendations DROP COLUMN impact_level;
-- ALTER TABLE recommendations DROP COLUMN estimated_score_gain;
-- ALTER TABLE recommendations DROP COLUMN generated_at;

-- Rename created_at if needed
ALTER TABLE recommendations RENAME COLUMN generated_at TO created_at;

-- Add index on completed
CREATE INDEX idx_recommendations_completed ON recommendations(completed);
```

### Step 4: Verify Changes

```sql
-- Check all tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;

-- Verify alumni table structure
\d alumni

-- Verify skills table structure
\d skills

-- Verify students constraints
\d students

-- Verify digital_wellbeing_data
\d digital_wellbeing_data

-- Verify trajectory_scores
\d trajectory_scores

-- Verify recommendations
\d recommendations
```

---

## Alternative: Use Alembic for Migrations

If you want to use Alembic (recommended for production):

### Step 1: Install Alembic

```bash
cd arun_backend/backend
pip install alembic
```

### Step 2: Initialize Alembic

```bash
alembic init alembic
```

### Step 3: Configure Alembic

Edit `alembic.ini`:
```ini
sqlalchemy.url = postgresql://postgres:8088@localhost:5432/trajectory
```

Edit `alembic/env.py`:
```python
from app.models import Base
target_metadata = Base.metadata
```

### Step 4: Generate Migration

```bash
alembic revision --autogenerate -m "Add alumni and skills tables, update existing tables"
```

### Step 5: Review and Apply Migration

```bash
# Review the generated migration file in alembic/versions/
# Then apply it:
alembic upgrade head
```

---

## Testing After Migration

### Test 1: Verify Alumni Table

```python
from app.db import SessionLocal
from app.models import Alumni, PlacementStatusEnum, CompanyTierEnum

db = SessionLocal()

# Create test alumni
test_alumni = Alumni(
    name="Test Alumni",
    major="Computer Science",
    graduation_year=2023,
    gpa=8.5,
    attendance=90.0,
    placement_status=PlacementStatusEnum.PLACED,
    company_tier=CompanyTierEnum.TIER1,
    role_title="Software Engineer",
    salary_range="15-20 LPA",
    role_to_major_match_score=95.0
)
db.add(test_alumni)
db.commit()
print("✅ Alumni table working!")
```

### Test 2: Verify Skills Table

```python
from app.models import Skill

# Create test skill
test_skill = Skill(
    student_id=1,  # Use existing student ID
    skill_name="Python",
    proficiency_score=85.0,
    quiz_score=90.0,
    voice_score=80.0,
    market_weight=2.0,
    market_weight_reasoning="High demand in AI/ML jobs"
)
db.add(test_skill)
db.commit()
print("✅ Skills table working!")
```

### Test 3: Verify Updated Tables

```python
from app.models import TrajectoryScore, TrendEnum, CompanyTierEnum

# Create test trajectory score
test_score = TrajectoryScore(
    student_id=1,
    score=75.5,
    confidence=0.85,
    margin_of_error=5.2,
    trend=TrendEnum.IMPROVING,
    velocity=2.5,
    predicted_tier=CompanyTierEnum.TIER1,
    num_similar_alumni=10
)
db.add(test_score)
db.commit()
print("✅ TrajectoryScore table working!")
```

---

## Common Issues and Solutions

### Issue 1: "column already exists"
**Solution:** The column was already added. Skip that ALTER TABLE command.

### Issue 2: "constraint already exists"
**Solution:** The constraint was already added. Skip that constraint.

### Issue 3: "cannot cast type"
**Solution:** You may need to drop and recreate the column:
```sql
ALTER TABLE table_name DROP COLUMN column_name;
ALTER TABLE table_name ADD COLUMN column_name NUMERIC(3, 2);
```

### Issue 4: "violates check constraint"
**Solution:** Clean your data first:
```sql
-- Find violating records
SELECT * FROM students WHERE gpa < 0 OR gpa > 10;

-- Fix them
UPDATE students SET gpa = 0 WHERE gpa < 0;
UPDATE students SET gpa = 10 WHERE gpa > 10;

-- Then add constraint
ALTER TABLE students ADD CONSTRAINT chk_gpa CHECK (gpa >= 0 AND gpa <= 10);
```

---

## Migration Checklist

- [ ] Backup database
- [ ] Create alumni table
- [ ] Create skills table
- [ ] Update students table constraints
- [ ] Rename digital_wellbeing_daily to digital_wellbeing_data
- [ ] Update digital_wellbeing_data constraints
- [ ] Update trajectory_scores table
- [ ] Update recommendations table
- [ ] Verify all tables with \d commands
- [ ] Test creating records in new tables
- [ ] Test querying updated tables
- [ ] Update any existing code that references old column names
- [ ] Run your application and check for errors

---

## Next Steps After Migration

1. **Update Services:**
   - Update `services/student_service.py` to handle new fields
   - Update `services/vector_gen_service.py` to include alumni vectors
   - Create `services/skill_service.py` for skill management
   - Create `services/alumni_service.py` for alumni data

2. **Update Routes:**
   - Update `routes/students.py` to use new field names
   - Create `routes/alumni.py` for alumni endpoints
   - Create `routes/skills.py` for skill assessment endpoints

3. **Test Everything:**
   - Test student CRUD operations
   - Test alumni data import
   - Test skill assessments
   - Test trajectory score calculation
   - Test recommendations generation

---

## Questions?

If you encounter any issues during migration:
1. Check the error message carefully
2. Verify your PostgreSQL version (should be 12+)
3. Make sure you have backup before making changes
4. Test on a development database first

**Need Help?** Share the error message and I can help troubleshoot!

---

**Status:** Models updated ✅ | Database migration pending ⏳
