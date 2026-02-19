@echo off
echo ========================================
echo Alembic Setup Script for Trajectory Engine
echo ========================================
echo.

echo Step 1: Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERROR: Failed to install dependencies
    pause
    exit /b 1
)
echo ✅ Dependencies installed successfully!
echo.

echo Step 2: Checking Alembic installation...
alembic --version
if %errorlevel% neq 0 (
    echo ERROR: Alembic not installed correctly
    pause
    exit /b 1
)
echo ✅ Alembic is installed!
echo.

echo Step 3: Generating initial migration...
echo This will detect all your models and create a migration file...
alembic revision --autogenerate -m "Initial schema with alumni and skills tables"
if %errorlevel% neq 0 (
    echo ERROR: Failed to generate migration
    pause
    exit /b 1
)
echo ✅ Migration file generated!
echo.

echo Step 4: Review the migration file
echo Please check the file in alembic\versions\ folder
echo Press any key when you're ready to apply the migration...
pause

echo Step 5: Applying migration to database...
alembic upgrade head
if %errorlevel% neq 0 (
    echo ERROR: Failed to apply migration
    pause
    exit /b 1
)
echo ✅ Migration applied successfully!
echo.

echo Step 6: Checking current migration version...
alembic current
echo.

echo ========================================
echo ✅ Alembic setup complete!
echo ========================================
echo.
echo Next steps:
echo 1. Test creating alumni records
echo 2. Test creating skill records
echo 3. Verify all tables in PostgreSQL
echo.
echo See ALEMBIC-SETUP-GUIDE.md for more details
echo.
pause
