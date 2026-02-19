# Trajectory-X - AI-Powered Student Trajectory Planning System

A comprehensive student management system with AI-powered vector database for personalized career trajectory predictions and recommendations.

## 🎯 Features

- **Student Management** - Complete student profile management
- **Activity Tracking** - Daily schedule, to-do lists, and day planner
- **Vector Database** - AI-powered semantic search and recommendations
- **Analytics** - Trajectory scores, gap analysis, and insights
- **Gamification** - Badges and achievements
- **Community** - Social features for student engagement

## 🗄️ Database Tables

- `students` - Student profiles and academic data
- `student_activities` - Schedule, todos, and day plans
- `vector_profiles` - AI embeddings for each student
- `behavioral_metrics` - Study habits and soft skills
- `digital_wellbeing_daily` - Screen time and health tracking
- `gap_analysis` - Performance vs. target metrics
- `recommendations` - AI-generated personalized tasks
- And more...

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m pip install -r requirements.txt
python -m pip install python-multipart
```

### 2. Configure Database

Edit `backend/app/db.py`:

```python
DATABASE_URL = "postgresql://username:password@localhost:5432/trajectory_x"
```

### 3. Setup Database Tables

```bash
python create_activity_table.py
python import_csv_data.py  # If you have student data CSV
```

### 4. Generate AI Vectors

```bash
python vectorize_all.py
```

### 5. Start Server

```bash
python -m uvicorn app.main:app --reload --port 8000
```

Or use the batch file:
```bash
start_server.bat
```

### 6. Access API Documentation

Open browser: **http://localhost:8000/docs**

## 📡 API Endpoints

### Activities
- `POST /activities/` - Create activity
- `GET /activities/` - Get activities (with filters)
- `PATCH /activities/{id}` - Update activity
- `DELETE /activities/{id}` - Delete activity
- `GET /activities/schedule/today` - Today's schedule
- `GET /activities/todos/pending` - Pending todos

### Students
- `POST /students/` - Create student
- `GET /students/` - Get all students
- `GET /students/{id}` - Get specific student

### Analytics
- `GET /analytics/trajectory-score` - Get trajectory score
- `GET /analytics/gap-analysis` - Gap analysis

## 🧬 Vector Database

The system uses AI embeddings to represent student profiles as 384-dimensional vectors. This enables:

- **Semantic Search** - Find similar students
- **Personalized Recommendations** - AI-powered suggestions
- **Pattern Recognition** - Identify success patterns
- **Predictive Analytics** - Career trajectory predictions

### How it works:

1. Student data (GPA, projects, habits, planning behavior) → Text summary
2. Text summary → AI model → 384-dimensional vector
3. Vector stored in PostgreSQL
4. LLM analyzes vectors for insights

## 📁 Project Structure

```
trajectory-x-main/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # Database models
│   │   ├── db.py                # Database connection
│   │   ├── routes/              # API endpoints
│   │   │   ├── activities.py
│   │   │   ├── students.py
│   │   │   ├── analytics.py
│   │   │   └── ...
│   │   └── services/            # Business logic
│   │       ├── vector_gen_service.py
│   │       └── ...
│   ├── create_activity_table.py # Setup script
│   ├── import_csv_data.py       # Data import
│   ├── vectorize_all.py         # Generate vectors
│   ├── verify_vectors.py        # Verify vector storage
│   └── requirements.txt         # Dependencies
├── start_server.bat             # Quick start script
└── README.md
```

## 🧪 Testing

### Using Swagger UI (Recommended)

1. Start server
2. Open http://localhost:8000/docs
3. Test endpoints interactively

### Using Postman

**GET Activities:**
```
GET http://localhost:8000/activities/?student_id=1&activity_date=2026-02-17
```

**POST Activity:**
```
POST http://localhost:8000/activities/?student_id=1
Body (JSON):
{
  "date": "2026-02-17",
  "title": "Physics Class",
  "activity_type": "schedule",
  "category": "class",
  "start_time": "10:00:00",
  "end_time": "11:00:00",
  "priority": 2
}
```

## 🔧 Maintenance Scripts

- `create_activity_table.py` - Create activity table
- `import_csv_data.py` - Import student data from CSV
- `vectorize_all.py` - Generate/update AI vectors
- `verify_vectors.py` - Check vector storage

## 📊 Data Format

### Activity Types
- `"schedule"` - Time-bound events (classes, meetings)
- `"todo"` - Tasks without specific time
- `"plan"` - Planned time blocks

### Date/Time Format
- **Date**: `YYYY-MM-DD` (e.g., `2026-02-17`)
- **Time**: `HH:MM:SS` (e.g., `14:30:00`)

### Priority Levels
- `1` - High priority
- `2` - Medium priority
- `3` - Low priority

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Database**: PostgreSQL
- **AI/ML**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Storage**: PostgreSQL ARRAY(Float)
- **API Docs**: Swagger/OpenAPI

## 📝 License

[Your License Here]

## 🤝 Contributing

[Your Contributing Guidelines]

## 📧 Contact

[Your Contact Information]

---

**Built with ❤️ for student success**
