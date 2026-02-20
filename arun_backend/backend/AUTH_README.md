# Authentication System Documentation

## Overview

The Trajectory Engine MVP uses JWT (JSON Web Token) based authentication with bcrypt password hashing.

## Features

✅ User registration with email validation  
✅ Secure password hashing with bcrypt  
✅ JWT token generation (1-hour expiration)  
✅ Role-based access control (student vs admin)  
✅ Protected route middleware  
✅ Token refresh capability  

---

## Installation

Install required packages:

```bash
pip install python-jose[cryptography] passlib[bcrypt] python-multipart
```

Or install from requirements.txt:

```bash
pip install -r requirements.txt
```

---

## API Endpoints

### 1. Register New User

**Endpoint:** `POST /api/auth/register`

**Request Body:**
```json
{
  "email": "student@example.com",
  "password": "securepassword123",
  "role": "student"
}
```

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "student@example.com",
    "role": "student"
  }
}
```

**Errors:**
- `400 Bad Request` - Email already registered or invalid role
- `422 Unprocessable Entity` - Invalid email format

---

### 2. Login

**Endpoint:** `POST /api/auth/login`

**Request Body (Form Data):**
```
username=student@example.com
password=securepassword123
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "email": "student@example.com",
    "role": "student"
  }
}
```

**Errors:**
- `401 Unauthorized` - Incorrect email or password

---

### 3. Get Current User

**Endpoint:** `GET /api/auth/me`

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "email": "student@example.com",
  "role": "student"
}
```

**Errors:**
- `401 Unauthorized` - Invalid or expired token

---

## Using Authentication in Code

### Protect a Route (Any Authenticated User)

```python
from fastapi import APIRouter, Depends
from app.auth import get_current_user
from app.models import User

router = APIRouter()

@router.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello {current_user.email}!"}
```

### Protect a Route (Specific Role Required)

```python
from fastapi import APIRouter, Depends
from app.auth import require_role
from app.models import User

router = APIRouter()

@router.get("/admin-only")
async def admin_route(current_user: User = Depends(require_role("admin"))):
    return {"message": "Admin access granted"}
```

---

## Testing

### Manual Testing with cURL

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","role":"student"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=test@example.com&password=test123"
```

**Get Current User:**
```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <your_token_here>"
```

### Automated Testing

Run the test script:

```bash
# Start the server first
python -m uvicorn app.main:app --reload

# In another terminal, run tests
python test_auth.py
```

---

## Security Configuration

### Change Secret Key (IMPORTANT!)

Edit `app/auth.py`:

```python
SECRET_KEY = "your-secret-key-here-change-in-production"
```

**For production, use a strong random key:**

```python
import secrets
print(secrets.token_urlsafe(32))
```

Add to `.env` file:
```
SECRET_KEY=your-generated-secret-key
```

Update `app/auth.py`:
```python
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
```

### Token Expiration

Default: 1 hour (60 minutes)

To change, edit `app/auth.py`:
```python
ACCESS_TOKEN_EXPIRE_MINUTES = 120  # 2 hours
```

---

## Password Requirements

Current implementation accepts any password. For production, add validation:

```python
from pydantic import BaseModel, validator

class UserRegister(BaseModel):
    email: EmailStr
    password: str
    role: str = "student"
    
    @validator('password')
    def password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not any(char.isdigit() for char in v):
            raise ValueError('Password must contain at least one digit')
        if not any(char.isupper() for char in v):
            raise ValueError('Password must contain at least one uppercase letter')
        return v
```

---

## Common Issues

### Issue 1: "Could not validate credentials"

**Cause:** Invalid or expired token

**Solution:** Login again to get a new token

### Issue 2: "Email already registered"

**Cause:** User with that email already exists

**Solution:** Use a different email or login with existing credentials

### Issue 3: "Access denied. Required role: admin"

**Cause:** User doesn't have required role

**Solution:** Register with correct role or use appropriate endpoint

---

## Next Steps

1. ✅ Install authentication packages
2. ✅ Test registration endpoint
3. ✅ Test login endpoint
4. ✅ Test protected routes
5. ⏳ Add frontend login/register pages (Task 3.3)
6. ⏳ Move SECRET_KEY to .env file
7. ⏳ Add password strength validation
8. ⏳ Add email verification (optional)

---

## Architecture

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ 1. POST /api/auth/register
       │    {email, password, role}
       ▼
┌─────────────────┐
│  Auth Router    │
│  (routes/auth)  │
└────────┬────────┘
         │ 2. hash_password()
         ▼
┌─────────────────┐
│   Auth Utils    │
│   (app/auth)    │
└────────┬────────┘
         │ 3. Store in DB
         ▼
┌─────────────────┐
│   PostgreSQL    │
│  (users table)  │
└────────┬────────┘
         │ 4. create_access_token()
         ▼
┌─────────────────┐
│   JWT Token     │
│  (1 hour exp)   │
└────────┬────────┘
         │ 5. Return to client
         ▼
┌─────────────┐
│   Client    │
│ Stores token│
└─────────────┘
```

---

**Documentation Version:** 1.0  
**Last Updated:** February 19, 2026
