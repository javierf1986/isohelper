@echo off
echo ========================================
echo ISO Helper - Starting Development Servers
echo ========================================
echo.

REM Get the directory where the batch file is located
set PROJECT_DIR=%~dp0

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.13 or higher
    pause
    exit /b 1
)

REM Check if Node.js is available
node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    echo Please install Node.js 18 or higher
    pause
    exit /b 1
)

echo [1/2] Starting Backend Server (FastAPI on port 8000)...
echo.
start "ISO Helper Backend" cmd /k "cd /d %PROJECT_DIR%backend && python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

echo [2/2] Starting Frontend Server (Next.js on port 3000)...
echo.
start "ISO Helper Frontend" cmd /k "cd /d %PROJECT_DIR%frontend && npm run dev"

echo.
echo ========================================
echo ✅ Servers Starting!
echo ========================================
echo.
echo Backend:  http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to close this window...
echo (The servers will continue running in their own windows)
pause >nul
