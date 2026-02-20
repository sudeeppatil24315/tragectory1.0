@echo off
REM Cloudflare Tunnel Startup Script
REM This script starts a Cloudflare Tunnel to expose your backend

echo ========================================
echo   Cloudflare Tunnel for Trajectory Engine
echo ========================================
echo.

REM Check if cloudflared is installed
where cloudflared >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: cloudflared is not installed!
    echo.
    echo Please install it first:
    echo   winget install --id Cloudflare.cloudflared
    echo.
    echo Or download from:
    echo   https://developers.cloudflare.com/cloudflare-one/connections/connect-apps/install-and-setup/installation/
    echo.
    pause
    exit /b 1
)

echo Cloudflared is installed ✓
echo.

REM Check if backend is running
echo Checking if backend is running on port 8000...
netstat -an | find ":8000" | find "LISTENING" >nul
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Backend doesn't appear to be running on port 8000
    echo Please start your backend first:
    echo   cd arun_backend/backend
    echo   python -m uvicorn app.main:app --reload --port 8000
    echo.
    echo Press any key to continue anyway, or Ctrl+C to cancel...
    pause >nul
)

echo.
echo Starting Cloudflare Tunnel...
echo.
echo IMPORTANT: Copy the tunnel URL from the output below!
echo You'll need to update frontend/.env.local with this URL.
echo.
echo ========================================
echo.

REM Start the tunnel
cloudflared tunnel --url http://localhost:8000

echo.
echo Tunnel stopped.
pause
