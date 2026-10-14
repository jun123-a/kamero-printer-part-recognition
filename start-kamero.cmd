@echo off
cd /d "%~dp0"
echo Open http://127.0.0.1:8000 in your browser.
".venv\Scripts\python.exe" -m uvicorn main:app --app-dir app --host 127.0.0.1 --port 8000
pause
