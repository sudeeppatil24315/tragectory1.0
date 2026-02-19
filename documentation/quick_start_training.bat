@echo off
REM Trajectory Engine - Quick Start Training Script
REM This script automates the entire training pipeline

echo ============================================================
echo TRAJECTORY ENGINE - LLM TRAINING QUICK START
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)
echo [OK] Python is installed

REM Check if Ollama is installed
ollama --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Ollama is not installed!
    echo Please install Ollama from https://ollama.ai
    pause
    exit /b 1
)
echo [OK] Ollama is installed

REM Check if base model exists
echo.
echo Checking for base model...
ollama list | findstr "llama3.1:8b-instruct-q4_0" >nul
if errorlevel 1 (
    echo [WARNING] Base model not found!
    echo.
    set /p PULL="Do you want to pull llama3.1:8b-instruct-q4_0? (y/n): "
    if /i "%PULL%"=="y" (
        echo Pulling model... This may take 5-10 minutes...
        ollama pull llama3.1:8b-instruct-q4_0
        if errorlevel 1 (
            echo [ERROR] Failed to pull model
            pause
            exit /b 1
        )
    ) else (
        echo [ERROR] Base model required for training
        pause
        exit /b 1
    )
)
echo [OK] Base model available

REM Check if CSV file exists
if not exist "student data.csv" (
    echo [ERROR] student data.csv not found!
    echo Please ensure the CSV file is in the current directory
    pause
    exit /b 1
)
echo [OK] Student data CSV found

echo.
echo ============================================================
echo STEP 1: PREPARE TRAINING DATA
echo ============================================================
echo.
echo This will parse your CSV and generate training examples...
echo.
pause

python prepare_training_data.py
if errorlevel 1 (
    echo [ERROR] Failed to prepare training data
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Training data prepared!
echo.
echo Files created:
echo - training_data.jsonl (LLM training format)
echo - training_data_summary.md (Human-readable summary)
echo.
pause

echo.
echo ============================================================
echo STEP 2: TRAIN THE MODEL
echo ============================================================
echo.
echo Choose training option:
echo 1. Basic Model (fast, system prompt only)
echo 2. Enhanced Model (better accuracy, includes examples)
echo.
set /p OPTION="Enter option (1 or 2): "

if "%OPTION%"=="1" (
    echo.
    echo Creating basic model...
    echo.
    
    REM Create basic Modelfile
    python -c "from train_llm import create_modelfile; create_modelfile()"
    
    REM Create model
    ollama create trajectory-engine:latest -f Modelfile
    if errorlevel 1 (
        echo [ERROR] Failed to create model
        pause
        exit /b 1
    )
    
    echo.
    echo [SUCCESS] Basic model created: trajectory-engine:latest
    
) else if "%OPTION%"=="2" (
    echo.
    echo Creating enhanced model with training examples...
    echo This may take 2-3 minutes...
    echo.
    
    REM Create enhanced model
    python -c "from train_llm import train_with_examples; train_with_examples()"
    if errorlevel 1 (
        echo [ERROR] Failed to create enhanced model
        pause
        exit /b 1
    )
    
    echo.
    echo [SUCCESS] Enhanced model created: trajectory-engine:latest-enhanced
    
) else (
    echo [ERROR] Invalid option
    pause
    exit /b 1
)

echo.
echo ============================================================
echo STEP 3: TEST THE MODEL
echo ============================================================
echo.
echo Running integration test with sample student...
echo.
pause

python integration_example.py
if errorlevel 1 (
    echo [WARNING] Test completed with errors
) else (
    echo [SUCCESS] Test completed successfully!
)

echo.
echo ============================================================
echo TRAINING COMPLETE!
echo ============================================================
echo.
echo Your model is ready to use!
echo.
echo Next steps:
echo 1. Test interactively: ollama run trajectory-engine:latest
echo 2. Integrate in your app: See integration_example.py
echo 3. Read the guide: llm-training-guide.md
echo.
echo Model location: trajectory-engine:latest
echo Training data: training_data.jsonl
echo Summary: training_data_summary.md
echo.
pause
