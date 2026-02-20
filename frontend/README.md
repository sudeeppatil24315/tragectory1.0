# Trajectory Engine Frontend

React + TypeScript frontend for the Trajectory Engine MVP.

## Features Implemented

✅ **Task 3.3 Complete:**
- Login page with email/password form
- Registration page with validation
- Authentication context (React Context API)
- Protected route wrapper component
- Token storage in localStorage
- Error handling and user feedback
- Responsive design

## Tech Stack

- React 18
- TypeScript
- Vite (build tool)
- React Router v6 (routing)
- Axios (HTTP client)

## Setup Instructions

### 1. Install Dependencies

```bash
cd frontend
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

The frontend will run on http://localhost:3000

### 3. Backend Connection

The frontend is configured to proxy API requests to the backend at http://localhost:8000

Make sure the FastAPI backend is running:
```bash
cd arun_backend/backend
python -m uvicorn app.main:app --reload
```

## Project Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── ProtectedRoute.tsx    # Route guard for authenticated pages
│   ├── contexts/
│   │   └── AuthContext.tsx       # Authentication state management
│   ├── pages/
│   │   ├── Login.tsx             # Login page
│   │   ├── Register.tsx          # Registration page
│   │   ├── Dashboard.tsx         # Protected dashboard
│   │   ├── Auth.css              # Auth pages styling
│   │   └── Dashboard.css         # Dashboard styling
│   ├── App.tsx                   # Main app component with routing
│   ├── main.tsx                  # Entry point
│   └── index.css                 # Global styles
├── index.html
├── package.json
├── tsconfig.json
└── vite.config.ts
```

## Available Routes

- `/` - Redirects to login
- `/login` - Login page
- `/register` - Registration page
- `/dashboard` - Protected dashboard (requires authentication)

## Authentication Flow

1. **Registration:**
   - User fills registration form (email, password, role)
   - Frontend sends POST to `/api/auth/register`
   - Backend returns JWT token
   - Token stored in localStorage
   - User redirected to dashboard

2. **Login:**
   - User fills login form (email, password)
   - Frontend sends POST to `/api/auth/login`
   - Backend returns JWT token
   - Token stored in localStorage
   - User redirected to dashboard

3. **Protected Routes:**
   - ProtectedRoute component checks authentication
   - If not authenticated, redirects to login
   - If authenticated, renders protected content

4. **Logout:**
   - Clears token from localStorage
   - Clears user state
   - Redirects to login

## Testing the Frontend

### Prerequisites
- Backend server running on http://localhost:8000
- PostgreSQL database accessible (see `LOCAL-POSTGRES-SETUP.md`)

### Test Flow

1. **Start Frontend:**
   ```bash
   npm run dev
   ```

2. **Open Browser:**
   Navigate to http://localhost:3000

3. **Test Registration:**
   - Click "Register here"
   - Fill form: email, password, confirm password, role
   - Click "Register"
   - Should redirect to dashboard

4. **Test Login:**
   - Logout from dashboard
   - Enter credentials
   - Click "Login"
   - Should redirect to dashboard

5. **Test Protected Routes:**
   - Try accessing http://localhost:3000/dashboard without login
   - Should redirect to login page

## Next Steps

After Task 3.3 is complete, the next tasks will add:
- Task 4: Checkpoint - Ensure authentication and database setup complete
- Task 5+: Core prediction engine, dashboard features, etc.

## Build for Production

```bash
npm run build
```

The production build will be in the `dist/` directory.

## Troubleshooting

### CORS Errors
Make sure the FastAPI backend has CORS middleware configured:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### API Connection Issues
Check that:
1. Backend is running on port 8000
2. Vite proxy is configured correctly in `vite.config.ts`
3. Database is accessible

### Token Issues
If authentication isn't working:
1. Clear localStorage: `localStorage.clear()`
2. Check browser console for errors
3. Verify backend JWT configuration
