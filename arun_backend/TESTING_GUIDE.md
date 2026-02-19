# How to Test the Activity APIs

## Step 1: Start the Server

Run this command:
```bash
python -m uvicorn app.main:app --reload
```

Or double-click: `start_server.bat`

The server will start at: http://localhost:8000

## Step 2: Open Interactive API Docs

Go to: **http://localhost:8000/docs**

You'll see a beautiful Swagger UI with all your endpoints!

## Step 3: Test Each Endpoint

### Test 1: Create a Schedule Event

1. Find `POST /activities/`
2. Click "Try it out"
3. Enter `student_id`: `1`
4. Enter this JSON:
```json
{
  "date": "2026-02-17",
  "title": "Data Structures Class",
  "description": "Learning Binary Trees",
  "activity_type": "schedule",
  "category": "class",
  "start_time": "09:00:00",
  "end_time": "11:00:00",
  "priority": 2
}
```
5. Click "Execute"
6. You should see a 200 response with the created activity!

### Test 2: Get All Activities

1. Find `GET /activities/`
2. Click "Try it out"
3. Enter `student_id`: `1`
4. Enter `activity_date`: `2026-02-17`
5. Click "Execute"
6. You'll see all activities for that day!

### Test 3: Mark as Complete

1. Find `PATCH /activities/{activity_id}`
2. Enter the `activity_id` from Test 1
3. Enter JSON:
```json
{
  "is_completed": true
}
```
4. Click "Execute"
5. Activity is now marked complete!

## Step 4: Run Automated Tests

```bash
python backend/test_activity_apis.py
```

This will test all endpoints automatically.

## Step 5: Update Vectors with Planning Data

```bash
python backend/vectorize_all.py
```

Now your vectors include planning behavior!

## What You Can Check in Database

Open pgAdmin and run:

```sql
-- See all activities
SELECT * FROM student_activities;

-- See updated vectors with planning data
SELECT 
    student_id, 
    LEFT(profile_summary, 200) as summary_preview
FROM vector_profiles;
```

You should see "Planning Behavior: Task completion rate..." in the summary!

## Next Steps

1. Build a frontend to use these APIs
2. Let the LLM analyze planning patterns
3. Generate recommendations based on completion rates

Enjoy your new planner feature! 🎉
