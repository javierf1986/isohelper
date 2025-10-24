@echo off
echo ========================================
echo ISO Helper - Stopping Development Servers
echo ========================================
echo.

echo Stopping Backend Server (port 8000)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":8000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Backend server stopped
    )
)

echo Stopping Frontend Server (port 3000)...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":3000" ^| find "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    if not errorlevel 1 (
        echo ✅ Frontend server stopped
    )
)

echo.
echo ========================================
echo ✅ All servers stopped
echo ========================================
echo.
pause
