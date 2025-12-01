@echo off
echo Starting Markdown Editor...
python markdown_editor.py
if %errorlevel% neq 0 (
    echo Error: Failed to run markdown_editor.py.
    pause
    exit /b %errorlevel%
)
pause