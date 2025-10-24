@echo off
echo ========================================
echo ISO Helper - Starting Backend Server Only
echo ========================================
echo.

set PROJECT_DIR=%~dp0

python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo Starting Backend Server (FastAPI on port 8000)...
echo.
cd /d %PROJECT_DIR%backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

pause
