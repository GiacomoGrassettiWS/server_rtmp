@echo off
title Creazione EXE - RTMP Server
echo.
echo ========================================
echo  Build EXE - RTMP Server per OBS
echo ========================================
echo.

REM Verifica ambiente
if not exist ".venv" (
    echo Creazione ambiente virtuale...
    python -m venv .venv
)

echo Attivazione ambiente virtuale...
call .venv\Scripts\activate.bat

echo Installazione dipendenze...
pip install -q -r requirements.txt

echo.
echo Pulizia build precedenti...
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

echo.
echo ========================================
echo  Creazione EXE con PyInstaller
echo ========================================
echo.

python -m PyInstaller --clean rtmp_server.spec

if errorlevel 1 (
    echo.
    echo ERRORE: Build fallito!
    pause
    exit /b 1
)

echo.
echo ========================================
echo  Build completato con successo!
echo ========================================
echo.
echo Eseguibile creato in: dist\RTMPServer.exe
echo.
echo Per testare: cd dist e esegui RTMPServer.exe
echo.
pause
