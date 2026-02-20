# 🎯 Next Steps Checklist

You've installed PostgreSQL with pgAdmin 4. Here's what to do next:

## ✅ Step-by-Step Checklist

### [ ] 1. Update Password in .env
**File:** `arun_backend/.env`

Change this line to match your PostgreSQL password:
```
DB_PASSWORD=YOUR_ACTUAL_PASSWORD
```

**How to find your password:**
- It's the password you set when installing PostgreSQL
- The one you use to login to pgAdmin 4

---

### [ ] 2. Create Database in pgAdmin 4
**See:** `CREATE-DATABASE-PGADMIN.md` for detailed steps

**Quick version:**
1. Open pgAdmin 4
2. Connect to PostgreSQL 18
3. Right-click "Databases" → Create → Database
4. Name: `trajectory`
5. Click Save

---

### [ ] 3. Run Database Migrations
**Command:**
```cmd
cd arun_backend\backend
alembic upgrade head
```

**Expected output:**
```
INFO  [alembic.runtime.migration] Running upgrade -> abc123, Create users table
INFO  [alembic.runtime.migration] Running upgrade abc123 -> def456, Create students table
...
```

---

### [ ] 4. Test Backend Authentication
**Command:**
```cmd
cd arun_backend\backend
python test_auth.py
```

**Expected output:**
```
✅ Test 1: User Registration - PASSED
✅ Test 2: User Login - PASSED
✅ Test 3: Get Current User - PASSED
✅ Test 4: Invalid Credentials - PASSED
✅ Test 5: Duplicate Registration - PASSED

All tests passed! 🎉
```

---

### [ ] 5. Install Frontend Dependencies
**Command:**
```cmd
cd frontend
npm install
```

**Wait for:** All packages to install (may take 2-3 minutes)

---

### [ ] 6. Start Frontend
**Command:**
```cmd
npm run dev
```

**Expected output:**
```
VITE v5.0.8  ready in 500 ms

➜  Local:   http://localhost:3000/
```

---

### [ ] 7. Test Full Authentication Flow
**Steps:**
1. Open browser: http://localhost:3000
2. Click "Register here"
3. Fill form:
   - Email: test@example.com
   - Password: password123
   - Confirm: password123
   - Role: Student
4. Click "Register"
5. Should see Dashboard with your email!
6. Click "Logout"
7. Login again with same credentials
8. Should see Dashboard again!

---

## 🎉 Success Criteria

You'll know everything works when:
- ✅ Backend test script shows all tests passed
- ✅ Frontend loads at http://localhost:3000
- ✅ You can register a new account
- ✅ You can login with credentials
- ✅ Dashboard shows your email and role
- ✅ Logout works and redirects to login

---

## 🐛 Common Issues

### Issue: "Password authentication failed"
**Solution:** Update `DB_PASSWORD` in `.env` file

### Issue: "Database 'trajectory' does not exist"
**Solution:** Create database in pgAdmin 4 (Step 2)

### Issue: "alembic: command not found"
**Solution:** Run `python -m alembic upgrade head` instead

### Issue: "Cannot connect to backend"
**Solution:** Make sure FastAPI server is running:
```cmd
cd arun_backend\backend
python -m uvicorn app.main:app --reload
```

### Issue: "npm: command not found"
**Solution:** Install Node.js from https://nodejs.org/

---

## 📁 Quick Reference

**Backend Server:**
```cmd
cd arun_backend\backend
python -m uvicorn app.main:app --reload
```
Runs on: http://localhost:8000

**Frontend Server:**
```cmd
cd frontend
npm run dev
```
Runs on: http://localhost:3000

**Test Authentication:**
```cmd
cd arun_backend\backend
python test_auth.py
```

---

## 🎯 Current Status

**Completed:**
- ✅ PostgreSQL installed (version 18)
- ✅ pgAdmin 4 installed
- ✅ Backend code complete
- ✅ Frontend code complete
- ✅ FastAPI server running

**Pending:**
- ⏳ Create database in pgAdmin 4
- ⏳ Update password in .env
- ⏳ Run migrations
- ⏳ Test authentication

---

## 💡 Tips

1. **Keep terminals open:** You'll need 2 terminals running:
   - Terminal 1: Backend server
   - Terminal 2: Frontend server

2. **Check server status:** 
   - Backend: http://localhost:8000/docs
   - Frontend: http://localhost:3000

3. **Clear browser cache:** If you see old errors, clear cache or use incognito mode

4. **Check logs:** If something fails, check the terminal output for error messages

---

## 📞 Need Help?

Just tell me which step you're on and what's happening. I'll help you through it!

**Example:**
- "I'm on step 2, can't find pgAdmin 4"
- "Step 3 failed with error: ..."
- "Everything works! What's next?"
