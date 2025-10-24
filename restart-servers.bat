@echo off
echo ========================================
echo ISO Helper - Restarting Development Servers
echo ========================================
echo.

set PROJECT_DIR=%~dp0

echo [1/3] Stopping existing servers...
call "%PROJECT_DIR%stop-servers.bat"

echo.
echo [2/3] Waiting 2 seconds...
timeout /t 2 /nobreak >nul

echo.
echo [3/3] Starting servers...
call "%PROJECT_DIR%start-servers.bat"
