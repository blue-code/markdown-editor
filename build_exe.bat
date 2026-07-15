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

:: 1-a. 잔존 프로세스 종료 — DLL 점유 해제 (이게 없으면 PermissionError 로 빌드 실패)
::      Nebula Note 본체 + PyQt6 WebEngine 헬퍼 프로세스
taskkill /F /IM "Nebula Note.exe" /T >nul 2>&1
taskkill /F /IM "QtWebEngineProcess.exe" /T >nul 2>&1

:: 1-b. 디렉터리 삭제 — 점유 해제 직후엔 핸들이 잠깐 남을 수 있어 짧게 재시도
call :try_rmdir build
call :try_rmdir dist
if exist dist (
    echo Error: 'dist' 폴더를 삭제할 수 없습니다. 다른 프로그램이 점유 중일 수 있습니다.
    echo        - 작업 관리자에서 "Nebula Note", "QtWebEngineProcess" 강제 종료 후 재시도
    echo        - 그래도 안 되면 윈도우 재부팅 후 재시도
    goto :error
)
goto :after_clean

:try_rmdir
if not exist "%~1" exit /b 0
rmdir /s /q "%~1" 2>nul
if not exist "%~1" exit /b 0
:: 1차 실패 — 잠깐 대기 후 재시도
ping -n 3 127.0.0.1 >nul
rmdir /s /q "%~1" 2>nul
exit /b 0

:after_clean

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
:: 미사용 Qt 모듈 제외 — 실제 사용 모듈은 Widgets/Core/Gui/WebEngine(Widgets,Core)/WebChannel/PrintSupport 뿐.
:: 3D·Quick3D·Multimedia·Charts·Sensors 등 마크다운 에디터와 무관한 모듈을 번들에서 배제해 용량을 줄인다.
python -m PyInstaller --noconfirm --windowed ^
    --name "Nebula Note" ^
    --icon "icon.ico" ^
    --add-data "icon.ico;." ^
    --add-data "assets;assets" ^
    --exclude-module PyQt6.QtMultimedia ^
    --exclude-module PyQt6.QtMultimediaWidgets ^
    --exclude-module PyQt6.QtBluetooth ^
    --exclude-module PyQt6.QtNfc ^
    --exclude-module PyQt6.QtPositioning ^
    --exclude-module PyQt6.QtLocation ^
    --exclude-module PyQt6.QtSensors ^
    --exclude-module PyQt6.QtSerialPort ^
    --exclude-module PyQt6.QtRemoteObjects ^
    --exclude-module PyQt6.QtSql ^
    --exclude-module PyQt6.QtTest ^
    --exclude-module PyQt6.QtHelp ^
    --exclude-module PyQt6.QtDesigner ^
    --exclude-module PyQt6.QtCharts ^
    --exclude-module PyQt6.QtDataVisualization ^
    --exclude-module PyQt6.QtQuick ^
    --exclude-module PyQt6.QtQuick3D ^
    --exclude-module PyQt6.QtQuickWidgets ^
    --exclude-module PyQt6.QtQml ^
    markdown_editor.py

if %errorlevel% neq 0 (
    echo Error: PyInstaller build failed.
    goto :error
)

:: 5. Check Output and Optional Installer Build
if not exist "dist\Nebula Note\Nebula Note.exe" (
    echo Error: Output executable not found.
    goto :error
)

echo.
echo ======================================================
echo [*] Executable Build Success!
echo Location: dist\Nebula Note\Nebula Note.exe
echo ======================================================

:: 빌드 경량화 — 디버그 리소스/불필요 로케일/qml 제거 (NSIS 패키징 전에 수행)
echo [*] Pruning build (debug resources, locales, qml)...
powershell -NoProfile -ExecutionPolicy Bypass -File "prune_build.ps1"

if defined SKIP_INSTALLER (
    echo [Notice] Skipping installer build as requested.
    goto :build_done
)

:: NSIS Detection
set "MAKENSIS_CMD=makensis.exe"
where /q makensis.exe
if %errorlevel% equ 0 goto :run_nsis

if exist "C:\Program Files (x86)\NSIS\makensis.exe" (
    set "MAKENSIS_CMD=C:\Program Files (x86)\NSIS\makensis.exe"
    goto :run_nsis
)

if exist "C:\Program Files\NSIS\makensis.exe" (
    set "MAKENSIS_CMD=C:\Program Files\NSIS\makensis.exe"
    goto :run_nsis
)

:: NSIS Not Found
echo.
echo [Notice] 'NebulaNote-Setup.exe' requires NSIS.
echo If you already installed NSIS, please restart your terminal
echo or make sure it's installed at 'C:\Program Files (x86)\NSIS'.
echo https://nsis.sourceforge.io/Download
goto :build_done

:run_nsis
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

:build_done
popd
echo.
echo Done.
if not defined NO_PAUSE pause
exit /b 0

:error
echo.
echo ======================================================
echo Build Failed. Please check the logs above.
echo ======================================================
popd
if not defined NO_PAUSE pause
exit /b 1
