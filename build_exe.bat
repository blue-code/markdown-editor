@echo off
rem Nebula Note Windows Build Script
setlocal
pushd "%~dp0"

echo.
echo ======================================================
echo Nebula Note Windows Build System
echo ======================================================
echo.

:: 1. Clean previous builds
echo [1/5] Cleaning previous builds...
if exist build rmdir /s /q build
if exist dist rmdir /s /q dist

:: 2. Setup Virtual Environment
if not exist venv (
    echo [2/5] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo Error: Failed to create virtual environment.
        goto :error
    )
)
call venv\Scripts\activate

:: 3. Install Dependencies
echo [3/5] Installing dependencies...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install pyinstaller
if %errorlevel% neq 0 (
    echo Error: Failed to install dependencies.
    goto :error
)

:: 4. Build Executable
echo [4/5] Building Executable with PyInstaller...
python -m PyInstaller --noconfirm --windowed ^
    --name "Nebula Note" ^
    --icon "icon.ico" ^
    --splash "splash.png" ^
    --add-data "icon.ico;." ^
    markdown_editor.py

if %errorlevel% neq 0 (
    echo Error: PyInstaller build failed.
    goto :error
)

:: 5. Check Output and Optional Installer Build
if exist "dist\Nebula Note\Nebula Note.exe" (
    echo.
    echo ======================================================
    echo [*] Executable Build Success!
    echo Location: dist\Nebula Note\Nebula Note.exe
    echo ======================================================
    
    :: Check for NSIS to build the Setup installer
    set "MAKENSIS_CMD=makensis.exe"
    where /q makensis.exe
    if %errorlevel% neq 0 (
        if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
            set "MAKENSIS_CMD=C:\Program Files (x86)\NSIS\makensis.exe"
        ) else if exist "C:\Program Files\NSIS\makensis.exe" (
            set "MAKENSIS_CMD=C:\Program Files\NSIS\makensis.exe"
        ) else (
            set "MAKENSIS_CMD="
        )
    )

    if defined MAKENSIS_CMD (
        echo.
        echo [5/5] NSIS detected! Building Setup Installer...
        "%MAKENSIS_CMD%" installer.nsi
        if exist "dist\NebulaNote-Setup.exe" (
            echo.
            echo ======================================================
            echo [*] Setup Installer Build Success!
            echo Location: dist\NebulaNote-Setup.exe
            echo ======================================================
        ) else (
            echo Error: Installer build failed. Check installer.nsi logs.
        )
    ) else (
        echo.
        echo [Notice] 'NebulaNote-Setup.exe' (Installer) requires NSIS.
        echo If you already installed NSIS, please restart your terminal
        echo or make sure it's installed at 'C:\Program Files (x86)\NSIS'.
        echo https://nsis.sourceforge.io/Download
    )
    
    popd
    echo.
    echo Done.
    pause
    exit /b 0
) else (
    echo Error: Output executable not found.
    goto :error
)

:error
echo.
echo ======================================================
echo Build Failed. Please check the logs above.
echo ======================================================
popd
pause
exit /b 1
