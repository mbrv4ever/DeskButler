@echo off
REM ============================================================
REM  DeskButler - start script (single-file versie)
REM ============================================================
REM  Dubbelklik om DeskButler te starten.
REM  Gebruikt pythonw.exe (zonder console-venster).
REM ============================================================

cd /d "%~dp0"

where pythonw >nul 2>nul
if errorlevel 1 (
    echo Python lijkt niet geinstalleerd te zijn.
    echo Installeer Python 3.10+ van https://www.python.org
    echo en zet "Add Python to PATH" aan tijdens de installatie.
    pause
    exit /b 1
)

if not exist ".installed" (
    echo Eerste keer opstarten - dependencies installeren...
    echo Dit kan een paar minuten duren.
    python -m pip install -r requirements.txt
    if errorlevel 1 (
        echo Installatie van dependencies is mislukt.
        echo Probeer handmatig: pip install -r requirements.txt
        pause
        exit /b 1
    )
    type nul > .installed
)

start "" pythonw deskbutler.py
exit /b 0
