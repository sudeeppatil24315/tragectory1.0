# Trajectory Engine MVP - All Formulas

This document contains all mathematical formulas used in the Trajectory Engine MVP project.

---

## 1. Vector Normalization Formulas

### 1.1 GPA Normalization (0-10 scale to 0-1)
```
normalized_gpa = gpa / 10.0
```

**Example:**
- GPA = 7.5 → normalized_gpa = 0.75
- GPA = 8.0 → normalized_gpa = 0.80

---

### 1.2 GPA Conversion (4.0 scale to 10.0 scale)
```
gpa_10_scale = (gpa_4_scale / 4.0) × 10.0
```

**Example:**
- GPA = 3.5 (4.0 scale) → 8.75 (10.0 scale)
- GPA = 3.0 (4.0 scale) → 7.5 (10.0 scale)

---

### 1.3 GPA Conversion (Percentage to 10.0 scale)
```
gpa_10_scale = percentage / 10.0
```

**Example:**
- 85% → 8.5 (10.0 scale)
- 75% → 7.5 (10.0 scale)

---

### 1.4 Attendance Normalization (0-100% to 0-1)
```
normalized_attendance = attendance_percentage / 100.0
```

**Example:**
- Attendance = 80% → normalized_attendance = 0.80
- Attendance = 75% → normalized_attendance = 0.75

---

### 1.5 Study Hours Normalization
```
normalized_study_hours = study_hours_per_week / max_study_hours
```

Where `max_study_hours` = 40 (reasonable maximum)

**Example:**
- Study hours = 20/week → normalized = 20/40 = 0.50
- Study hours = 30/week → normalized = 30/40 = 0.75

---

### 1.6 Screen Time Normalization
```
normalized_screen_time = screen_time_hours / 24.0
```

**Example:**
- Screen time = 6 hours → normalized = 6/24 = 0.25
- Screen time = 9 hours → normalized = 9/24 = 0.375

---

### 1.7 Sleep Duration Normalization
```
normalized_sleep = sleep_hours / 12.0
```

Where 12 hours is the maximum reasonable sleep duration.

**Example:**
- Sleep = 7 hours → normalized = 7/12 = 0.583
- Sleep = 5.5 hours → normalized = 5.5/12 = 0.458

---

### 1.8 Skill Score Normalization (0-100 to 0-1)
```
normalized_skill_score = skill_score / 100.0
```

**Example:**
- Skill score = 85 → normalized = 0.85
- Skill score = 70 → normalized = 0.70

---

## 2. Focus Score Calculation

### 2.1 Focus Score Formula
```
Focus_Score = (Educational_Time + Productivity_Time) / (Social_Media_Time + Entertainment_Time)
```

**Where:**
- Educational_Time = Time spent on educational apps (coding, learning)
- Productivity_Time = Time spent on productivity apps (calendar, notes)
- Social_Media_Time = Time spent on social media (Instagram, Twitter)
- Entertainment_Time = Time spent on entertainment (YouTube, Netflix)

**Example:**
```
Educational_Time = 2 hours
Productivity_Time = 1 hour
Social_Media_Time = 3 hours
Entertainment_Time = 2 hours

Focus_Score = (2 + 1) / (3 + 2) = 3 / 5 = 0.6
```

**Interpretation:**
- Focus_Score < 0.5 → Low productivity
- Focus_Score 0.5-1.0 → Moderate productivity
- Focus_Score > 1.0 → High productivity

---

## 3. Vector Generation Formula

### 3.1 Student Vector Representation
```
student_vector = [
    normalized_gpa,
    normalized_attendance,
    major_encoding,
    normalized_study_hours,
    normalized_project_count,
    normalized_screen_time,
    normalized_focus_score,
    normalized_sleep_duration,
    normalized_quiz_score,
    normalized_voice_score,
    normalized_skill_scores...
]
```

**Dimensions:** 15-20 features (depending on number of skills)

**Example:**
```python
student_vector = [
    0.75,   # GPA (7.5/10)
    0.80,   # Attendance (80%)
    1.0,    # Major encoding (Computer Science = 1.0)
    0.50,   # Study hours (20/40)
    0.30,   # Projects (3/10)
    0.375,  # Screen time (9/24)
    0.60,   # Focus score
    0.583,  # Sleep (7/12)
    0.85,   # Quiz score (85/100)
    0.80,   # Voice score (80/100)
    0.85,   # Python skill (85/100)
    0.80,   # React skill (80/100)
    0.75    # AWS skill (75/100)
]
```

