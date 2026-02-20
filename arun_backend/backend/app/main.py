from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routes import students, analytics, metrics, gamification, community, activities, auth, prediction, admin, student_profile, skills, behavioral
import os

# Create FastAPI app with enhanced documentation
app = FastAPI(
    title="Trajectory-X API",
    description="Advanced AI-powered University Student Trajectory Planning & Analytics",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Local frontend development
        "http://localhost:5173",  # Vite default port
        "https://*.trycloudflare.com",  # Cloudflare Tunnel (wildcard for any tunnel URL)
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(auth.router)  # Authentication routes
app.include_router(prediction.router)  # Trajectory prediction endpoint
app.include_router(admin.router)  # Admin routes (CSV import, templates, analytics)
app.include_router(student_profile.router)  # Student profile management (Task 20)
app.include_router(skills.router)  # Skill assessment system (Task 21)
app.include_router(behavioral.router)  # Behavioral analysis (Task 22)
app.include_router(students.router)
app.include_router(analytics.router)
app.include_router(metrics.router)
app.include_router(gamification.router)
app.include_router(community.router)
app.include_router(activities.router)  # NEW: Schedule/Todo/Planner endpoints

# Mount static folder to serve uploaded memes and reels
# Ensure the directory exists
STATIC_DIR = os.path.join(os.path.dirname(__file__), "..", "static")
if not os.path.exists(STATIC_DIR):
    os.makedirs(STATIC_DIR)
    os.makedirs(os.path.join(STATIC_DIR, "uploads"))

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# Optional root route to show backend status
@app.get("/")
def root():
    return {"status": "Trajectory-X backend running"}
