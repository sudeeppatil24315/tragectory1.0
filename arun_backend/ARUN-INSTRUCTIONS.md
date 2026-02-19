# Instructions for Arun - Database Migration

**Date:** February 18, 2026  
**Task:** Apply database migrations to your PostgreSQL  
**Time:** 5-10 minutes

---

## What You Need to Do

I've updated the database models and set up Alembic for you. You just need to apply the changes to your PostgreSQL database.

### Quick Start (Easiest Way)

1. **Get the updated code** (I'll share the `arun_backend` folder with you)

2. **Open Command Prompt** and navigate to the backend folder:
```bash
cd path\to\arun_backend\backend
```

3. **Run the setup script:**
```bash
setup_alembic.bat
```

4. **Follow the prompts** - it will:
   - Install new packages (alembic, numpy, scikit-learn, pandas)
   - Generate a migration file
   - Ask you to review it
   - Apply the migration to your database

5. **Done!** Your database now has:
   - ✅ Alumni table (for predictions)
   - ✅ Skills table (for skill assessments)
   - ✅ Updated Students table (with constraints)
   - ✅ Updated other tables

---

## What Changed

### New Tables Created:
1. **alumni** - Stores graduated student data with employment outcomes
2. **skills** - Stores individual skill assessments with market demand weighting

### Existing Tables Updated:
3. **students** - Added GPA/attendance constraints
4. **digital_wellbeing_data** - Renamed from digital_wellbeing_daily
5. **trajectory_scores** - Added confidence, trend, velocity fields
6. **recommendations** - Renamed some fields

---

## Verification

After running the script, verify in PostgreSQL:

```sql
-- Connect to database
psql -U postgres -d trajectory

-- Check tables
\dt

-- You should see 'alumni' and 'skills' tables

-- Check alumni structure
\d alumni

-- Check skills structure
\d skills

-- Exit
\q
```

---

## If You Have Issues

### Issue 1: "pip is not recognized"
**Solution:** Make sure you're in the virtual environment
```bash
venv\Scripts\activate
```

### Issue 2: "alembic is not recognized"
**Solution:** Install it manually
```bash
pip install alembic
```

### Issue 3: "Table already exists"
**Solution:** Tell Alembic to skip
```bash
alembic stamp head
```

### Issue 4: Need help?
**Solution:** Share the error message with me and I'll help!

---

## What Happens Next

After you apply the migration:
1. I'll continue building the rest of the system
2. We'll test creating alumni and skill records
3. We'll integrate with the prediction engine

---

## Files You'll See

After running the script, you'll have:
- `alembic/versions/abc123_initial_schema.py` - The migration file
- `alembic.ini` - Configuration file
- Updated `requirements.txt` - With new packages

---

## Questions?

- **What is Alembic?** - It's like Git for your database. Tracks changes automatically.
- **Will this delete my data?** - No! It only adds new tables and updates existing ones.
- **Can I undo it?** - Yes! Run `alembic downgrade -1` to rollback.
- **Do I need to do this every time?** - Only when models change. Alembic makes it automatic.

---

## Ready?

Just run `setup_alembic.bat` and you're done! 🚀

Let me know when it's complete!
