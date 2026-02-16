@echo off
title Server RTMP per OBS
echo.
echo ========================================
echo  Server RTMP per OBS - Avvio
echo ========================================
echo.

REM Verifica Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERRORE: Python non trovato!
    echo.
    echo Installa Python da: https://www.python.org/downloads/
    echo Assicurati di selezionare "Add Python to PATH" durante l'installazione
    pause
    exit /b 1
)

REM Installa dipendenze se necessario
if not exist "requirements.txt" (
    echo ERRORE: requirements.txt non trovato!
    pause
    exit /b 1
)

echo Verifica dipendenze...
pip install -q -r requirements.txt

echo.
echo Avvio del server RTMP...
echo.

python rtmp_server_gui.py

if errorlevel 1 (
    echo.
    echo ERRORE: Il programma si è chiuso in modo inaspettato
    pause
)
