@echo off
echo ============================================================
echo Creating PostgreSQL Database for Trajectory Engine
echo ============================================================
echo.

REM Try to find PostgreSQL installation
set PGPATH=C:\Program Files\PostgreSQL\15\bin
if not exist "%PGPATH%\psql.exe" set PGPATH=C:\Program Files\PostgreSQL\16\bin
if not exist "%PGPATH%\psql.exe" set PGPATH=C:\Program Files\PostgreSQL\14\bin

if not exist "%PGPATH%\psql.exe" (
    echo ERROR: Could not find PostgreSQL installation
    echo Please create the database manually using pgAdmin 4:
    echo   1. Open pgAdmin 4
    echo   2. Right-click on "Databases"
    echo   3. Select "Create" -^> "Database..."
    echo   4. Database name: trajectory
    echo   5. Click "Save"
    echo.
    pause
    exit /b 1
)

echo Found PostgreSQL at: %PGPATH%
echo.
echo Creating database 'trajectory'...
echo Enter your PostgreSQL password when prompted (default: 8088)
echo.

"%PGPATH%\psql.exe" -U postgres -c "CREATE DATABASE trajectory;"

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo SUCCESS! Database 'trajectory' created successfully!
    echo ============================================================
    echo.
    echo Next step: Run migrations
    echo   alembic upgrade head
    echo.
) else (
    echo.
    echo ============================================================
    echo Database creation failed or database already exists
    echo ============================================================
    echo.
    echo If database already exists, that's OK! Continue with:
    echo   alembic upgrade head
    echo.
)

pause
