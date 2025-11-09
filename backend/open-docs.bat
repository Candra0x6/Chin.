@echo off
REM Open Developer Documentation (Windows)
REM This script opens the Chin  developer documentation in your default browser

echo.
echo =========================================
echo   Chin  - Developer Documentation
echo =========================================
echo.

REM Check if docs/index.html exists
if not exist "docs\index.html" (
    echo [91mError: docs\index.html not found![0m
    echo Please ensure you're running this script from the project root directory.
    pause
    exit /b 1
)

REM Get the absolute path
set "DOCS_PATH=%CD%\docs\index.html"

echo Opening documentation: %DOCS_PATH%
echo.

REM Open in default browser
start "" "%DOCS_PATH%"

echo [92mDocumentation opened in default browser[0m
echo.
echo ========================================
echo   Interactive Test Runner
echo ========================================
echo.
echo To use the Interactive Test Runner:
echo   1. Ensure backend server is running:
echo      uvicorn app.main:app --reload
echo.
echo   2. Navigate to the Integration Tests tab
echo.
echo   3. Click 'Run All Tests' button
echo.
echo For more information, see: docs\README.md
echo.

pause
