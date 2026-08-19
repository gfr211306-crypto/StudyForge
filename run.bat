@echo off
setlocal
cd /d "%~dp0"
set "PYTHONUTF8=1"

if exist ".venv\Scripts\python.exe" goto :start
echo StudyForge is not installed yet. Starting setup.bat...
call setup.bat
if errorlevel 1 exit /b 1

:start
if not defined STUDYFORGE_NO_BROWSER start "" /min powershell.exe -NoProfile -WindowStyle Hidden -Command "Start-Sleep -Seconds 3; Start-Process 'http://localhost:8501'"
".venv\Scripts\python.exe" -m streamlit run app.py --server.headless true --browser.gatherUsageStats false
