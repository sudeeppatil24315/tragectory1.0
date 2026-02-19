@echo off
echo Starting FastAPI Server...
echo.
echo Server will run at: http://localhost:8000
echo API Docs available at: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
uvicorn app.main:app --reload --port 8000
