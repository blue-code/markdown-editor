@echo off
rem Nebula Note Windows installer build script (NSIS)

setlocal
pushd "%~dp0"

call build_exe.bat
if errorlevel 1 (
    popd
    exit /b 1
)

where /q makensis.exe
if errorlevel 1 (
    echo.
    echo NSIS not found. Install NSIS and add makensis.exe to PATH.
    echo https://nsis.sourceforge.io/Download
    popd
    exit /b 1
)

makensis installer.nsi
if errorlevel 1 (
    popd
    exit /b 1
)

if exist "dist\NebulaNote-Setup.exe" (
    echo.
    echo Installer build complete: dist\NebulaNote-Setup.exe
) else (
    echo.
    echo Installer build failed: dist\NebulaNote-Setup.exe not found.
    popd
    exit /b 1
)

popd
