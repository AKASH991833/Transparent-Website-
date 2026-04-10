@echo off
title Ansh Air Cool - Backend Server
echo ========================================
echo   Starting Ansh Air Cool Backend
echo ========================================
echo.

cd /d "%~dp0"

REM Check if .env exists
if not exist ".env" (
    echo [ERROR] .env file not found!
    echo Please setup the environment first.
    pause
    exit /b 1
)

REM Check dependencies
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] Dependencies not found!
    echo Running setup...
    call setup.bat
)

echo.
echo Starting Flask application...
echo.
echo Server will be available at:
echo   Website: http://localhost:5000
echo   Admin:   http://localhost:5000/admin
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
