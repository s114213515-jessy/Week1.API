@echo off
setlocal
cd /d "%~dp0"

set "HOST=%~1"
if "%HOST%"=="" set "HOST=0.0.0.0"

set "PORT=%~2"
if "%PORT%"=="" set "PORT=7777"

if exist "%~dp0venv\Scripts\python.exe" (
    "%~dp0venv\Scripts\python.exe" -m uvicorn app.main:app --host %HOST% --port %PORT%
) else (
    python -m uvicorn app.main:app --host %HOST% --port %PORT%
)
