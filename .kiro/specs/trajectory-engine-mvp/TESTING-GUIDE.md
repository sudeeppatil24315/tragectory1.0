# Testing Guide: Prediction Endpoint

**Date:** February 20, 2026  
**Status:** Ready for Testing

---

## Quick Start

### Step 1: Start the Backend Server

Open a terminal in the backend directory and run:

```bash
cd arun_backend/backend
python -m uvicorn app.main:app --reload
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

### Step 2: Verify Qdrant is Running

Make sure Qdrant is running on port 6333:

```bash
# Check if Qdrant is running
curl http://localhost:6333/collections
```

If Qdrant is not running, start it:
```bash
# If using Docker
docker run -p 6333:6333 qdrant/qdrant

# Or if installed locally
qdrant
```

### Step 3: Run the Test Script

Open a **NEW terminal** (keep the backend running) and run:

```bash
cd arun_backend/backend
python test_prediction_endpoint.py
```

---

## Expected Test Output

If everything is working correctly, you should see:

```
============================================================
TESTING PREDICTION ENDPOINT
============================================================

1. Registering/Logging in test user...
✓ User registered successfully

2. Calling prediction endpoint...
   Status Code: 200
✓ Prediction successful!

============================================================
PREDICTION RESULTS
============================================================

Trajectory Score: 75.7/100
Predicted Tier: Tier1
Confidence: 0.77 (±4.5)
Trend: stable (velocity: 0.00)

Component Scores:
  Academic:    72.4
  Behavioral:  48.0
  Skills:      52.6

Component Weights:
  Academic:    25%
  Behavioral:  35%
  Skills:      40%

Interpretation: High employability - Strong placement likelihood
Similar Alumni: 3

Top Similar Alumni:
  1. Similarity: 0.95, Tier: Tier1, Score: 95.0
  2. Similarity: 0.92, Tier: Tier1, Score: 92.0
  3. Similarity: 0.88, Tier: Tier2, Score: 75.0

============================================================
✓ TEST PASSED
============================================================

3. Testing health check endpoint...
✓ Health check successful
  Status: healthy
  Qdrant Available: True
  Message: Prediction service is fully operational
```

---

## Common Issues and Solutions

### Issue 1: "Could not connect to backend server"

**Error:**
```
✗ ERROR: Could not connect to backend server
  Make sure the backend is running on http://localhost:8000
```

**Solution:**
- Make sure you started the backend server in Step 1
- Check if port 8000 is already in use
- Try accessing http://localhost:8000 in your browser

### Issue 2: "Student profile not found"

**Error:**
```
✗ Student profile not found
  This is expected if no student profile exists for this user
```

**Solution:**
This is expected for a new test user. The test user needs a student profile. You can either:

1. **Create a student profile manually** using the database
2. **Use an existing student** by modifying the test script
3. **Create a profile creation endpoint** (Task 20.1)

For now, this is expected behavior and not a critical issue.

### Issue 3: "Service unavailable (Qdrant not running?)"

**Error:**
```
✗ Service unavailable (Qdrant not running?)
  Response: {"detail":"Vector database unavailable. Please try again later."}
```

**Solution:**
- Make sure Qdrant is running on port 6333
- Check Qdrant logs for errors
- Verify Qdrant collections exist (students, alumni)

### Issue 4: "No similar alumni found"

**Error:**
```
Similar Alumni: 0
```

**Solution:**
- Make sure alumni data is imported into the database
- Make sure alumni vectors are generated and stored in Qdrant
- Run the alumni import script to populate data

---

## Manual Testing with curl

If you prefer to test manually with curl:

### 1. Register a User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"test123\",\"role\":\"student\"}"
```

### 2. Login to Get Token
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d "{\"email\":\"test@example.com\",\"password\":\"test123\"}"
```

Copy the `access_token` from the response.

### 3. Call Prediction Endpoint
```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d "{}"
```

### 4. Check Health
```bash
curl http://localhost:8000/api/predict/health
```

---

## Testing with Postman/Thunder Client

### Setup
1. Create a new request collection
2. Add environment variables:
   - `base_url`: http://localhost:8000
   - `token`: (will be set after login)

### Requests

#### 1. Register
- Method: POST
- URL: `{{base_url}}/api/auth/register`
- Body (JSON):
```json
{
  "email": "test@example.com",
  "password": "test123",
  "role": "student"
}
```

#### 2. Login
- Method: POST
- URL: `{{base_url}}/api/auth/login`
- Body (JSON):
```json
{
  "email": "test@example.com",
  "password": "test123"
}
```
- Save `access_token` to `{{token}}` variable

#### 3. Predict
- Method: POST
- URL: `{{base_url}}/api/predict`
- Headers:
  - `Authorization`: `Bearer {{token}}`
- Body (JSON):
```json
{}
```

#### 4. Health Check
- Method: GET
- URL: `{{base_url}}/api/predict/health`

---

## Verifying the Results

### Check if Results are Reasonable

1. **Trajectory Score (0-100)**
   - Should be between 0 and 100
   - Higher scores indicate better employability
   - Typical range: 40-90

2. **Component Scores**
   - Academic: Based on GPA, attendance, internal marks, backlogs
   - Behavioral: Based on study hours, practice, projects, grit, wellbeing
   - Skills: Based on proficiency, market demand, languages, soft skills

3. **Confidence (0-1)**
   - Higher confidence means more reliable prediction
   - Depends on: number of similar alumni, data completeness, consistency
   - Typical range: 0.5-0.9

4. **Margin of Error (0-20)**
   - Lower is better
   - Calculated as: (1 - confidence) × 20
   - Typical range: 2-10

5. **Predicted Tier**
   - Tier1: Score 71-100 (Top companies)
   - Tier2: Score 41-70 (Mid-tier companies)
   - Tier3: Score 0-40 (Entry-level or not placed)

6. **Similar Alumni**
   - Should have similarity scores > 0.7
   - Should be from the same or similar major
   - Should have relevant outcomes

---

## Next Steps After Testing

### If Tests Pass ✅
1. Mark Task 11 as complete
2. Proceed to Phase 3: LLM Integration
3. Start with Task 12: Ollama Client Infrastructure

### If Tests Fail ❌
1. Check the error messages
2. Review the logs for details
3. Fix any issues found
4. Re-run the tests
5. Ask for help if needed

---

## Performance Benchmarks

### Expected Performance
- Registration: <500ms
- Login: <300ms
- Prediction: <2000ms (target)
- Health check: <100ms

### Actual Performance (measure with test script)
- Will be displayed in test output
- Should be well under targets

---

## Summary

The prediction endpoint is ready for testing. Follow the steps above to:
1. Start the backend server
2. Verify Qdrant is running
3. Run the test script
4. Verify the results

If everything works, the core prediction engine is complete and ready for Phase 3 (LLM Integration)!
