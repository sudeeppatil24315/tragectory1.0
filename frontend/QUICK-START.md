# Frontend Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

### Step 2: Start Frontend
```bash
npm run dev
```
✅ Frontend will run on http://localhost:3000

### Step 3: Ensure Backend is Running
In another terminal:
```bash
cd arun_backend/backend
python -m uvicorn app.main:app --reload
```
✅ Backend will run on http://localhost:8000

## 🎯 Test Authentication

1. Open http://localhost:3000
2. Click "Register here"
3. Fill the form:
   - Email: test@example.com
   - Password: password123
   - Confirm Password: password123
   - Role: Student
4. Click "Register"
5. You should see the dashboard!

## ⚠️ Important Note

**PostgreSQL must be running** for authentication to work.

If you see errors, you need to set up PostgreSQL:
- See `arun_backend/LOCAL-POSTGRES-SETUP.md` for instructions
- Or connect to Arun's remote database

## 📁 What You Get

- Modern login/register pages
- JWT authentication
- Protected dashboard
- Responsive design
- Error handling

## 🐛 Troubleshooting

**"Cannot connect to backend"**
- Make sure FastAPI server is running on port 8000
- Check: http://localhost:8000/docs

**"500 Internal Server Error"**
- PostgreSQL is not running or not accessible
- Follow `LOCAL-POSTGRES-SETUP.md`

**"CORS Error"**
- Backend CORS is already configured
- Restart both frontend and backend

## 📝 Next Steps

Once authentication works:
- Task 4: Checkpoint verification
- Task 5+: Build core prediction engine
- Add dashboard features (trajectory score, recommendations, etc.)
