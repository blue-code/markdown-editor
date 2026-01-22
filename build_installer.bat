@echo off
rem Nebula Note Windows Installer Build Script
setlocal
pushd "%~dp0"

echo.
echo ======================================================
echo Nebula Note Installer Build System
echo ======================================================
echo.

:: 1. Build the executable first
echo [1/2] Building executable...
set "SKIP_INSTALLER=1"
set "NO_PAUSE=1"
call build_exe.bat
set "SKIP_INSTALLER="
set "NO_PAUSE="

if %errorlevel% neq 0 (
    echo.
    echo Error: Executable build failed. Installer build aborted.
    popd
    exit /b 1
)

:: 2. Build the installer
echo.
echo [2/2] Building Setup Installer with NSIS...

:: NSIS path detection logic
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
echo Error: NSIS (makensis.exe) not found.
echo Please install NSIS from: https://nsis.sourceforge.io/Download
goto :error

:run_nsis
"%MAKENSIS_CMD%" installer.nsi
if %errorlevel% neq 0 (
    echo Error: NSIS build failed.
    goto :error
)

if exist "dist\NebulaNote-Setup.exe" (
    echo.
    echo ======================================================
    echo [*] Installer Build Success!
    echo Location: dist\NebulaNote-Setup.exe
    echo ======================================================
) else (
    echo Error: dist\NebulaNote-Setup.exe not found after build.
    goto :error
)

popd
echo.
echo Done.
pause
exit /b 0

:error
echo.
echo ======================================================
echo Installer Build Failed.
echo ======================================================
popd
pause
exit /b 1
