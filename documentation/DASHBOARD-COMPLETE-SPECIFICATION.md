# Trajectory Engine - Complete Dashboard Specification

**Version:** 1.0  
**Date:** February 17, 2026  
**Status:** Ready for Development

---

## Table of Contents

1. [Dashboard Overview](#1-dashboard-overview)
2. [Student Dashboard](#2-student-dashboard)
3. [Admin Dashboard](#3-admin-dashboard)
4. [Component Library](#4-component-library)
5. [Data Structure](#5-data-structure)
6. [API Endpoints](#6-api-endpoints)
7. [UI/UX Guidelines](#7-uiux-guidelines)
8. [Development Guide](#8-development-guide)

---

## 1. Dashboard Overview

### 1.1 Dashboard Types

**Two Main Dashboards:**

1. **Student Dashboard** - Individual student view
   - Personal trajectory score with confidence intervals
   - Component breakdown (Academic, Behavioral, Skills)
   - Digital wellbeing metrics from mobile app
   - Personalized recommendations (LLM-generated)
   - Similar alumni matches
   - Gap analysis with narratives
   - Progress tracking and gamification

2. **Admin Dashboard** - Institution-wide analytics
   - Overview statistics (total students, average scores)
   - Student distribution by trajectory score
   - Behavioral pattern analytics
   - Filtering and search capabilities
   - CSV import/export for bulk operations
   - Batch recommendation generation
   - Mobile app data monitoring

### 1.2 Technology Stack

**Frontend:**
- Framework: React 18+ with TypeScript
- State Management: Redux Toolkit
- UI Library: Material-UI (MUI) v5
- Charts: Recharts + Sparklines
- Icons: Material Icons
- Routing: React Router v6
- Forms: React Hook Form + Yup validation

**Backend:**
- API: FastAPI (Python 3.10+)
- Database: PostgreSQL 14+
- Vector DB: Qdrant (self-hosted)
- Cache: Redis
- LLM: Ollama (Llama 3.1 8B)
- Task Queue: Celery (for batch operations)

**Mobile:**
- Framework: React Native
- State: Redux Toolkit
- Navigation: React Navigation
- Storage: AsyncStorage + SQLite

---

## 2. Student Dashboard

### 2.1 Dashboard Layout

**Overall Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│  Header: Student Name | Trajectory Score | Last Updated     │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────────────────────┐ │
│  │  Trajectory     │  │  Component Breakdown             │ │
│  │  Score Card     │  │  (Academic, Behavioral, Skills)  │ │
│  └─────────────────┘  └──────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Digital Wellbeing Metrics                           │  │
│  │  (Screen Time, Focus Score, Sleep, App Usage)        │  │
│  └──────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────────────────────┐ │
│  │  Recommendations│  │  Similar Alumni                  │ │
│  │  (Top 5)        │  │  (Top 3 Matches)                 │ │
│  └─────────────────┘  └──────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Gap Analysis (vs Successful Alumni)                 │  │
│  └──────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Progress Tracking & Gamification                    │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

### 2.2 Container 1: Trajectory Score Card

**Purpose:** Display the main employability score prominently with clear interpretation.

**Data Required:**
```typescript
interface TrajectoryScoreData {
  score: number; // 0-100
  confidenceInterval: { lower: number; upper: number };
  placementLikelihood: { min: number; max: number };
  category: 'Excellent' | 'Very Good' | 'Good' | 'Fair' | 'Below Average' | 'Poor';
  lastUpdated: Date;
  trend: 'up' | 'down' | 'stable';
  previousScore?: number;
}
```

**Visual Design:**
```
┌─────────────────────────────────────────┐
│  Your Trajectory Score                  │
│                                         │
│         ┌─────────────┐                 │
│         │     73      │                 │
│         │   ━━━━━━    │  Good           │
│         │   /100      │  ↑ +3 pts      │
│         └─────────────┘                 │
│                                         │
│  Confidence: 68-78 (High)               │
│  Placement Likelihood: 65-75%           │
│                                         │
│  📊 What this means:                    │
│  You have moderate-high employability.  │
│  Similar to alumni who got Tier 1/2     │
│  placements at product companies.       │
│                                         │
│  Last updated: 2 hours ago              │
└─────────────────────────────────────────┘
```

**Score Interpretation Logic:**
- 90-100: Excellent (Green) - Very High (85-95%) placement likelihood
- 80-89: Very Good (Light Green) - High (75-85%)
- 70-79: Good (Yellow-Green) - Moderate-High (65-75%)
- 60-69: Fair (Orange) - Moderate (50-65%)
- 50-59: Below Average (Red-Orange) - Low-Moderate (35-50%)
- 0-49: Poor (Red) - Low (15-35%)

**Features:**
- Circular progress indicator with color coding
- Confidence interval display
- Placement likelihood percentage range
- Plain language interpretation
- Trend indicator (up/down/stable)
- Last updated timestamp

---

### 2.3 Container 2: Component Breakdown

**Purpose:** Show detailed breakdown of Academic, Behavioral, and Skills components.

**Data Required:**
```typescript
interface ComponentBreakdownData {
  academic: {
    score: number; // 0-1
    weight: number; // 0.25 for CS
    details: {
      gpa: number;
      attendance: number;
      internal: number;
      backlogs: number;
    };
  };
  behavioral: {
    score: number; // 0-1
    weight: number; // 0.35 for CS
    details: {
      studyHours: number;
      practiceHours: number;
      screenTime: number;
      socialMedia: number;
      sleep: number;
      grit: number;
    };
  };
  skills: {
    score: number; // 0-1
    weight: number; // 0.40 for CS
    details: {
      projects: number;
      deployed: boolean;
      internship: boolean;
      languages: number;
      problemSolving: number;
    };
  };
  major: string;
}
```

**Visual Design:**
```
┌─────────────────────────────────────────┐
│  Component Breakdown                    │
│  For Computer Science major             │
│                                         │
│  Academic (25% weight)          90/100  │
│  ████████████████████░░  ✅ Strong      │
│  GPA: 8.6 | Attendance: 90% | Backlogs: 0
│                                         │
│  Behavioral (35% weight)        48/100  │
│  ██████████░░░░░░░░░░  ⚠️ Needs Work   │
│  Study: 3h | Screen: 6h | Sleep: 8h    │
│  Grit: 0.48 (Moderate)                  │
│                                         │
│  Skills (40% weight)            73/100  │
│  ███████████████░░░░░  ✅ Good          │
│  Projects: 5 | Deployed: Yes            │
│  Internship: Yes | Languages: 5         │
│                                         │
│  💡 Focus on improving Behavioral       │
│     (highest weight, lowest score)      │
└─────────────────────────────────────────┘
```

**Features:**
- Progress bars with color coding (green/yellow/red)
- Weight percentage display
- Key metrics for each component
- Status indicators (✅ Strong, ⚠️ Moderate, ❌ Needs Work)
- Smart recommendation (focus on lowest-scoring high-weight component)
- Expandable details on click

---

### 2.4 Container 3: Digital Wellbeing Metrics

**Purpose:** Display behavioral data collected from mobile app with trends.

**Data Required:**
```typescript
interface DigitalWellbeingData {
  screenTime: {
    current: number; // hours/day (last 7 days avg)
    trend: number[]; // Last 7 days
    target: number; // 5 hours
    alumniAvg: number;
  };
  focusScore: {
    current: number; // 0-1
    trend: number[]; // Last 7 days
    target: number; // 0.8
    alumniAvg: number;
  };
  sleep: {
    current: number; // hours/day
    trend: number[]; // Last 7 days
    target: { min: number; max: number }; // 7-8 hours
    alumniAvg: number;
  };
  appUsage: {
    educational: number; // percentage
    social: number;
    entertainment: number;
    productivity: number;
  };
  lastSync: Date;
}
```

**Visual Design:**
```
┌─────────────────────────────────────────┐
│  Digital Wellbeing Metrics              │
│  Data from mobile app (last 7 days)     │
│                                         │
│  📱 Screen Time                         │
│  6.2h/day  ⚠️ High                      │
│  ▁▂▃▅▆▇█▆▅ (sparkline trend)            │
│  Target: <5h | Alumni avg: 4.8h        │
│                                         │
│  🎯 Focus Score                         │
│  0.65 (Moderate)  ⚠️                    │
│  Educational: 25% | Social: 35%         │
│  Target: >0.8 | Alumni avg: 0.82        │
│                                         │
│  😴 Sleep                               │
│  7.8h/day (Good)  ✅                    │
│  ▆▇█▆▅▆▇ (sparkline trend)              │
│  Target: 7-8h | Alumni avg: 7.5h       │
│                                         │
│  📊 App Usage Breakdown                 │
│  [Educational 25%][Social 35%]          │
│  [Entertainment 30%][Productivity 10%]  │
│                                         │
│  💡 Reduce social media by 1h/day       │
│     to improve focus score              │
│                                         │
│  Last synced: 3 hours ago               │
└─────────────────────────────────────────┘
```

**Features:**
- Real-time metrics from mobile app
- 7-day trend sparklines
- Comparison to targets and alumni averages
- Color-coded status indicators
- App usage pie chart or stacked bar
- Actionable recommendations
- Last sync timestamp
- Link to mobile app if not synced recently

---

### 2.5 Container 4: Recommendations

**Purpose:** Display LLM-generated personalized recommendations.

**Data Required:**
```typescript
interface RecommendationData {
  recommendations: Array<{
    id: string;
    title: string;
    description: string;
    impact: 'High' | 'Medium' | 'Low';
    estimatedPoints: number; // +X points to trajectory
    timeline: string; // "2 weeks", "1 month"
    category: 'Academic' | 'Behavioral' | 'Skills';
    actionSteps: string[];
    completed: boolean;
    alumniStory?: string; // Success story reference
  }>;
  generatedAt: Date;
  llmModel: string; // "llama3.1:8b"
}
```

**Visual Design:**
```
┌─────────────────────────────────────────┐
│  Personalized Recommendations           │
│  Generated by AI (Llama 3.1 8B)         │
│                                         │
│  1. 🔴 Improve Problem-Solving Skills   │
│     Impact: High (+8 pts) | 4 weeks     │
│     Practice DSA problems daily on      │
│     LeetCode. Start with Easy, move to  │
│     Medium. Alumni Arun did this and    │
│     improved from 2/5 to 4/5.           │
│     [ ] Mark as Complete                │
│                                         │
│  2. 🟡 Reduce Screen Time               │
│     Impact: Medium (+5 pts) | 2 weeks   │
│     Reduce from 6h to 4h daily. Use     │
│     app blockers during study hours.    │
│     [ ] Mark as Complete                │
│                                         │
│  3. 🟢 Build Consistency                │
│     Impact: Medium (+4 pts) | 1 month   │
│     Create daily study schedule. Track  │
│     with habit tracker app.             │
│     [ ] Mark as Complete                │
│                                         │
│  4. 🟡 Clarify Career Path              │
│     Impact: Low (+2 pts) | 2 weeks      │
│     Research 3 career options. Talk to  │
│     alumni in those roles.              │
│     [ ] Mark as Complete                │
│                                         │
│  5. 🟢 Practice Mock Interviews         │
│     Impact: Medium (+6 pts) | 3 weeks   │
│     Do 2 mock interviews per week.      │
│     Record and review performance.      │
│     [ ] Mark as Complete                │
│                                         │
│  Generated: 2 hours ago                 │
│  [Regenerate Recommendations]           │
└─────────────────────────────────────────┘
```

**Features:**
- Priority-sorted by impact (High → Medium → Low)
- Color-coded impact indicators (🔴 High, 🟡 Medium, 🟢 Low)
- Estimated trajectory score improvement
- Realistic timelines
- Actionable steps
- Alumni success stories for motivation
- Completion tracking
- Regenerate button (calls LLM again)
- Category tags (Academic/Behavioral/Skills)

---

### 2.6 Container 5: Similar Alumni

**Purpose:** Show top 3 most similar alumni with their outcomes.

**Data Required:**
```typescript
interface SimilarAlumniData {
  matches: Array<{
    id: string;
    name: string; // Anonymized (e.g., "Alumni A")
    similarity: number; // 0-1
    graduationYear: number;
    major: string;
    outcome: {
      placementStatus: 'Placed' | 'Not Placed';
      companyTier: 'Tier1' | 'Tier2' | 'Tier3';
      companyName?: string; // Optional, anonymized
      role: string;
      salaryRange: string; // "12-15 LPA"
    };
    profileSummary: {
      gpa: number;
      projects: number;
      internship: boolean;
    };
  }>;
  totalAlumni: number;
}
```

**Visual Design:**
```
┌─────────────────────────────────────────┐
│  Similar Alumni (Top 3 Matches)         │
│  Based on your profile similarity       │
│                                         │
│  1. Alumni A (92% similar)              │
│     Graduated: 2024 | CS Major          │
│     ✅ Placed at Tier 1 Company         │
│     Role: Software Engineer             │
│     Salary: 14-16 LPA                   │
│     Profile: GPA 8.5 | 5 projects       │
│     [View Full Profile]                 │
│                                         │
│  2. Alumni B (88% similar)              │
│     Graduated: 2023 | CS Major          │
│     ✅ Placed at Tier 1 Company         │
│     Role: Backend Developer             │
│     Salary: 12-14 LPA                   │
│     Profile: GPA 8.2 | 4 projects       │
│     [View Full Profile]                 │
│                                         │
│  3. Alumni C (85% similar)              │
│     Graduated: 2024 | CS Major          │
│     ✅ Placed at Tier 2 Company         │
│     Role: Full Stack Developer          │
│     Salary: 8-10 LPA                    │
│     Profile: GPA 7.8 | 6 projects       │
│     [View Full Profile]                 │
│                                         │
│  Based on 127 alumni in database        │
└─────────────────────────────────────────┘
```

**Features:**
- Top 3 most similar alumni (by cosine similarity)
- Similarity percentage display
- Anonymized names (Alumni A, B, C)
- Placement outcomes (company tier, role, salary)
- Profile summary for comparison
- Expandable full profile view
- Total alumni count in database
- Visual indicators for placement status (✅/❌)

---

### 2.7 Container 6: Gap Analysis

**Purpose:** Show specific gaps between student and successful alumni with LLM narratives.

**Data Required:**
```typescript
interface GapAnalysisData {
  gaps: Array<{
    metric: string;
    studentValue: number;
    alumniAverage: number;
    gap: number; // Positive = student ahead, Negative = student behind
    gapPercentage: number;
    impact: 'High' | 'Medium' | 'Low';
    narrative: string; // LLM-generated explanation
    target: number;
  }>;
  overallGapScore: number; // 0-1 (0 = no gaps, 1 = large gaps)
}
```

**Visual Design:**
```
┌─────────────────────────────────────────┐
│  Gap Analysis                           │
│  vs Top 3 Similar Successful Alumni     │
│                                         │
│  🔴 Problem-Solving (High Impact)       │
│  You: 2/5 | Alumni: 4.2/5 | Gap: -2.2  │
│  ████░░░░░░░░░░░░░░░░ (20% vs 84%)     │
│                                         │
│  💬 Why this matters:                   │
│  Problem-solving is critical for CS     │
│  placements. Alumni with 4+ scores got  │
│  Tier 1 offers 78% of the time vs 32%  │
│  for those with 2-3 scores. This gap    │
│  alone reduces your trajectory by 8pts. │
│                                         │
│  Target: Improve to 4/5 in 8 weeks      │
│  ────────────────────────────────────── │
│                                         │
│  🟡 Screen Time (Medium Impact)         │
│  You: 6h | Alumni: 4.8h | Gap: +1.2h   │
│  ░░░░░░░░░░░░░░░░████ (125% vs 100%)   │
│                                         │
│  💬 Why this matters:                   │
│  Successful alumni averaged 4.8h screen │
│  time. Your 6h indicates lower focus.   │
│  Reducing to 5h can improve behavioral  │
│  score by 5 points.                     │
│                                         │
│  Target: Reduce to 5h in 4 weeks        │
│  ────────────────────────────────────── │
│                                         │
│  ✅ GPA (No Gap)                        │
│  You: 8.6 | Alumni: 8.4 | Gap: +0.2    │
│  ████████████████████ (102% vs 100%)   │
│                                         │
│  💬 Great job!                          │
│  Your GPA exceeds successful alumni.    │
│  Maintain this strength.                │
│                                         │
│  Overall Gap Score: 0.35 (Moderate)     │
│  Close 2-3 key gaps to boost trajectory │
└─────────────────────────────────────────┘
```

**Features:**
- Side-by-side comparison (student vs alumni average)
- Visual gap indicators (progress bars)
- Impact classification (High/Medium/Low)
- LLM-generated narratives explaining why each gap matters
- Real-world impact data (salary, placement rates)
- Specific numeric targets
- Realistic timelines
- Positive reinforcement for strengths
- Overall gap score summary

---

### 2.8 Container 7: Progress Tracking & Gamification

**Purpose:** Motivate students through progress visualization and achievements.

**Data Required:**
```typescript
interface ProgressData {
  trajectoryHistory: Array<{
    date: Date;
    score: number;
  }>;
  achievements: Array<{
    id: string;
    name: string;
    description: string;
    icon: string;
    unlockedAt?: Date;
    progress?: number; // 0-1 for in-progress achievements
  }>;
  streak: {
    current: number; // Days
    longest: number;
  };
  leaderboard: {
    rank: number;
    totalStudents: number;
    percentile: number;
  };
  completedRecommendations: number;
  totalRecommendations: number;
}
```

**Visual Design:**
```
┌─────────────────────────────────────────┐
│  Progress Tracking                      │
│                                         │
│  📈 Trajectory Score Trend (30 days)    │
│  ┌─────────────────────────────────┐   │
│  │ 80│                         ╱   │   │
│  │ 75│                    ╱────    │   │
│  │ 70│               ╱────         │   │
│  │ 65│          ╱────              │   │
│  │ 60│     ╱────                   │   │
│  │   └─────────────────────────────│   │
│  │    Jan  Feb  Mar  Apr  May      │   │
│  └─────────────────────────────────┘   │
│  +8 points in last 30 days! 🎉         │
│                                         │
│  🏆 Achievements (5/12 unlocked)        │
│  ✅ First Login                         │
│  ✅ Profile Complete                    │
│  ✅ Trajectory Score 70+                │
│  ✅ 7-Day Streak                        │
│  ✅ First Recommendation Completed      │
│  🔒 Trajectory Score 80+ (78/80)        │
│  🔒 30-Day Streak (7/30)                │
│  🔒 All Recommendations Completed (1/5) │
│                                         │
│  🔥 Current Streak: 7 days              │
│     Longest Streak: 12 days             │
│                                         │
│  📊 Leaderboard                         │
│     Your Rank: #23 / 156 students       │
│     Top 15% in your major               │
│                                         │
│  ✓ Recommendations: 1/5 completed       │
│  [View All Achievements]                │
└─────────────────────────────────────────┘
```

**Features:**
- 30-day trajectory score trend chart
- Achievement badges (locked/unlocked)
- Progress bars for in-progress achievements
- Streak counter with visual flame icon
- Leaderboard ranking (anonymized)
- Percentile display
- Recommendation completion tracker
- Celebration animations on milestone unlock
- Social sharing (optional)

---

## 3. Admin Dashboard

### 3.1 Dashboard Layout

**Overall Structure:**
```
┌─────────────────────────────────────────────────────────────┐
│  Header: Admin Panel | Total Students | Last Updated        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────────────────────┐ │
│  │  Overview Stats │  │  Score Distribution              │ │
│  │  (KPIs)         │  │  (Histogram)                     │ │
│  └─────────────────┘  └──────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Student List (Filterable Table)                     │  │
│  │  Search | Filter by Major/Score/Status               │  │
│  └──────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────────────────────┐ │
│  │  Behavioral     │  │  Recommendations Analytics       │ │
│  │  Analytics      │  │  (Most Common)                   │ │
│  └─────────────────┘  └──────────────────────────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────┐  │
│  │  Bulk Operations (CSV Import/Export, Batch Actions)  │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

---

### 3.2 Container 1: Overview Stats (KPIs)

**Data Required:**
```typescript
interface AdminOverviewData {
  totalStudents: number;
  totalAlumni: number;
  averageTrajectoryScore: number;
  scoreDistribution: {
    excellent: number; // 90-100
    veryGood: number; // 80-89
    good: number; // 70-79
    fair: number; // 60-69
    belowAverage: number; // 50-59
    poor: number; // 0-49
  };
  atRiskStudents: number; // Score < 50
  topPerformers: number; // Score >= 80
  mobileAppSyncRate: number; // % of students syncing data
  lastUpdated: Date;
}
```

**Visual Design:**
```
┌─────────────────────────────────────────┐
│  Overview Statistics                    │
│                                         │
│  👥 Total Students: 156                 │
│  🎓 Total Alumni: 127                   │
│  📊 Avg Trajectory: 64.2/100            │
│                                         │
│  ⚠️ At-Risk Students: 23 (15%)          │
│  ⭐ Top Performers: 18 (12%)            │
│                                         │
│  📱 Mobile Sync Rate: 78%               │
│     (122/156 students syncing)          │
│                                         │
│  Last updated: 5 minutes ago            │
└─────────────────────────────────────────┘
```

---

### 3.3 Container 2: Score Distribution

**Visual Design:**
```
┌─────────────────────────────────────────┐
│  Trajectory Score Distribution          │
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ 40│     ██                      │   │
│  │ 30│     ██  ████                │   │
│  │ 20│ ██  ██  ████  ██            │   │
│  │ 10│ ██  ██  ████  ██  ██  ██    │   │
│  │  0└─────────────────────────────│   │
│  │    0-49 50-59 60-69 70-79 80-89 │   │
│  │    Poor Fair  Good  VGood Exc   │   │
│  └─────────────────────────────────┘   │
│                                         │
│  Poor (0-49): 23 students (15%)         │
│  Fair (50-69): 78 students (50%)        │
│  Good (70-79): 37 students (24%)        │
│  Very Good (80-89): 15 students (10%)   │
│  Excellent (90-100): 3 students (2%)    │
└─────────────────────────────────────────┘
```

---

### 3.4 Container 3: Student List (Filterable Table)

**Data Required:**
```typescript
interface StudentListData {
  students: Array<{
    id: string;
    name: string;
    email: string;
    major: string;
    semester: number;
    trajectoryScore: number;
    category: string;
    gpa: number;
    lastActive: Date;
    mobileSynced: boolean;
    atRisk: boolean;
  }>;
  filters: {
    major: string[];
    scoreRange: { min: number; max: number };
    semester: number[];
    atRiskOnly: boolean;
  };
  pagination: {
    page: number;
    pageSize: number;
    total: number;
  };
}
```

**Visual Design:**
```
┌─────────────────────────────────────────────────────────────┐
│  Student List                                               │
│                                                             │
│  🔍 Search: [____________]  Major: [All ▼]  Score: [All ▼] │
│  Semester: [All ▼]  ☑ At-Risk Only                         │
│                                                             │
│  ┌───────────────────────────────────────────────────────┐ │
│  │ Name          │ Major │ Sem │ Score │ GPA │ Status   │ │
│  ├───────────────────────────────────────────────────────┤ │
│  │ Arun Pattar   │ CS    │ 7   │ 73    │ 8.6 │ Good     │ │
│  │ Mayur Madiwal │ CS    │ 7   │ 64    │ 8.1 │ Fair     │ │
│  │ Vivek Desai   │ CS    │ 7   │ 64    │ 7.5 │ Fair     │ │
│  │ Sudeep        │ CS    │ 7   │ 62    │ 7.1 │ Fair ⚠️  │ │
│  │ Vaibhava B G  │ CS    │ 6   │ 54    │ 6.3 │ Poor ⚠️  │ │
│  └───────────────────────────────────────────────────────┘ │
│                                                             │
│  Showing 1-5 of 156 students  [< 1 2 3 ... 32 >]           │
│                                                             │
│  Bulk Actions: [Generate Recommendations] [Export CSV]     │
└─────────────────────────────────────────────────────────────┘
```

**Features:**
- Real-time search by name/email
- Multi-select filters (major, semester, score range)
- At-risk indicator (⚠️)
- Mobile sync status indicator
- Sortable columns
- Pagination
- Bulk selection for batch operations
- Click row to view student dashboard
- Export filtered results to CSV

---

### 3.5 Container 4: Behavioral Analytics

**Data Required:**
```typescript
interface BehavioralAnalyticsData {
  averages: {
    screenTime: number;
    focusScore: number;
    sleep: number;
    studyHours: number;
  };
  correlations: Array<{
    metric: string;
    correlation: number; // -1 to 1
    significance: 'High' | 'Medium' | 'Low';
  }>;
  trends: {
    improving: number; // % of students improving
    declining: number; // % of students declining
    stable: number;
  };
}
```

**Visual Design:**
```
┌─────────────────────────────────────────┐
│  Behavioral Analytics                   │
│                                         │
│  📊 Average Metrics (All Students)      │
│  Screen Time: 6.4h/day                  │
│  Focus Score: 0.68                      │
│  Sleep: 7.2h/day                        │
│  Study Hours: 3.5h/day                  │
│                                         │
│  🔗 Correlations with Trajectory        │
│  GPA: +0.72 (High) ✅                   │
│  Study Hours: +0.58 (Medium) ✅         │
│  Screen Time: -0.45 (Medium) ⚠️         │
│  Focus Score: +0.63 (High) ✅           │
│  Sleep: +0.38 (Low) ✅                  │
│                                         │
│  📈 Trends (Last 30 Days)               │
│  Improving: 42% (65 students)           │
│  Declining: 18% (28 students)           │
│  Stable: 40% (63 students)              │
└─────────────────────────────────────────┘
```

---

### 3.6 Container 5: Recommendations Analytics

**Data Required:**
```typescript
interface RecommendationsAnalyticsData {
  mostCommon: Array<{
    recommendation: string;
    count: number;
    percentage: number;
    avgImpact: number;
  }>;
  completionRate: number;
  avgTimeToComplete: number; // days
}
```

**Visual Design:**
```
┌─────────────────────────────────────────┐
│  Recommendations Analytics              │
│                                         │
│  Most Common Recommendations:           │
│  1. Improve Problem-Solving (89 students│
│     57% | Avg Impact: +7 pts            │
│  2. Reduce Screen Time (76 students)    │
│     49% | Avg Impact: +5 pts            │
│  3. Build Consistency (68 students)     │
│     44% | Avg Impact: +4 pts            │
│  4. Get Internship (54 students)        │
│     35% | Avg Impact: +9 pts            │
│  5. Practice Interviews (47 students)   │
│     30% | Avg Impact: +6 pts            │
│                                         │
│  Completion Rate: 23%                   │
│  Avg Time to Complete: 18 days          │
└─────────────────────────────────────────┘
```

---

### 3.7 Container 6: Bulk Operations

**Features:**
- CSV Import (students and alumni data)
- CSV Export (filtered student list)
- Batch recommendation generation
- Batch trajectory recalculation
- Bulk email notifications

**Visual Design:**
```
┌─────────────────────────────────────────┐
│  Bulk Operations                        │
│                                         │
│  📥 Import Data                         │
│  [Upload Student CSV]                   │
│  [Upload Alumni CSV]                    │
│  Template: [Download CSV Template]      │
│                                         │
│  📤 Export Data                         │
│  [Export All Students]                  │
│  [Export Filtered Results]              │
│  [Export Alumni Data]                   │
│                                         │
│  ⚙️ Batch Actions                       │
│  [Generate Recommendations for All]     │
│  [Recalculate All Trajectories]         │
│  [Send Email Notifications]             │
│                                         │
│  📊 Last Batch Operation                │
│  Generated recommendations for 156      │
│  students in 42 minutes                 │
│  Completed: 2 hours ago                 │
└─────────────────────────────────────────┘
```

---

## 4. Component Library

### 4.1 Reusable Components

**ScoreCard Component:**
```typescript
interface ScoreCardProps {
  title: string;
  score: number; // 0-100
  icon: React.ReactNode;
  color: 'success' | 'warning' | 'error';
  trend?: 'up' | 'down' | 'stable';
  subtitle?: string;
}

const ScoreCard: React.FC<ScoreCardProps> = ({
  title,
  score,
  icon,
  color,
  trend,
  subtitle
}) => {
  return (
    <Card sx={{ p: 2 }}>
      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
        {icon}
        <Typography variant="h6" sx={{ ml: 1 }}>
          {title}
        </Typography>
      </Box>
      <Typography variant="h3" color={color}>
        {score}
      </Typography>
      {subtitle && (
        <Typography variant="body2" color="text.secondary">
          {subtitle}
        </Typography>
      )}
      {trend && (
        <Chip
          label={trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'}
          size="small"
          color={trend === 'up' ? 'success' : trend === 'down' ? 'error' : 'default'}
        />
      )}
    </Card>
  );
};
```

**ProgressBar Component:**
```typescript
interface ProgressBarProps {
  label: string;
  value: number; // 0-100
  target?: number;
  color?: 'primary' | 'success' | 'warning' | 'error';
  showPercentage?: boolean;
}

const ProgressBar: React.FC<ProgressBarProps> = ({
  label,
  value,
  target,
  color = 'primary',
  showPercentage = true
}) => {
  const getColor = () => {
    if (target) {
      if (value >= target) return 'success';
      if (value >= target * 0.7) return 'warning';
      return 'error';
    }
    return color;
  };

  return (
    <Box sx={{ mb: 2 }}>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
        <Typography variant="body2">{label}</Typography>
        {showPercentage && (
          <Typography variant="body2">{value}%</Typography>
        )}
      </Box>
      <LinearProgress
        variant="determinate"
        value={value}
        color={getColor()}
        sx={{ height: 8, borderRadius: 4 }}
      />
      {target && (
        <Typography variant="caption" color="text.secondary">
          Target: {target}%
        </Typography>
      )}
    </Box>
  );
};
```

**TrendChart Component:**
```typescript
interface TrendChartProps {
  data: Array<{ date: Date; value: number }>;
  title: string;
  color?: string;
  height?: number;
}

const TrendChart: React.FC<TrendChartProps> = ({
  data,
  title,
  color = '#2196f3',
  height = 200
}) => {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        {title}
      </Typography>
      <ResponsiveContainer width="100%" height={height}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="date" tickFormatter={(date) => format(date, 'MMM dd')} />
          <YAxis />
          <Tooltip />
          <Line type="monotone" dataKey="value" stroke={color} strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};
```

---

## 5. Data Structure

### 5.1 Student Profile Schema

```typescript
interface StudentProfile {
  // Identity
  id: string;
  name: string;
  email: string;
  age: number;
  gender: 'Male' | 'Female' | 'Other';
  
  // Academic
  major: string;
  semester: number;
  college: string;
  gpa: number; // 0-10
  gpatrend: 'Increasing' | 'Decreasing' | 'Stable';
  attendance: number; // 0-100
  internalMarks: number; // 0-100
  backlogs: number;
  
  // Behavioral
  studyHours: number; // per day
  practiceHours: number; // per day
  screenTime: number; // hours per day
  socialMediaTime: number; // hours per day
  sleepHours: number;
  sleepSchedule: 'Fixed' | 'Irregular';
  distractionLevel: number; // 1-5
  consistencyLevel: number; // 1-5
  
  // Skills
  programmingLanguages: string[];
  otherSkills: string[];
  strongestSkill: string;
  problemSolving: number; // 1-5
  communication: number; // 1-5
  teamwork: number; // 1-5
  projects: number;
  projectTypes: string[];
  deployed: boolean;
  internship: boolean;
  internshipDuration?: number; // months
  
  // Mental & Career
  careerClarity: number; // 1-5
  confidence: number; // 1-5
  interviewFear: number; // 1-5
  placementPrep: boolean;
  
  // Calculated Scores
  trajectoryScore: number; // 0-1
  academicScore: number; // 0-1
  behavioralScore: number; // 0-1
  skillsScore: number; // 0-1
  gritScore: number; // 0-1
  focusScore: number; // 0-1
  
  // Metadata
  createdAt: Date;
  updatedAt: Date;
  lastActive: Date;
  mobileSynced: boolean;
  lastSyncAt?: Date;
}
```

### 5.2 Alumni Profile Schema

```typescript
interface AlumniProfile {
  // Identity
  id: string;
  name: string; // Anonymized
  graduationYear: number;
  major: string;
  college: string;
  
  // Academic (historical)
  gpa: number;
  attendance: number;
  backlogs: number;
  
  // Behavioral (historical)
  studyHours: number;
  projects: number;
  internship: boolean;
  
  // Skills (historical)
  programmingLanguages: string[];
  problemSolving: number;
  communication: number;
  
  // Outcome
  placementStatus: 'Placed' | 'Not Placed';
  companyTier?: 'Tier1' | 'Tier2' | 'Tier3';
  companyName?: string; // Anonymized
  role?: string;
  salaryRange?: string; // "12-15 LPA"
  roleToMajorMatch?: number; // 0-100
  
  // Calculated
  trajectoryScore: number; // 0-1
  academicScore: number;
  behavioralScore: number;
  skillsScore: number;
  
  // Metadata
  createdAt: Date;
  updatedAt: Date;
}
```

### 5.3 Recommendation Schema

```typescript
interface Recommendation {
  id: string;
  studentId: string;
  title: string;
  description: string;
  category: 'Academic' | 'Behavioral' | 'Skills';
  impact: 'High' | 'Medium' | 'Low';
  estimatedPoints: number; // +X points
  timeline: string; // "2 weeks"
  actionSteps: string[];
  alumniStory?: string;
  completed: boolean;
  completedAt?: Date;
  generatedAt: Date;
  llmModel: string; // "llama3.1:8b"
}
```

### 5.4 Digital Wellbeing Data Schema

```typescript
interface DigitalWellbeingData {
  id: string;
  studentId: string;
  date: Date;
  
  // Screen Time
  totalScreenTime: number; // hours
  screenTimeByHour: number[]; // 24 values
  
  // App Usage
  appUsage: Array<{
    appName: string;
    category: 'Educational' | 'Social' | 'Entertainment' | 'Productivity' | 'Other';
    duration: number; // minutes
  }>;
  
  // Calculated
  focusScore: number; // 0-1
  educationalTime: number; // hours
  socialMediaTime: number; // hours
  entertainmentTime: number; // hours
  productivityTime: number; // hours
  
  // Sleep
  sleepDuration: number; // hours
  bedtime?: Date;
  wakeTime?: Date;
  
  // Metadata
  syncedAt: Date;
  deviceType: 'Android' | 'iOS';
}
```

---

## 6. API Endpoints

### 6.1 Student Endpoints

**GET /api/students/:id/dashboard**
- Returns: Complete dashboard data for student
- Response:
```json
{
  "student": { /* StudentProfile */ },
  "trajectoryScore": {
    "score": 73,
    "confidenceInterval": { "lower": 68, "upper": 78 },
    "placementLikelihood": { "min": 65, "max": 75 },
    "category": "Good",
    "trend": "up",
    "previousScore": 70
  },
  "components": {
    "academic": { "score": 0.90, "weight": 0.25, "details": {...} },
    "behavioral": { "score": 0.48, "weight": 0.35, "details": {...} },
    "skills": { "score": 0.73, "weight": 0.40, "details": {...} }
  },
  "digitalWellbeing": { /* Last 7 days data */ },
  "recommendations": [ /* Array of recommendations */ ],
  "similarAlumni": [ /* Top 3 matches */ ],
  "gapAnalysis": [ /* Array of gaps */ ],
  "progress": { /* Progress data */ }
}
```

**POST /api/students/:id/recommendations/generate**
- Triggers: LLM Job #2 (Recommendation Generation)
- Body: `{ "regenerate": boolean }`
- Returns: Array of new recommendations

**PATCH /api/students/:id/recommendations/:recId/complete**
- Marks recommendation as complete
- Body: `{ "completed": boolean }`
- Returns: Updated recommendation

**GET /api/students/:id/trajectory/history**
- Returns: 30-day trajectory score history
- Query params: `?days=30`

---

### 6.2 Admin Endpoints

**GET /api/admin/overview**
- Returns: Admin dashboard overview stats
- Response:
```json
{
  "totalStudents": 156,
  "totalAlumni": 127,
  "averageTrajectoryScore": 64.2,
  "scoreDistribution": {
    "excellent": 3,
    "veryGood": 15,
    "good": 37,
    "fair": 78,
    "belowAverage": 18,
    "poor": 5
  },
  "atRiskStudents": 23,
  "topPerformers": 18,
  "mobileSyncRate": 0.78
}
```

**GET /api/admin/students**
- Returns: Paginated student list
- Query params: `?page=1&pageSize=20&major=CS&scoreMin=60&scoreMax=80&atRiskOnly=false`
- Response:
```json
{
  "students": [ /* Array of student summaries */ ],
  "pagination": {
    "page": 1,
    "pageSize": 20,
    "total": 156,
    "totalPages": 8
  }
}
```

**POST /api/admin/import/students**
- Uploads CSV file with student data
- Triggers: LLM Job #1 (Data Cleaning)
- Body: FormData with CSV file
- Returns: Import summary

**POST /api/admin/import/alumni**
- Uploads CSV file with alumni data
- Triggers: LLM Job #1 (Data Cleaning)
- Body: FormData with CSV file
- Returns: Import summary

**POST /api/admin/batch/recommendations**
- Generates recommendations for all students
- Triggers: LLM Job #2 (Batch mode)
- Body: `{ "studentIds": string[] | "all" }`
- Returns: Job ID for tracking

**POST /api/admin/batch/recalculate**
- Recalculates trajectory scores for all students
- Body: `{ "studentIds": string[] | "all" }`
- Returns: Job ID for tracking

**GET /api/admin/analytics/behavioral**
- Returns: Behavioral analytics data
- Response:
```json
{
  "averages": {
    "screenTime": 6.4,
    "focusScore": 0.68,
    "sleep": 7.2,
    "studyHours": 3.5
  },
  "correlations": [
    { "metric": "GPA", "correlation": 0.72, "significance": "High" },
    { "metric": "Study Hours", "correlation": 0.58, "significance": "Medium" }
  ],
  "trends": {
    "improving": 42,
    "declining": 18,
    "stable": 40
  }
}
```

**GET /api/admin/analytics/recommendations**
- Returns: Recommendations analytics
- Response:
```json
{
  "mostCommon": [
    {
      "recommendation": "Improve Problem-Solving",
      "count": 89,
      "percentage": 57,
      "avgImpact": 7
    }
  ],
  "completionRate": 0.23,
  "avgTimeToComplete": 18
}
```

---

### 6.3 Mobile App Endpoints

**POST /api/mobile/sync**
- Syncs digital wellbeing data from mobile app
- Body:
```json
{
  "studentId": "string",
  "data": [
    {
      "date": "2026-02-17",
      "screenTime": 6.2,
      "appUsage": [ /* Array of app usage */ ],
      "sleepDuration": 7.8
    }
  ]
}
```
- Returns: Sync confirmation

**GET /api/mobile/insights/:studentId**
- Returns: Behavioral insights for mobile app
- Response:
```json
{
  "weeklyAverage": {
    "screenTime": 6.2,
    "focusScore": 0.65,
    "sleep": 7.8
  },
  "comparison": {
    "alumniAverage": {
      "screenTime": 4.8,
      "focusScore": 0.82,
      "sleep": 7.5
    }
  },
  "recommendations": [
    "Reduce social media by 1h/day"
  ]
}
```

---

### 6.4 LLM Endpoints

**POST /api/llm/clean-data**
- LLM Job #1: Data Cleaning
- Body: `{ "data": { /* Raw CSV data */ } }`
- Returns: Cleaned data

**POST /api/llm/generate-recommendations**
- LLM Job #2: Recommendation Generation
- Body: `{ "studentId": "string", "context": { /* Student profile + gaps */ } }`
- Returns: Array of recommendations

**POST /api/llm/evaluate-voice**
- LLM Job #3: Voice Assessment Evaluation
- Body: `{ "studentId": "string", "transcript": "string", "question": "string" }`
- Returns: Evaluation scores + feedback

**POST /api/llm/generate-gap-narrative**
- LLM Job #4: Gap Analysis Narrative
- Body: `{ "studentId": "string", "gap": { /* Gap data */ } }`
- Returns: Narrative text

**POST /api/llm/analyze-skill-demand**
- LLM Job #5: Skill Market Demand Analysis
- Body: `{ "skill": "string", "major": "string", "year": 2026 }`
- Returns: Market weight (0.5x, 1.0x, or 2.0x) + reasoning

**GET /api/llm/health**
- Returns: LLM server health status
- Response:
```json
{
  "status": "healthy",
  "model": "llama3.1:8b",
  "gpuAvailable": true,
  "gpuMemoryUsed": "4.2GB",
  "avgResponseTime": "0.8s"
}
```

---

## 7. UI/UX Guidelines

### 7.1 Design Principles

**1. Clarity Over Complexity**
- Use plain language, avoid jargon
- Explain what trajectory score means in simple terms
- Provide context for every metric

**2. Data-Driven Insights**
- Always show "why" behind recommendations
- Include alumni success stories for motivation
- Display confidence intervals to manage expectations

**3. Actionable Information**
- Every insight should lead to a clear action
- Provide specific targets (not vague advice)
- Include realistic timelines

**4. Positive Reinforcement**
- Celebrate improvements and milestones
- Highlight strengths, not just weaknesses
- Use encouraging language

**5. Mobile-First**
- Responsive design for all screen sizes
- Touch-friendly buttons and controls
- Optimized for mobile app integration

---

### 7.2 Color Palette

**Primary Colors:**
- Primary Blue: `#2196f3` (Buttons, links, accents)
- Success Green: `#4caf50` (Positive indicators, achievements)
- Warning Orange: `#ff9800` (Moderate alerts, cautions)
- Error Red: `#f44336` (Critical issues, at-risk indicators)

**Score Category Colors:**
- Excellent (90-100): `#4caf50` (Green)
- Very Good (80-89): `#8bc34a` (Light Green)
- Good (70-79): `#cddc39` (Yellow-Green)
- Fair (60-69): `#ff9800` (Orange)
- Below Average (50-59): `#ff5722` (Red-Orange)
- Poor (0-49): `#f44336` (Red)

**Neutral Colors:**
- Background: `#fafafa`
- Card Background: `#ffffff`
- Text Primary: `#212121`
- Text Secondary: `#757575`
- Divider: `#e0e0e0`

---

### 7.3 Typography

**Font Family:**
- Primary: `'Roboto', 'Helvetica', 'Arial', sans-serif`
- Monospace (for code/data): `'Roboto Mono', monospace`

**Font Sizes:**
- H1: 48px (Page titles)
- H2: 36px (Section headers)
- H3: 28px (Card titles)
- H4: 24px (Subsection headers)
- H5: 20px (Component titles)
- H6: 18px (Small headers)
- Body: 16px (Regular text)
- Caption: 14px (Secondary text)
- Small: 12px (Metadata, timestamps)

**Font Weights:**
- Light: 300
- Regular: 400
- Medium: 500
- Bold: 700

---

### 7.4 Spacing & Layout

**Grid System:**
- 12-column grid
- Gutter: 24px
- Container max-width: 1200px

**Spacing Scale:**
- xs: 4px
- sm: 8px
- md: 16px
- lg: 24px
- xl: 32px
- xxl: 48px

**Card Padding:**
- Small cards: 16px
- Medium cards: 24px
- Large cards: 32px

**Border Radius:**
- Small: 4px
- Medium: 8px
- Large: 16px
- Circular: 50%

---

### 7.5 Icons

**Material Icons Usage:**
- 📊 Trajectory Score
- 📚 Academic
- 🧠 Behavioral
- 💻 Skills
- 📱 Screen Time
- 🎯 Focus Score
- 😴 Sleep
- 🏆 Achievements
- 🔥 Streak
- ⚠️ At-Risk
- ✅ Complete
- 🔒 Locked
- 📈 Trending Up
- 📉 Trending Down
- 💡 Recommendation
- 👥 Alumni

---

### 7.6 Animations & Transitions

**Hover Effects:**
- Cards: Slight elevation increase (shadow)
- Buttons: Background color darken
- Links: Underline appear

**Loading States:**
- Skeleton screens for data loading
- Circular progress for LLM operations
- Linear progress for batch operations

**Transitions:**
- Duration: 200-300ms
- Easing: `cubic-bezier(0.4, 0.0, 0.2, 1)`

**Celebrations:**
- Confetti animation on achievement unlock
- Pulse animation on score improvement
- Checkmark animation on recommendation completion

---

### 7.7 Responsive Breakpoints

**Breakpoints:**
- xs: 0px (Mobile portrait)
- sm: 600px (Mobile landscape)
- md: 960px (Tablet)
- lg: 1280px (Desktop)
- xl: 1920px (Large desktop)

**Layout Adjustments:**
- Mobile (xs-sm): Single column, stacked cards
- Tablet (md): 2-column grid for some sections
- Desktop (lg-xl): 3-column grid, side-by-side layouts

---

### 7.8 Accessibility

**WCAG 2.1 AA Compliance:**
- Color contrast ratio ≥ 4.5:1 for text
- Color contrast ratio ≥ 3:1 for UI components
- Keyboard navigation support
- Screen reader friendly (ARIA labels)
- Focus indicators on interactive elements
- Alt text for all images/icons

**Keyboard Shortcuts:**
- `/` - Focus search
- `Esc` - Close modals
- `Tab` - Navigate between elements
- `Enter` - Activate buttons/links

---

## 8. Development Guide

### 8.1 Project Setup

**Frontend (React + TypeScript):**
```bash
# Create React app with TypeScript
npx create-react-app trajectory-dashboard --template typescript

# Install dependencies
cd trajectory-dashboard
npm install @mui/material @emotion/react @emotion/styled
npm install @reduxjs/toolkit react-redux
npm install react-router-dom
npm install recharts react-sparklines
npm install axios
npm install date-fns
npm install react-hook-form yup @hookform/resolvers
```

**Backend (FastAPI + Python):**
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastapi uvicorn
pip install sqlalchemy psycopg2-binary
pip install pydantic
pip install numpy pandas scikit-learn
pip install qdrant-client
pip install redis
pip install celery
pip install python-multipart  # For file uploads
pip install ollama  # For LLM integration
```

**Mobile (React Native):**
```bash
# Create React Native app
npx react-native init TrajectoryMobile --template react-native-template-typescript

# Install dependencies
cd TrajectoryMobile
npm install @react-navigation/native @react-navigation/stack
npm install @reduxjs/toolkit react-redux
npm install axios
npm install @react-native-async-storage/async-storage
npm install react-native-sqlite-storage
```

---

### 8.2 Folder Structure

**Frontend:**
```
trajectory-dashboard/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── ScoreCard.tsx
│   │   │   ├── ProgressBar.tsx
│   │   │   ├── TrendChart.tsx
│   │   │   └── LoadingState.tsx
│   │   ├── student/
│   │   │   ├── TrajectoryScoreCard.tsx
│   │   │   ├── ComponentBreakdown.tsx
│   │   │   ├── DigitalWellbeingMetrics.tsx
│   │   │   ├── Recommendations.tsx
│   │   │   ├── SimilarAlumni.tsx
│   │   │   ├── GapAnalysis.tsx
│   │   │   └── ProgressTracking.tsx
│   │   └── admin/
│   │       ├── OverviewStats.tsx
│   │       ├── ScoreDistribution.tsx
│   │       ├── StudentList.tsx
│   │       ├── BehavioralAnalytics.tsx
│   │       └── BulkOperations.tsx
│   ├── pages/
│   │   ├── StudentDashboard.tsx
│   │   ├── AdminDashboard.tsx
│   │   └── Login.tsx
│   ├── store/
│   │   ├── slices/
│   │   │   ├── studentSlice.ts
│   │   │   ├── adminSlice.ts
│   │   │   └── authSlice.ts
│   │   └── store.ts
│   ├── services/
│   │   ├── api.ts
│   │   ├── studentService.ts
│   │   └── adminService.ts
│   ├── types/
│   │   ├── student.ts
│   │   ├── alumni.ts
│   │   └── recommendation.ts
│   ├── utils/
│   │   ├── formatters.ts
│   │   └── validators.ts
│   ├── App.tsx
│   └── index.tsx
├── public/
├── package.json
└── tsconfig.json
```

**Backend:**
```
trajectory-backend/
├── app/
│   ├── api/
│   │   ├── endpoints/
│   │   │   ├── students.py
│   │   │   ├── admin.py
│   │   │   ├── mobile.py
│   │   │   └── llm.py
│   │   └── router.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   ├── models/
│   │   ├── student.py
│   │   ├── alumni.py
│   │   ├── recommendation.py
│   │   └── digital_wellbeing.py
│   ├── services/
│   │   ├── data_cleaning.py  # LLM Job #1
│   │   ├── recommendation_engine.py  # LLM Job #2
│   │   ├── voice_evaluation.py  # LLM Job #3
│   │   ├── gap_analysis.py  # LLM Job #4
│   │   ├── skill_demand_analysis.py  # LLM Job #5
│   │   ├── vector_engine.py
│   │   ├── prediction_engine.py
│   │   └── behavioral_analysis.py
│   ├── schemas/
│   │   ├── student.py
│   │   ├── alumni.py
│   │   └── recommendation.py
│   └── main.py
├── tests/
├── requirements.txt
└── .env
```

---

### 8.3 Environment Variables

**Frontend (.env):**
```
REACT_APP_API_URL=http://localhost:8000
REACT_APP_ENV=development
```

**Backend (.env):**
```
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/trajectory_db

# Qdrant
QDRANT_HOST=localhost
QDRANT_PORT=6333

# Redis
REDIS_URL=redis://localhost:6379

# Ollama
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Environment
ENV=development
```

---

### 8.4 Database Setup

**PostgreSQL Schema:**
```sql
-- Students table
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    major VARCHAR(100),
    semester INTEGER,
    gpa DECIMAL(3,2),
    attendance DECIMAL(5,2),
    trajectory_score DECIMAL(3,2),
    academic_score DECIMAL(3,2),
    behavioral_score DECIMAL(3,2),
    skills_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Alumni table
CREATE TABLE alumni (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255),
    graduation_year INTEGER,
    major VARCHAR(100),
    gpa DECIMAL(3,2),
    placement_status VARCHAR(50),
    company_tier VARCHAR(20),
    salary_range VARCHAR(50),
    trajectory_score DECIMAL(3,2),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Recommendations table
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id),
    title VARCHAR(255),
    description TEXT,
    category VARCHAR(50),
    impact VARCHAR(20),
    estimated_points INTEGER,
    completed BOOLEAN DEFAULT FALSE,
    generated_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP
);

-- Digital Wellbeing table
CREATE TABLE digital_wellbeing (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID REFERENCES students(id),
    date DATE,
    screen_time DECIMAL(4,2),
    focus_score DECIMAL(3,2),
    sleep_duration DECIMAL(4,2),
    synced_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_students_major ON students(major);
CREATE INDEX idx_students_trajectory ON students(trajectory_score);
CREATE INDEX idx_alumni_major ON alumni(major);
CREATE INDEX idx_recommendations_student ON recommendations(student_id);
CREATE INDEX idx_wellbeing_student_date ON digital_wellbeing(student_id, date);
```

---

### 8.5 Development Workflow

**Day 1-2: Setup & Infrastructure**
- Set up React + TypeScript project
- Set up FastAPI backend
- Configure PostgreSQL database
- Set up Qdrant vector database
- Install and configure Ollama
- Set up React Native mobile app project

**Day 3-4: Student Dashboard - Core Components**
- Implement TrajectoryScoreCard component
- Implement ComponentBreakdown component
- Create API endpoints for student data
- Implement vector generation logic
- Test trajectory score calculation

**Day 5-6: Student Dashboard - Behavioral & Recommendations**
- Implement DigitalWellbeingMetrics component
- Implement Recommendations component (LLM Job #2)
- Create mobile app data sync API
- Test LLM recommendation generation

**Day 7-8: Student Dashboard - Alumni & Gaps**
- Implement SimilarAlumni component
- Implement GapAnalysis component (LLM Job #4)
- Implement similarity matching with Qdrant
- Test gap analysis narratives

**Day 9-10: Admin Dashboard**
- Implement OverviewStats component
- Implement StudentList with filters
- Implement BehavioralAnalytics component
- Create CSV import/export functionality (LLM Job #1)

**Day 11-12: Mobile App**
- Implement screen time tracking
- Implement app usage categorization
- Implement sleep detection
- Implement data sync to backend
- Test mobile app on Android device

**Day 13-14: Testing & Optimization**
- End-to-end testing
- LLM performance optimization
- Mobile app battery optimization
- Fix bugs and edge cases

**Day 15: Demo Preparation**
- Prepare demo data (7 students from sudent2.csv)
- Create demo script
- Test all features
- Deploy to staging environment

---

### 8.6 Testing Strategy

**Unit Tests:**
- Test formula calculations (trajectory, academic, behavioral, skills)
- Test normalization functions
- Test vector generation
- Test similarity calculations

**Integration Tests:**
- Test API endpoints
- Test LLM integration
- Test database operations
- Test mobile app sync

**End-to-End Tests:**
- Test complete student dashboard flow
- Test admin dashboard flow
- Test mobile app data collection and sync
- Test recommendation generation and completion

**Performance Tests:**
- Test LLM response time (<2s)
- Test vector search speed (<100ms)
- Test batch operations (156 students)
- Test mobile app battery usage (<5%/day)

---

### 8.7 Deployment

**Frontend Deployment (Vercel/Netlify):**
```bash
# Build production bundle
npm run build

# Deploy to Vercel
vercel --prod
```

**Backend Deployment (Docker):**
```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Mobile App Deployment:**
```bash
# Android
cd android
./gradlew assembleRelease

# iOS
cd ios
xcodebuild -workspace TrajectoryMobile.xcworkspace -scheme TrajectoryMobile -configuration Release
```

---

### 8.8 Monitoring & Maintenance

**Metrics to Track:**
- API response times
- LLM success rate and latency
- Database query performance
- Mobile app sync rate
- User engagement (daily active users)
- Recommendation completion rate

**Logging:**
- API request/response logs
- LLM operation logs
- Error logs with stack traces
- Mobile app crash reports

**Alerts:**
- LLM server down
- Database connection issues
- High API error rate (>5%)
- Low mobile sync rate (<70%)

---

## 9. Summary

This comprehensive dashboard specification provides:

1. **Two Complete Dashboards:**
   - Student Dashboard (7 containers)
   - Admin Dashboard (6 containers)

2. **Mobile App Integration:**
   - Automatic data collection
   - Daily sync
   - Behavioral insights

3. **LLM Integration:**
   - 5 LLM jobs (data cleaning, recommendations, voice evaluation, gap narratives, skill demand analysis)
   - Local deployment (Ollama + Llama 3.1 8B)
   - Zero cloud costs

4. **Complete Technical Stack:**
   - Frontend: React + TypeScript + MUI
   - Backend: FastAPI + PostgreSQL + Qdrant
   - Mobile: React Native
   - LLM: Ollama (Llama 3.1 8B)

5. **Production-Ready Features:**
   - Responsive design
   - Accessibility compliant
   - Performance optimized
   - Comprehensive testing

**Total Development Time:** 15 days (MVP)

**Expected Accuracy:** 85-90% trajectory prediction accuracy

**Cost:** $0 (all local, no cloud APIs)

---

**Document Version:** 1.0  
**Last Updated:** February 17, 2026  
**Status:** Ready for Development ✅
