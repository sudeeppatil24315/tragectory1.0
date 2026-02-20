@echo off
REM Setup script for Qdrant Vector Database
REM This script helps install and run Qdrant locally using Docker

echo ========================================
echo Qdrant Vector Database Setup
echo ========================================
echo.

REM Check if Docker is installed
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed!
    echo.
    echo Please install Docker Desktop from:
    echo https://www.docker.com/products/docker-desktop
    echo.
    pause
    exit /b 1
)

echo Docker is installed. Proceeding with Qdrant setup...
echo.

REM Pull Qdrant Docker image
echo Pulling Qdrant Docker image...
docker pull qdrant/qdrant

REM Create Qdrant data directory
if not exist "qdrant_storage" mkdir qdrant_storage

REM Run Qdrant container
echo.
echo Starting Qdrant container...
docker run -d ^
    --name qdrant ^
    -p 6333:6333 ^
    -p 6334:6334 ^
    -v "%cd%\qdrant_storage:/qdrant/storage" ^
    qdrant/qdrant

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo Qdrant is now running!
    echo ========================================
    echo.
    echo Web UI: http://localhost:6333/dashboard
    echo API: http://localhost:6333
    echo gRPC: localhost:6334
    echo.
    echo Data is stored in: %cd%\qdrant_storage
    echo.
    echo To stop Qdrant: docker stop qdrant
    echo To start Qdrant: docker start qdrant
    echo To remove Qdrant: docker rm -f qdrant
    echo.
) else (
    echo.
    echo ERROR: Failed to start Qdrant container!
    echo.
    echo If container already exists, try:
    echo   docker start qdrant
    echo.
    echo Or remove and recreate:
    echo   docker rm -f qdrant
    echo   Then run this script again.
    echo.
)

pause
