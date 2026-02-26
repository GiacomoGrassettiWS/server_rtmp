@echo off
title Build EXE - RTMP Streaming Server
echo.
echo ========================================
echo  RTMP Streaming Server - Build EXE
echo ========================================
echo.

echo Installing dependencies...
pip install -q -r requirements.txt

echo.
echo Cleaning previous builds...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo.
echo ========================================
echo  Building EXE with PyInstaller...
echo ========================================
echo.

python -m PyInstaller --clean rtmp_server.spec

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Build completed successfully!
echo ========================================
echo.
echo Executable created at: dist\RTMPServer.exe
echo.
echo NOTE: Copy the mediamtx/ folder next to RTMPServer.exe
echo       before running the application.
echo.
pause
