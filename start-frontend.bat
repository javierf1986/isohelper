@echo off
echo ========================================
echo ISO Helper - Starting Frontend Server Only
echo ========================================
echo.

set PROJECT_DIR=%~dp0

node --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Node.js is not installed or not in PATH
    pause
    exit /b 1
)

echo Starting Frontend Server (Next.js on port 3000)...
echo.
cd /d %PROJECT_DIR%frontend
npm run dev

pause
