@echo off
REM  DeskButler - bouw een .exe (onedir, PyInstaller) - Dravenlock
setlocal
cd /d "%~dp0"
set "PYEXE="
for %%V in (3.12 3.13 3.11 3.10) do (
  if not defined PYEXE ( py -%%V -c "import sys" >nul 2>&1 && set "PYEXE=py -%%V" )
)
if not defined PYEXE ( echo Geen Python 3.10-3.13 gevonden. & pause & exit /b 1 )
set "BV=.build-venv"
if not exist "%BV%\Scripts\python.exe" ( %PYEXE% -m venv "%BV%" )
if not exist "%BV%\Scripts\python.exe" ( echo Bouw-omgeving mislukt. & pause & exit /b 1 )
set "VPY=%BV%\Scripts\python.exe"
"%VPY%" -m pip install --upgrade pip >nul 2>&1
"%VPY%" -m pip install --only-binary=:all: -r requirements.txt pyinstaller
if errorlevel 1 ( echo Installeren mislukt. & pause & exit /b 1 )
echo Bouwen...
"%VPY%" -m PyInstaller --noconfirm --clean --windowed --onedir --name DeskButler --icon app_icon.ico --collect-all PySide6 --collect-submodules feedparser deskbutler.py
if errorlevel 1 ( echo Bouwen mislukt. & pause & exit /b 1 )
if not exist "dist\DeskButler\DeskButler.exe" ( echo Geen exe gevonden. & pause & exit /b 1 )
echo.
echo KLAAR: dist\DeskButler\DeskButler.exe  (houd de map _internal erbij)
pause
