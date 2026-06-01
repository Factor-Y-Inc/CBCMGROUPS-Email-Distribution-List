@echo off
REM Launcher script for CBCMGROUPS Migration Tool
REM Activates virtual environment and runs the application

echo Starting CBCMGROUPS Migration Tool...
echo.

REM Check if virtual environment exists
if not exist ".venv\Scripts\python.exe" (
    echo ERROR: Virtual environment not found!
    echo Please run: python -m venv .venv
    echo Then install dependencies: pip install -r requirements.txt
    pause
    exit /b 1
)

REM Run the application
.venv\Scripts\python.exe src\main.py

REM Pause if there was an error
if errorlevel 1 (
    echo.
    echo Application exited with an error.
    pause
)
