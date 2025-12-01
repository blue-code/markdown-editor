@echo off
cd /d "%~dp0"

if not exist "venv" (
    echo Virtual environment not found. Running setup...
    call setup.bat
)

echo Starting Markdown Editor...
venv\Scripts\python.exe markdown_editor.py
if %errorlevel% neq 0 (
    echo Error: Failed to run markdown_editor.py.
    pause
    exit /b %errorlevel%
)
pause