---

## 4. Cosine Similarity Formula

### 4.1 Cosine Similarity Between Two Vectors
```
cosine_similarity(A, B) = (A · B) / (||A|| × ||B||)
```

**Where:**
- A · B = Dot product of vectors A and B
- ||A|| = Magnitude (Euclidean norm) of vector A
- ||B|| = Magnitude (Euclidean norm) of vector B

**Expanded:**
```
A · B = Σ(A[i] × B[i]) for i = 0 to n

||A|| = √(Σ(A[i]²)) for i = 0 to n

||B|| = √(Σ(B[i]²)) for i = 0 to n
```

**Example:**
```python
Student A = [0.75, 0.80, 0.50]
Alumni B = [0.80, 0.85, 0.55]

# Dot product
A · B = (0.75 × 0.80) + (0.80 × 0.85) + (0.50 × 0.55)
      = 0.60 + 0.68 + 0.275
      = 1.555

# Magnitudes
||A|| = √(0.75² + 0.80² + 0.50²) = √(0.5625 + 0.64 + 0.25) = √1.4525 = 1.205
||B|| = √(0.80² + 0.85² + 0.55²) = √(0.64 + 0.7225 + 0.3025) = √1.665 = 1.290

# Cosine similarity
similarity = 1.555 / (1.205 × 1.290) = 1.555 / 1.554 = 0.999 ≈ 1.0
```

**Interpretation:**
- similarity = 1.0 → Identical vectors
- similarity = 0.9-1.0 → Very similar
- similarity = 0.7-0.9 → Similar
- similarity < 0.7 → Not very similar

---

## 5. Trajectory Score Calculation

### 5.1 Weighted Average Formula
```
Trajectory_Score = Σ(similarity[i] × outcome_score[i]) / Σ(similarity[i])
```

**Where:**
- similarity[i] = Cosine similarity score with alumni i (0-1)
- outcome_score[i] = Employment outcome score of alumni i (0-100)
- i = 1 to 5 (top 5 similar alumni)

**Outcome Score Mapping:**
```
Tier 1 (FAANG/Top) + High Salary (15+ LPA) → 90-100
Tier 1 (FAANG/Top) + Medium Salary (10-15 LPA) → 80-90
Tier 2 (Mid-size/Product) + High Salary (10+ LPA) → 70-80
Tier 2 (Mid-size/Product) + Medium Salary (6-10 LPA) → 60-70
Tier 3 (Service/Startup) + Medium Salary (5-8 LPA) → 50-60
Tier 3 (Service/Startup) + Low Salary (3-5 LPA) → 40-50
Not Placed → 0-40
```

**Example:**
```
Alumni matches:
1. Alumni A: similarity = 0.92, outcome_score = 95 (Google, 18 LPA)
2. Alumni B: similarity = 0.88, outcome_score = 90 (Microsoft, 16 LPA)
3. Alumni C: similarity = 0.85, outcome_score = 65 (Infosys, 8 LPA)
4. Alumni D: similarity = 0.80, outcome_score = 55 (Startup, 6 LPA)
5. Alumni E: similarity = 0.75, outcome_score = 20 (Not placed)

Trajectory_Score = (0.92×95 + 0.88×90 + 0.85×65 + 0.80×55 + 0.75×20) / (0.92 + 0.88 + 0.85 + 0.80 + 0.75)

Numerator = 87.4 + 79.2 + 55.25 + 44 + 15 = 280.85
Denominator = 4.2

Trajectory_Score = 280.85 / 4.2 = 66.87 ≈ 67
```

**Interpretation:**
- 0-40: Low employability (at-risk)
- 41-70: Moderate employability (average placement)
- 71-100: High employability (top-tier placement)

---

## 6. Skill Market Weighting Formula

### 6.1 Weighted Skill Score
```
Weighted_Skill_Score = Σ(skill_proficiency[i] × market_weight[i]) / Σ(market_weight[i])
```

