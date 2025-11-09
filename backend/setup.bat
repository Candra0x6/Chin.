@echo off
REM Setup script for Chin  Backend (Windows)

echo 🏥 Chin  - Setup Script
echo ================================
echo.

REM Check Python version
echo 📌 Checking Python version...
python --version
if %errorlevel% neq 0 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    exit /b 1
)

echo.
echo 📦 Creating virtual environment...
python -m venv venv

if %errorlevel% neq 0 (
    echo ❌ Failed to create virtual environment.
    exit /b 1
)

echo ✅ Virtual environment created
echo.

REM Activate virtual environment
echo 📌 Activating virtual environment...
call venv\Scripts\activate.bat

if %errorlevel% neq 0 (
    echo ❌ Failed to activate virtual environment.
    exit /b 1
)

echo ✅ Virtual environment activated
echo.

REM Install dependencies
echo 📦 Installing dependencies...
python -m pip install --upgrade pip
pip install -r requirements.txt

if %errorlevel% neq 0 (
    echo ❌ Failed to install dependencies.
    exit /b 1
)

echo ✅ Dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist .env (
    echo 📝 Creating .env file from template...
    copy .env.example .env
    echo ⚠️  Please edit .env and add your GEMINI_API_KEY
) else (
    echo ✅ .env file already exists
)

echo.
echo 🎉 Setup complete!
echo.
echo Next steps:
echo 1. Activate virtual environment: venv\Scripts\activate
echo 2. Edit .env file and add your Gemini API key
echo 3. Run the application: python -m app.main
echo.
echo 📚 Documentation: http://localhost:8000/docs
echo.
pause
