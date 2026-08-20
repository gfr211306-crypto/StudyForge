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

echo [1/4] Creating the virtual environment...
%PYTHON% -m venv .venv
if errorlevel 1 goto :error

echo [2/4] Updating pip...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 goto :error

echo [3/4] Installing StudyForge website packages...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 goto :error

echo [4/4] Installing the StudyForge CLI...
".venv\Scripts\python.exe" -m pip install --no-deps -e .
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