**Where:**
- skill_proficiency[i] = Proficiency score for skill i (0-100)
- market_weight[i] = Market demand multiplier (0.5x, 1.0x, or 2.0x)

**Market Weight Values:**
- 2.0x = High demand (Python, React, AWS, AI/ML, Cloud, DevOps)
- 1.0x = Medium demand (Java, JavaScript, SQL, C++)
- 0.5x = Low demand (jQuery, Flash, VB.NET, legacy technologies)

**Example:**
```
Student skills:
1. Python: proficiency = 85, market_weight = 2.0x
2. React: proficiency = 80, market_weight = 2.0x
3. jQuery: proficiency = 90, market_weight = 0.5x

Weighted_Skill_Score = (85×2.0 + 80×2.0 + 90×0.5) / (2.0 + 2.0 + 0.5)
                     = (170 + 160 + 45) / 4.5
                     = 375 / 4.5
                     = 83.33

Normalized to 0-100 scale = 83.33 (already in range)
```

**Comparison:**
```
Student A (Trending Skills):
- Python (85, 2.0x), React (80, 2.0x), AWS (75, 2.0x)
- Weighted Score = (170 + 160 + 150) / 6.0 = 80

Student B (Outdated Skills):
- PHP (90, 0.5x), jQuery (85, 0.5x), Flash (80, 0.5x)
- Weighted Score = (45 + 42.5 + 40) / 1.5 = 85

Wait, this seems wrong. Let me recalculate...

Actually, the formula should normalize to 0-100:
Weighted_Skill_Score = [Σ(skill_proficiency[i] × market_weight[i]) / number_of_skills] / 2.0 × 100

Student A: (170 + 160 + 150) / 3 = 160 → 160/2.0 = 80
Student B: (45 + 42.5 + 40) / 3 = 42.5 → 42.5/2.0 = 21.25

This makes more sense!
```

**Corrected Formula:**
```
Weighted_Skill_Score = [Σ(skill_proficiency[i] × market_weight[i]) / number_of_skills] / max_weight × 100

Where max_weight = 2.0 (highest possible weight)
```

---

## 7. Combined Skill Score Formula

### 7.1 Final Skill Score (Quiz + Voice)
```
Final_Skill_Score = (Quiz_Score × 0.6) + (Voice_Score × 0.4)
```

**Where:**
- Quiz_Score = Score from quiz-based assessment (0-100)
- Voice_Score = Score from voice interview evaluation (0-100)

**Example:**
```
Quiz_Score = 85
Voice_Score = 75

Final_Skill_Score = (85 × 0.6) + (75 × 0.4)
                  = 51 + 30
                  = 81
```

**If only one assessment is completed:**
```
# Only quiz completed
Final_Skill_Score = Quiz_Score × 0.9  (10% confidence penalty)

# Only voice completed
Final_Skill_Score = Voice_Score × 0.9  (10% confidence penalty)
```

---

## 8. Voice Assessment Scoring Formula

### 8.1 Overall Voice Score
```
Overall_Voice_Score = (Technical_Accuracy + Communication_Clarity + Depth + Completeness) × 2.5
```

**Where each dimension is scored 0-10:**
- Technical_Accuracy (0-10)
- Communication_Clarity (0-10)
- Depth (0-10)
- Completeness (0-10)

**Example:**
```
Technical_Accuracy = 8
Communication_Clarity = 9
Depth = 7
Completeness = 8

Overall_Voice_Score = (8 + 9 + 7 + 8) × 2.5
                    = 32 × 2.5
                    = 80
```

**This converts the 0-40 range to 0-100 scale.**

---

## 9. Gap Calculation Formulas

### 9.1 Percentage Gap
```
Percentage_Gap = |student_value - alumni_average| / alumni_average × 100
```

**Example:**
```
Student GPA = 7.2
Alumni Average GPA = 8.1

Percentage_Gap = |7.2 - 8.1| / 8.1 × 100
               = 0.9 / 8.1 × 100
               = 11.11%
```

---

### 9.2 Absolute Gap
```
Absolute_Gap = alumni_average - student_value
```

**Example:**
```
Student Sleep = 5.5 hours
Alumni Average Sleep = 7.2 hours

Absolute_Gap = 7.2 - 5.5 = 1.7 hours
```

