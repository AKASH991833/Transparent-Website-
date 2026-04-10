@echo off
echo ========================================
echo   Ansh Air Cool - Backend Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed!
    echo Please install Python 3.8+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Python found!
echo.

REM Check if MySQL is installed
mysql --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARNING] MySQL command not found!
    echo Please ensure MySQL Server is installed and running.
    echo.
    pause
)

echo [2/4] Installing Python dependencies...
cd /d "%~dp0"
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo [ERROR] Failed to install dependencies!
    pause
    exit /b 1
)

echo.
echo [3/4] Dependencies installed successfully!
echo.

REM Check if .env exists
if not exist ".env" (
    echo [WARNING] .env file not found!
    echo Please create .env file with your database credentials.
    echo.
) else (
    echo [4/4] Configuration file found!
)

echo.
echo ========================================
echo   Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Ensure MySQL is running
echo 2. Review .env file with your credentials
echo 3. Run: python app.py
echo 4. Visit: http://localhost:5000/admin
echo.
echo Default Login:
echo   Username: admin
echo   Password: admin123
echo.
pause
