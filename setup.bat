@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"

where py >nul 2>nul
if not errorlevel 1 set "PYTHON=py"
if defined PYTHON goto :python_found

where python >nul 2>nul
if not errorlevel 1 set "PYTHON=python"
if defined PYTHON goto :python_found

echo [ERROR] Python was not found.
echo Install Python 3.11 or newer from https://www.python.org/downloads/
echo Select "Add python.exe to PATH" during installation.
pause
exit /b 1

:python_found

echo [1/3] Creating the virtual environment...
%PYTHON% -m venv .venv
if errorlevel 1 goto :error

echo [2/3] Updating pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error

echo [3/3] Installing the StudyForge website and CLI...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo.
echo Setup complete. Double-click run.bat to start StudyForge.
pause
exit /b 0

:error
echo.
echo Setup failed. Check the internet connection and run setup.bat again.
pause
exit /b 1