---

## 10. Confidence Interval Formula

### 10.1 Confidence Interval for Trajectory Score
```
Confidence_Interval = Trajectory_Score ± (Standard_Deviation × Confidence_Factor)
```

**Where:**
```
Standard_Deviation = √[Σ(outcome_score[i] - Trajectory_Score)² / n]

Confidence_Factor = based on number of matches:
- n ≥ 5: Confidence_Factor = 1.0 (High confidence)
- n = 3-4: Confidence_Factor = 1.5 (Medium confidence)
- n < 3: Confidence_Factor = 2.0 (Low confidence)
```

**Example:**
```
Trajectory_Score = 67
Alumni outcome scores: [95, 90, 65, 55, 20]
n = 5

Standard_Deviation = √[(95-67)² + (90-67)² + (65-67)² + (55-67)² + (20-67)²] / 5
                   = √[784 + 529 + 4 + 144 + 2209] / 5
                   = √[3670 / 5]
                   = √734
                   = 27.09

Confidence_Factor = 1.0 (n ≥ 5)

Confidence_Interval = 67 ± (27.09 × 1.0)
                    = 67 ± 27
                    = [40, 94]

Display as: 67 ± 27 or "Between 40 and 94"
```

---

## 11. Component Weight Formula

### 11.1 Overall Profile Score (Equal Weighting)
```
Overall_Profile_Score = (Academic_Score + Behavioral_Score + Skill_Score) / 3
```

**Where:**
- Academic_Score = (normalized_gpa + normalized_attendance) / 2 × 100
- Behavioral_Score = (normalized_study_hours + normalized_projects + normalized_focus_score + normalized_sleep) / 4 × 100
- Skill_Score = Weighted_Skill_Score (from formula 6.1)

**Example:**
```
Academic_Score = (0.75 + 0.80) / 2 × 100 = 77.5
Behavioral_Score = (0.50 + 0.30 + 0.60 + 0.583) / 4 × 100 = 49.6
Skill_Score = 80 (from weighted skill calculation)

Overall_Profile_Score = (77.5 + 49.6 + 80) / 3 = 69.03 ≈ 69
```

---

## 12. Batch Processing Formulas

### 12.1 Parallel Processing Time
```
Total_Time_Parallel = (Total_Students / Number_of_Workers) × Time_Per_Student
```

**Example:**
```
Total_Students = 8
Number_of_Workers = 4
Time_Per_Student = 3 seconds

Total_Time_Parallel = (8 / 4) × 3 = 2 × 3 = 6 seconds

Compare to sequential:
Total_Time_Sequential = 8 × 3 = 24 seconds

Speedup = 24 / 6 = 4x faster
```

---

## 13. Cache Hit Rate Formula

### 13.1 Effective Response Time with Caching
```
Effective_Response_Time = (Cache_Hit_Rate × Cache_Time) + ((1 - Cache_Hit_Rate) × LLM_Time)
```

**Example:**
```
Cache_Hit_Rate = 0.90 (90%)
Cache_Time = 0.01 seconds
LLM_Time = 3 seconds

Effective_Response_Time = (0.90 × 0.01) + (0.10 × 3)
                        = 0.009 + 0.3
                        = 0.309 seconds

Speedup = 3 / 0.309 = 9.7x faster
```

---

## Summary of Key Formulas

1. **Vector Normalization:** value / max_value
2. **Focus Score:** (Educational + Productivity) / (Social_Media + Entertainment)
3. **Cosine Similarity:** (A · B) / (||A|| × ||B||)
4. **Trajectory Score:** Σ(similarity × outcome) / Σ(similarity)
5. **Weighted Skill Score:** Σ(proficiency × weight) / number_of_skills / 2.0 × 100
6. **Final Skill Score:** (Quiz × 0.6) + (Voice × 0.4)
7. **Voice Score:** (Accuracy + Clarity + Depth + Completeness) × 2.5
8. **Percentage Gap:** |student - alumni| / alumni × 100
9. **Confidence Interval:** Score ± (StdDev × Factor)
10. **Overall Profile:** (Academic + Behavioral + Skill) / 3

---

**Note:** All formulas use pure mathematics (NumPy, scikit-learn). NO LLM is used for calculations.
