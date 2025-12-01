@echo off
cd /d "%~dp0"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Error: Failed to create virtual environment. Make sure Python is installed and in your PATH.
        pause
        exit /b %errorlevel%
    )
)

echo Installing Python dependencies...
venv\Scripts\python.exe -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies.
    pause
    exit /b %errorlevel%
)

echo Setup complete. dependencies installed in 'venv'.
pause