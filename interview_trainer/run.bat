@echo off
REM Interview Trainer Agent — Flask launcher
REM Double-click this file to start the app.
REM API keys are loaded from .env by run.py (see .env.example).

set HF_HUB_DISABLE_SYMLINKS_WARNING=1

cd /d %~dp0

if not exist ".env" (
    echo WARNING: .env not found. Copy .env.example to .env and add your API keys.
    echo The app will still run, but AI features will use fallback responses.
    echo.
)

echo Starting Interview Trainer Agent (Flask)...
echo Open your browser at: http://localhost:5000
echo.

py run.py
